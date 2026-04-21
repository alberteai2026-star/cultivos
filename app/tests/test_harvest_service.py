from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.services.harvest_service import HarvestService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _Plot:
    def __init__(self, farm_id: int):
        self.farm_id = farm_id


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


class _PlotsRepo:
    def __init__(self, plot=None):
        self.plot = plot

    def get_by_id(self, plot_id: int):
        return self.plot


class _Harvest:
    def __init__(self, harvest_id: int, farm_id: int):
        self.id = harvest_id
        self.farm_id = farm_id
        self.quantity = 100
        self.unit = 'kg'
        self.quality_grade = 'A'


class _HarvestRepo:
    def __init__(self):
        self.last_args = None
        self.harvest = _Harvest(harvest_id=5, farm_id=10)

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.harvest]

    def get_by_id(self, harvest_id: int):
        return self.harvest if harvest_id == self.harvest.id else None

    def update_fields(self, harvest, **kwargs):
        self.last_args = kwargs
        for key, value in kwargs.items():
            if value is not None:
                setattr(harvest, key, value)
        return harvest


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
    service = HarvestService(db=None)
    harvests = _HarvestRepo()
    service.harvests = harvests
    service.relations = _RelationsAllow()
    service.plots = _PlotsRepo(plot=_Plot(farm_id=10))

    start = datetime.utcnow() - timedelta(days=10)
    end = datetime.utcnow()
    payload = service.list_for_user(
        _User(1),
        farm_id=10,
        plot_id=33,
        crop_cycle_id=44,
        harvested_from=start,
        harvested_to=end,
        limit=50,
        offset=5,
    )

    assert payload.total == 1
    assert len(payload.items) == 1
    assert harvests.last_args == {
        'farm_ids': [10, 20],
        'farm_id': 10,
        'plot_id': 33,
        'crop_cycle_id': 44,
        'harvested_from': start,
        'harvested_to': end,
        'limit': 50,
        'offset': 5,
    }


def test_list_for_user_rejects_invalid_date_range():
    service = HarvestService(db=None)
    service.harvests = _HarvestRepo()
    service.relations = _RelationsAllow()
    service.plots = _PlotsRepo(plot=_Plot(farm_id=10))

    start = datetime.utcnow()
    end = start - timedelta(days=1)

    with pytest.raises(HTTPException) as exc:
        service.list_for_user(_User(1), harvested_from=start, harvested_to=end)

    assert exc.value.status_code == 422


def test_get_for_user_denies_when_user_has_no_access():
    service = HarvestService(db=None)
    service.harvests = _HarvestRepo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), harvest_id=5)

    assert exc.value.status_code == 403


def test_update_for_user_updates_record_and_writes_audit():
    db = _DB()
    service = HarvestService(db=db)
    service.harvests = _HarvestRepo()
    service.relations = _RelationsAllow()
    service.audit = _AuditRepo()

    updated = service.update_for_user(
        user=_User(1),
        harvest_id=5,
        harvested_at=None,
        quantity=150,
        unit='qq',
        quality_grade='B',
        destination='Bodega central',
    )

    assert updated.quantity == 150
    assert updated.unit == 'qq'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update'
