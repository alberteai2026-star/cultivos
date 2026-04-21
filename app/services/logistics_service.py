from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.logistics_repository import LogisticsRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.logistics import ShipmentListResponse, ShipmentTrackingPointListResponse


class LogisticsService:
    def __init__(self, db: Session):
        self.db = db
        self.logistics = LogisticsRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        status_value: str | None = None,
        destination_search: str | None = None,
        departure_from: datetime | None = None,
        departure_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ShipmentListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.logistics.list_shipments_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            status_value=status_value,
            destination_search=destination_search,
            departure_from=departure_from,
            departure_to=departure_to,
            limit=limit,
            offset=offset,
        )
        return ShipmentListResponse(total=total, items=items)

    def create_for_user(self, *, user: User, farm_id: int, invoice_id: int | None, destination_name: str, transport_type: str | None, driver_name: str | None, vehicle_plate: str | None, departure_at: datetime, arrival_at: datetime | None, status_value: str, freight_cost: float | None, notes: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        shipment = self.logistics.create_shipment(farm_id=farm_id, invoice_id=invoice_id, destination_name=destination_name, transport_type=transport_type, driver_name=driver_name, vehicle_plate=vehicle_plate, departure_at=departure_at, arrival_at=arrival_at, status=status_value, freight_cost=freight_cost, notes=notes)
        self.audit.add(module='logistics', action='create_shipment', user_id=user.id, farm_id=farm_id, record_id=str(shipment.id))
        self.db.commit(); self.db.refresh(shipment)
        return shipment

    def get_for_user(self, *, user: User, shipment_id: int):
        shipment = self.logistics.get_shipment_by_id(shipment_id)
        if not shipment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Despacho no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=shipment.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return shipment

    def update_for_user(
        self,
        *,
        user: User,
        shipment_id: int,
        destination_name: str | None,
        transport_type: str | None,
        driver_name: str | None,
        vehicle_plate: str | None,
        departure_at: datetime | None,
        arrival_at: datetime | None,
        freight_cost: float | None,
        notes: str | None,
    ):
        shipment = self.get_for_user(user=user, shipment_id=shipment_id)
        updated = self.logistics.update_shipment_fields(
            shipment,
            destination_name=destination_name,
            transport_type=transport_type,
            driver_name=driver_name,
            vehicle_plate=vehicle_plate,
            departure_at=departure_at,
            arrival_at=arrival_at,
            freight_cost=freight_cost,
            notes=notes,
        )
        self.audit.add(module='logistics', action='update_shipment', user_id=user.id, farm_id=shipment.farm_id, record_id=str(shipment.id))
        self.db.commit(); self.db.refresh(updated)
        return updated

    def update_status_for_user(self, *, user: User, shipment_id: int, status_value: str):
        shipment = self.get_for_user(user=user, shipment_id=shipment_id)
        shipment.status = status_value
        self.audit.add(module='logistics', action='update_status', user_id=user.id, farm_id=shipment.farm_id, record_id=str(shipment.id))
        self.db.commit(); self.db.refresh(shipment)
        return shipment

    def add_tracking_point_for_user(
        self,
        *,
        user: User,
        shipment_id: int,
        latitude: float,
        longitude: float,
        speed_kmh: float | None,
        heading_deg: float | None,
        recorded_at: datetime,
        source: str,
        notes: str | None,
    ):
        shipment = self.get_for_user(user=user, shipment_id=shipment_id)
        point = self.logistics.create_tracking_point(
            shipment_id=shipment.id,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            heading_deg=heading_deg,
            recorded_at=recorded_at,
            source=source,
            notes=notes,
        )
        self.audit.add(module='logistics', action='add_tracking_point', user_id=user.id, farm_id=shipment.farm_id, record_id=str(point.id))
        self.db.commit(); self.db.refresh(point)
        return point

    def list_tracking_for_user(
        self,
        *,
        user: User,
        shipment_id: int,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> ShipmentTrackingPointListResponse:
        if recorded_from is not None and recorded_to is not None and recorded_from > recorded_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Rango de fechas inválido')
        shipment = self.get_for_user(user=user, shipment_id=shipment_id)
        total, items = self.logistics.list_tracking_points_by_shipment_id(
            shipment.id,
            recorded_from=recorded_from,
            recorded_to=recorded_to,
            limit=limit,
            offset=offset,
        )
        return ShipmentTrackingPointListResponse(total=total, items=items)
