from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.services.weather_service import WeatherService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _RelationsAllow:
    def list_farm_ids_by_user(self, user_id: int):
        return [10, 20]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return farm_id in {10, 20}


class _RelationsDeny:
    def list_farm_ids_by_user(self, user_id: int):
        return []

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return False


class _Observation:
    def __init__(self, obs_id: int, farm_id: int):
        self.id = obs_id
        self.farm_id = farm_id
        self.source = 'iot'


class _WeatherRepo:
    def __init__(self):
        self.last_args = None
        self.observation = _Observation(obs_id=11, farm_id=10)

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.observation]

    def get_by_id(self, observation_id: int):
        return self.observation if observation_id == self.observation.id else None

    def update_fields(self, observation, **kwargs):
        self.last_args = kwargs
        for key, value in kwargs.items():
            setattr(observation, key, value)
        return observation


class _AuditRepo:
    def __init__(self):
        self.entries = []

    def add(self, **kwargs):
        self.entries.append(kwargs)


class _DB:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1

    def refresh(self, _obj):
        return None


def test_list_for_user_forwards_filters_and_pagination():
    service = WeatherService(db=None)
    repo = _WeatherRepo()
    service.weather = repo
    service.relations = _RelationsAllow()

    start = datetime.utcnow() - timedelta(days=5)
    end = datetime.utcnow()

    payload = service.list_for_user(
        _User(1),
        farm_id=10,
        source='station',
        observed_from=start,
        observed_to=end,
        limit=30,
        offset=4,
    )

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args == {
        'farm_ids': [10, 20],
        'farm_id': 10,
        'source': 'station',
        'observed_from': start,
        'observed_to': end,
        'limit': 30,
        'offset': 4,
    }


def test_list_for_user_rejects_invalid_date_range():
    service = WeatherService(db=None)
    service.weather = _WeatherRepo()
    service.relations = _RelationsAllow()

    start = datetime.utcnow()
    end = start - timedelta(days=1)

    with pytest.raises(HTTPException) as exc:
        service.list_for_user(_User(1), observed_from=start, observed_to=end)

    assert exc.value.status_code == 422


def test_get_for_user_denies_when_user_has_no_farm_access():
    service = WeatherService(db=None)
    service.weather = _WeatherRepo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), observation_id=11)

    assert exc.value.status_code == 403


def test_update_for_user_updates_and_audits_observation():
    db = _DB()
    service = WeatherService(db=db)
    service.weather = _WeatherRepo()
    service.relations = _RelationsAllow()
    service.audit = _AuditRepo()

    updated = service.update_for_user(
        user=_User(1),
        observation_id=11,
        observed_at=None,
        temperature_c=21.5,
        humidity_pct=73.0,
        rainfall_mm=2.1,
        wind_kmh=8.2,
        source='manual',
    )

    assert updated.source == 'manual'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_observation'
