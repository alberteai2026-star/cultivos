from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.logistics_service import LogisticsService


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


class _Shipment:
    def __init__(self):
        self.id = 4
        self.farm_id = 10
        self.invoice_id = None
        self.destination_name = 'Bodega central'
        self.transport_type = 'camion'
        self.driver_name = 'Carlos'
        self.vehicle_plate = 'ABC123'
        self.departure_at = datetime.utcnow()
        self.arrival_at = None
        self.status = 'pendiente'
        self.freight_cost = 100.0
        self.notes = None
        self.created_at = datetime.utcnow()


class _TrackingPoint:
    def __init__(self):
        self.id = 22
        self.shipment_id = 4
        self.latitude = 4.1234
        self.longitude = -73.1234
        self.speed_kmh = 45.0
        self.heading_deg = 180.0
        self.recorded_at = datetime.utcnow()
        self.source = 'gps'
        self.notes = None
        self.created_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.shipment = _Shipment()
        self.point = _TrackingPoint()
        self.last_args = None

    def list_shipments_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.shipment]

    def get_shipment_by_id(self, shipment_id: int):
        return self.shipment if shipment_id == self.shipment.id else None

    def update_shipment_fields(self, shipment, **kwargs):
        self.last_args = kwargs
        return shipment

    def create_tracking_point(self, **kwargs):
        self.last_args = kwargs
        return self.point

    def list_tracking_points_by_shipment_id(self, shipment_id: int, **kwargs):
        self.last_args = {'shipment_id': shipment_id, **kwargs}
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
    service = LogisticsService(db=None)
    repo = _Repo()
    service.logistics = repo
    service.relations = _RelationsAllow()

    start = datetime.utcnow()
    payload = service.list_for_user(_User(1), farm_id=10, status_value='pendiente', destination_search='bodega', departure_from=start, limit=20, offset=4)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args['farm_ids'] == [10]
    assert repo.last_args['status_value'] == 'pendiente'


def test_get_for_user_denies_without_access():
    service = LogisticsService(db=None)
    service.logistics = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), shipment_id=4)

    assert exc.value.status_code == 403


def test_update_status_for_user_updates_and_audits():
    db = _DB()
    service = LogisticsService(db=db)
    service.logistics = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_status_for_user(user=_User(1), shipment_id=4, status_value='en_transito')

    assert updated.status == 'en_transito'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_status'


def test_add_tracking_point_for_user_creates_and_audits():
    db = _DB()
    service = LogisticsService(db=db)
    repo = _Repo()
    service.logistics = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    point = service.add_tracking_point_for_user(
        user=_User(1),
        shipment_id=4,
        latitude=4.1,
        longitude=-73.1,
        speed_kmh=35.0,
        heading_deg=90.0,
        recorded_at=datetime.utcnow(),
        source='gps',
        notes='ok',
    )

    assert point.id == 22
    assert db.commits == 1
    assert service.audit.entries[0]['action'] == 'add_tracking_point'


def test_list_tracking_for_user_validates_date_range():
    service = LogisticsService(db=None)
    service.logistics = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.list_tracking_for_user(
            user=_User(1),
            shipment_id=4,
            recorded_from=datetime(2026, 2, 1),
            recorded_to=datetime(2026, 1, 1),
        )

    assert exc.value.status_code == 422
