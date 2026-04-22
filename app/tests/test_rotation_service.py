import pytest
from fastapi import HTTPException

from app.services.rotation_service import RotationService


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


class _Plan:
    def __init__(self):
        self.id = 6
        self.farm_id = 10
        self.status = 'propuesto'


class _Repo:
    def __init__(self):
        self.plan = _Plan()
        self.last_args = None

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.plan]

    def get_by_id(self, plan_id: int):
        return self.plan if plan_id == self.plan.id else None

    def update_fields(self, plan, **kwargs):
        self.last_args = kwargs
        return plan


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
    service = RotationService(db=None)
    repo = _Repo()
    service.rotation = repo
    service.relations = _RelationsAllow()

    payload = service.list_for_user(_User(1), farm_id=10, plot_id=4, status_value='propuesto', search='maiz', limit=20, offset=1)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args == {
        'farm_ids': [10],
        'farm_id': 10,
        'plot_id': 4,
        'status_value': 'propuesto',
        'search': 'maiz',
        'limit': 20,
        'offset': 1,
    }


def test_get_for_user_denies_without_access():
    service = RotationService(db=None)
    service.rotation = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), plan_id=6)

    assert exc.value.status_code == 403


def test_update_status_for_user_updates_and_audits():
    db = _DB()
    service = RotationService(db=db)
    service.rotation = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_status_for_user(user=_User(1), plan_id=6, status_value='aprobado')

    assert updated.status == 'aprobado'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_status'
