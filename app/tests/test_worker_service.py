from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.worker_service import WorkerService


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


class _Worker:
    def __init__(self):
        self.id = 7
        self.farm_id = 10
        self.full_name = 'Ana Perez'
        self.document_id = None
        self.role_name = 'Operaria'
        self.daily_rate = 20.0
        self.is_active = True
        self.created_at = datetime.utcnow()


class _TrackingPoint:
    def __init__(self):
        self.id = 13
        self.worker_id = 7
        self.latitude = 4.5
        self.longitude = -73.9
        self.speed_kmh = 3.0
        self.recorded_at = datetime.utcnow()
        self.source = 'mobile'
        self.notes = None
        self.created_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.worker = _Worker()
        self.point = _TrackingPoint()
        self.last_args = None

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.worker]

    def get_by_id(self, worker_id: int):
        return self.worker if worker_id == self.worker.id else None

    def update_fields(self, worker, **kwargs):
        self.last_args = kwargs
        return worker

    def create_tracking_point(self, **kwargs):
        self.last_args = kwargs
        return self.point

    def list_tracking_points_by_worker_id(self, worker_id: int, **kwargs):
        self.last_args = {'worker_id': worker_id, **kwargs}
        return 1, [self.point]


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
    service = WorkerService(db=None)
    repo = _Repo()
    service.workers = repo
    service.relations = _RelationsAllow()

    payload = service.list_for_user(_User(1), farm_id=10, is_active=True, search='ana', limit=30, offset=3)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args == {
        'farm_ids': [10],
        'farm_id': 10,
        'is_active': True,
        'search': 'ana',
        'limit': 30,
        'offset': 3,
    }


def test_get_for_user_denies_without_access():
    service = WorkerService(db=None)
    service.workers = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), worker_id=7)

    assert exc.value.status_code == 403


def test_update_status_for_user_updates_and_audits():
    db = _DB()
    service = WorkerService(db=db)
    service.workers = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_status_for_user(user=_User(1), worker_id=7, is_active=False)

    assert updated.is_active is False
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_status'


def test_add_tracking_point_for_user_creates_and_audits():
    db = _DB()
    service = WorkerService(db=db)
    repo = _Repo()
    service.workers = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    point = service.add_tracking_point_for_user(
        user=_User(1),
        worker_id=7,
        latitude=4.5,
        longitude=-73.9,
        speed_kmh=3.0,
        recorded_at=datetime.utcnow(),
        source='mobile',
        notes='turno mañana',
    )

    assert point.id == 13
    assert db.commits == 1
    assert service.audit.entries[0]['action'] == 'add_tracking_point'


def test_list_tracking_for_user_validates_date_range():
    service = WorkerService(db=None)
    service.workers = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.list_tracking_for_user(
            user=_User(1),
            worker_id=7,
            recorded_from=datetime(2026, 2, 1),
            recorded_to=datetime(2026, 1, 1),
        )

    assert exc.value.status_code == 422
