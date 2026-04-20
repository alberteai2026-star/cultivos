from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.logistics_shipment import LogisticsShipment


class LogisticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_shipment(self, *, farm_id: int, invoice_id: int | None, destination_name: str, transport_type: str | None, driver_name: str | None, vehicle_plate: str | None, departure_at: datetime, arrival_at: datetime | None, status: str, freight_cost: float | None, notes: str | None) -> LogisticsShipment:
        shipment = LogisticsShipment(
            farm_id=farm_id,
            invoice_id=invoice_id,
            destination_name=destination_name,
            transport_type=transport_type,
            driver_name=driver_name,
            vehicle_plate=vehicle_plate,
            departure_at=departure_at,
            arrival_at=arrival_at,
            status=status,
            freight_cost=freight_cost,
            notes=notes,
        )
        self.db.add(shipment)
        self.db.flush()
        return shipment

    def list_shipments_by_farm_ids(self, farm_ids: list[int]) -> list[LogisticsShipment]:
        if not farm_ids:
            return []
        q = select(LogisticsShipment).where(LogisticsShipment.farm_id.in_(farm_ids)).order_by(LogisticsShipment.departure_at.desc(), LogisticsShipment.id.desc())
        return list(self.db.scalars(q).all())
