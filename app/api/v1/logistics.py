from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.logistics import ShipmentCreateRequest, ShipmentOut
from app.services.logistics_service import LogisticsService

router = APIRouter()


@router.get('/shipments', response_model=list[ShipmentOut])
def list_shipments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LogisticsService(db).list_for_user(user)


@router.post('/shipments', response_model=ShipmentOut, status_code=201)
def create_shipment(payload: ShipmentCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LogisticsService(db).create_for_user(user=user, farm_id=payload.farm_id, invoice_id=payload.invoice_id, destination_name=payload.destination_name, transport_type=payload.transport_type, driver_name=payload.driver_name, vehicle_plate=payload.vehicle_plate, departure_at=payload.departure_at, arrival_at=payload.arrival_at, status_value=payload.status, freight_cost=payload.freight_cost, notes=payload.notes)
