from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.nursery_service import NurseryService


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


class _Batch:
    def __init__(self):
        self.id = 12
        self.farm_id = 10
        self.plot_id = 1
        self.species = 'palma'
        self.variety = 'hibrida'
        self.sowing_date = datetime.utcnow()
        self.tray_count = 40
        self.status = 'activo'
        self.notes = None
        self.created_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.batch = _Batch()
        self.last_kwargs = None

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.batch]

    def get_by_id(self, batch_id: int):
        return self.batch if batch_id == self.batch.id else None

    def update_fields(self, batch, **kwargs):
        self.last_kwargs = kwargs
        if kwargs.get('tray_count') is not None:
            batch.tray_count = kwargs['tray_count']
        return batch


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
    service = NurseryService(db=None)
    repo = _Repo()
    service.nursery = repo
    service.relations = _RelationsAllow()

    response = service.list_for_user(
        _User(1),
        farm_id=10,
        plot_id=1,
        status_value='activo',
        species_search='pal',
        limit=25,
        offset=2,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'plot_id': 1,
        'status_value': 'activo',
        'species_search': 'pal',
        'limit': 25,
        'offset': 2,
    }


def test_get_for_user_denies_without_access():
    service = NurseryService(db=None)
    service.nursery = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), batch_id=12)

    assert exc.value.status_code == 403


def test_update_status_for_user_updates_and_audits():
    db = _DB()
    service = NurseryService(db=db)
    service.nursery = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_status_for_user(user=_User(1), batch_id=12, status_value='trasplantado')

    assert updated.status == 'trasplantado'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_status'
