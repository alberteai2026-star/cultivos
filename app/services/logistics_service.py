from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.logistics_repository import LogisticsRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class LogisticsService:
    def __init__(self, db: Session):
        self.db = db
        self.logistics = LogisticsRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.logistics.list_shipments_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, farm_id: int, invoice_id: int | None, destination_name: str, transport_type: str | None, driver_name: str | None, vehicle_plate: str | None, departure_at: datetime, arrival_at: datetime | None, status_value: str, freight_cost: float | None, notes: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        shipment = self.logistics.create_shipment(farm_id=farm_id, invoice_id=invoice_id, destination_name=destination_name, transport_type=transport_type, driver_name=driver_name, vehicle_plate=vehicle_plate, departure_at=departure_at, arrival_at=arrival_at, status=status_value, freight_cost=freight_cost, notes=notes)
        self.audit.add(module='logistics', action='create_shipment', user_id=user.id, farm_id=farm_id, record_id=str(shipment.id))
        self.db.commit(); self.db.refresh(shipment)
        return shipment
