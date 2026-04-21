from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.irrigation_service import IrrigationService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _RelationsAllow:
    def list_farm_ids_by_user(self, user_id: int):
        return [10]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return farm_id == 10


class _RelationsDeny:
    def list_farm_ids_by_user(self, user_id: int):
        return []

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return False


class _Event:
    def __init__(self):
        self.id = 4
        self.farm_id = 10
        self.status = 'programado'


class _Repo:
    def __init__(self):
        self.event = _Event()
        self.last_args = None

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.event]

    def get_by_id(self, event_id: int):
        return self.event if event_id == self.event.id else None

    def update_fields(self, event, **kwargs):
        self.last_args = kwargs
        return event


class _Audit:
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


def test_list_for_user_forwards_filters():
    service = IrrigationService(db=None)
    repo = _Repo()
    service.irrigation = repo
    service.relations = _RelationsAllow()

    start = datetime.utcnow()
    payload = service.list_for_user(_User(1), farm_id=10, plot_id=3, status_value='programado', scheduled_from=start, limit=20, offset=2)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args['farm_ids'] == [10]
    assert repo.last_args['plot_id'] == 3


def test_get_for_user_denies_without_access():
    service = IrrigationService(db=None)
    service.irrigation = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), event_id=4)

    assert exc.value.status_code == 403


def test_update_status_rejects_invalid_transition():
    service = IrrigationService(db=None)
    service.irrigation = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.update_status_for_user(user=_User(1), event_id=4, status_value='cerrado')

    assert exc.value.status_code == 409


def test_update_status_updates_and_audits():
    db = _DB()
    service = IrrigationService(db=db)
    service.irrigation = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_status_for_user(user=_User(1), event_id=4, status_value='ejecutado')

    assert updated.status == 'ejecutado'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
