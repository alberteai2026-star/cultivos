from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.logistics import (
    ShipmentCreateRequest,
    ShipmentListResponse,
    ShipmentOut,
    ShipmentStatusUpdateRequest,
    ShipmentTrackingPointCreateRequest,
    ShipmentTrackingPointListResponse,
    ShipmentTrackingPointOut,
    ShipmentUpdateRequest,
)
from app.services.logistics_service import LogisticsService

router = APIRouter()


@router.get('/shipments', response_model=ShipmentListResponse)
def list_shipments(
    farm_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    destination_search: str | None = Query(default=None),
    departure_from: datetime | None = Query(default=None),
    departure_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return LogisticsService(db).list_for_user(
        user,
        farm_id=farm_id,
        status_value=status_value,
        destination_search=destination_search,
        departure_from=departure_from,
        departure_to=departure_to,
        limit=limit,
        offset=offset,
    )


@router.post('/shipments', response_model=ShipmentOut, status_code=201)
def create_shipment(payload: ShipmentCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LogisticsService(db).create_for_user(user=user, farm_id=payload.farm_id, invoice_id=payload.invoice_id, destination_name=payload.destination_name, transport_type=payload.transport_type, driver_name=payload.driver_name, vehicle_plate=payload.vehicle_plate, departure_at=payload.departure_at, arrival_at=payload.arrival_at, status_value=payload.status, freight_cost=payload.freight_cost, notes=payload.notes)


@router.get('/shipments/{shipment_id}', response_model=ShipmentOut)
def get_shipment(shipment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LogisticsService(db).get_for_user(user=user, shipment_id=shipment_id)


@router.patch('/shipments/{shipment_id}', response_model=ShipmentOut)
def update_shipment(shipment_id: int, payload: ShipmentUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LogisticsService(db).update_for_user(
        user=user,
        shipment_id=shipment_id,
        destination_name=payload.destination_name,
        transport_type=payload.transport_type,
        driver_name=payload.driver_name,
        vehicle_plate=payload.vehicle_plate,
        departure_at=payload.departure_at,
        arrival_at=payload.arrival_at,
        freight_cost=payload.freight_cost,
        notes=payload.notes,
    )


@router.patch('/shipments/{shipment_id}/status', response_model=ShipmentOut)
def update_shipment_status(shipment_id: int, payload: ShipmentStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LogisticsService(db).update_status_for_user(user=user, shipment_id=shipment_id, status_value=payload.status)


@router.post('/shipments/{shipment_id}/tracking', response_model=ShipmentTrackingPointOut, status_code=201)
def create_shipment_tracking_point(shipment_id: int, payload: ShipmentTrackingPointCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LogisticsService(db).add_tracking_point_for_user(
        user=user,
        shipment_id=shipment_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        speed_kmh=payload.speed_kmh,
        heading_deg=payload.heading_deg,
        recorded_at=payload.recorded_at,
        source=payload.source,
        notes=payload.notes,
    )


@router.get('/shipments/{shipment_id}/tracking', response_model=ShipmentTrackingPointListResponse)
def list_shipment_tracking_points(
    shipment_id: int,
    recorded_from: datetime | None = Query(default=None),
    recorded_to: datetime | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return LogisticsService(db).list_tracking_for_user(
        user=user,
        shipment_id=shipment_id,
        recorded_from=recorded_from,
        recorded_to=recorded_to,
        limit=limit,
        offset=offset,
    )
