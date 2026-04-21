import pytest
from fastapi import HTTPException

from app.services.inventory_service import InventoryService


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


class _Item:
    def __init__(self):
        self.id = 3
        self.farm_id = 10


class _Move:
    def __init__(self):
        self.id = 8
        self.farm_id = 10
        self.reason = 'init'


class _InventoryRepo:
    def __init__(self):
        self.item = _Item()
        self.move = _Move()
        self.last_args = None

    def list_items_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.item]

    def list_movements_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.move]

    def get_item(self, item_id):
        return self.item if item_id == self.item.id else None

    def get_movement(self, movement_id):
        return self.move if movement_id == self.move.id else None

    def update_item_fields(self, item, **kwargs):
        self.last_args = kwargs
        return item

    def update_movement_reason(self, movement, **kwargs):
        self.last_args = kwargs
        movement.reason = kwargs.get('reason')
        return movement


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


def test_list_items_for_user_forwards_filters():
    service = InventoryService(db=None)
    repo = _InventoryRepo()
    service.inventory = repo
    service.relations = _RelationsAllow()

    payload = service.list_items_for_user(_User(1), farm_id=10, search='fer', limit=50, offset=5)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args == {'farm_ids': [10, 20], 'farm_id': 10, 'search': 'fer', 'limit': 50, 'offset': 5}


def test_list_movements_for_user_denies_forbidden_farm():
    service = InventoryService(db=None)
    service.inventory = _InventoryRepo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.list_movements_for_user(_User(1), farm_id=999)

    assert exc.value.status_code == 403


def test_get_item_for_user_denies_without_access():
    service = InventoryService(db=None)
    service.inventory = _InventoryRepo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_item_for_user(user=_User(1), item_id=3)

    assert exc.value.status_code == 403


def test_update_movement_for_user_updates_reason_and_audits():
    db = _DB()
    service = InventoryService(db=db)
    service.inventory = _InventoryRepo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_movement_for_user(user=_User(1), movement_id=8, reason='ajuste')

    assert updated.reason == 'ajuste'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_movement'
