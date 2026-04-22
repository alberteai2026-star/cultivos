from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.phytosanitary_service import PhytosanitaryService


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


class _Record:
    def __init__(self):
        self.id = 9
        self.farm_id = 10
        self.plot_id = 2
        self.crop_cycle_id = None
        self.detected_issue = 'hongo'
        self.severity = 'media'
        self.action_taken = 'aplicar fungicida'
        self.observed_at = datetime.utcnow()
        self.created_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.record = _Record()
        self.last_kwargs = None

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.record]

    def get_by_id(self, record_id: int):
        return self.record if record_id == self.record.id else None

    def update_fields(self, record, **kwargs):
        self.last_kwargs = kwargs
        if kwargs.get('severity') is not None:
            record.severity = kwargs['severity']
        return record


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


def test_list_for_user_forwards_filters_and_pagination():
    service = PhytosanitaryService(db=None)
    repo = _Repo()
    service.phytosanitary = repo
    service.relations = _RelationsAllow()

    response = service.list_for_user(
        _User(1),
        farm_id=10,
        plot_id=2,
        severity='media',
        issue_search='hon',
        limit=30,
        offset=1,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'plot_id': 2,
        'severity': 'media',
        'issue_search': 'hon',
        'limit': 30,
        'offset': 1,
    }


def test_get_for_user_denies_without_access():
    service = PhytosanitaryService(db=None)
    service.phytosanitary = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), record_id=9)

    assert exc.value.status_code == 403


def test_update_for_user_updates_and_audits():
    db = _DB()
    service = PhytosanitaryService(db=db)
    service.phytosanitary = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_for_user(
        user=_User(1),
        record_id=9,
        detected_issue=None,
        severity='alta',
        action_taken=None,
        observed_at=None,
    )

    assert updated.severity == 'alta'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update'
