import pytest
from fastapi import HTTPException

from app.services.machine_service import MachineService


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


class _Machine:
    def __init__(self):
        self.id = 9
        self.farm_id = 10
        self.status = 'disponible'


class _Repo:
    def __init__(self):
        self.machine = _Machine()
        self.last_args = None

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.machine]

    def get_by_id(self, machine_id: int):
        return self.machine if machine_id == self.machine.id else None

    def update_fields(self, machine, **kwargs):
        self.last_args = kwargs
        return machine


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
    service = MachineService(db=None)
    repo = _Repo()
    service.machines = repo
    service.relations = _RelationsAllow()

    payload = service.list_for_user(_User(1), farm_id=10, status_value='disponible', search='tractor', limit=25, offset=2)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args == {
        'farm_ids': [10],
        'farm_id': 10,
        'status_value': 'disponible',
        'search': 'tractor',
        'limit': 25,
        'offset': 2,
    }


def test_get_for_user_denies_without_access():
    service = MachineService(db=None)
    service.machines = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), machine_id=9)

    assert exc.value.status_code == 403


def test_update_status_for_user_updates_and_audits():
    db = _DB()
    service = MachineService(db=db)
    service.machines = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_status_for_user(user=_User(1), machine_id=9, status_value='mantenimiento')

    assert updated.status == 'mantenimiento'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_status'
