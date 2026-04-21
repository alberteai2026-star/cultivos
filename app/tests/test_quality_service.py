from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.quality_service import QualityService


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


class _Test:
    def __init__(self):
        self.id = 3
        self.farm_id = 10
        self.plot_id = 2
        self.harvest_id = None
        self.test_type = 'brix'
        self.result_value = '18'
        self.status = 'ok'
        self.tested_at = datetime.utcnow()
        self.created_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.test = _Test()
        self.last_kwargs = None

    def list_tests_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.test]

    def get_test_by_id(self, test_id: int):
        return self.test if test_id == self.test.id else None

    def update_test_fields(self, test, **kwargs):
        self.last_kwargs = kwargs
        if kwargs.get('status') is not None:
            test.status = kwargs['status']
        return test


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


def test_list_tests_for_user_forwards_filters():
    service = QualityService(db=None)
    repo = _Repo()
    service.quality = repo
    service.relations = _RelationsAllow()

    response = service.list_tests_for_user(
        _User(1),
        farm_id=10,
        plot_id=2,
        status_value='ok',
        test_type='brix',
        limit=20,
        offset=2,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'plot_id': 2,
        'status_value': 'ok',
        'test_type': 'brix',
        'limit': 20,
        'offset': 2,
    }


def test_get_test_for_user_denies_without_access():
    service = QualityService(db=None)
    service.quality = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_test_for_user(user=_User(1), test_id=3)

    assert exc.value.status_code == 403


def test_update_test_for_user_updates_and_audits():
    db = _DB()
    service = QualityService(db=db)
    service.quality = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_test_for_user(user=_User(1), test_id=3, result_value=None, status_value='observado', tested_at=None)

    assert updated.status == 'observado'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_test'
