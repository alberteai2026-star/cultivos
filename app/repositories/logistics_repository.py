from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.logistics_shipment import LogisticsShipment
from app.models.logistics_tracking_point import LogisticsTrackingPoint


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

    def list_shipments_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        status_value: str | None = None,
        destination_search: str | None = None,
        departure_from: datetime | None = None,
        departure_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[LogisticsShipment]]:
        if not farm_ids:
            return 0, []
        q = select(LogisticsShipment).where(LogisticsShipment.farm_id.in_(farm_ids))
        count_q = select(func.count(LogisticsShipment.id)).where(LogisticsShipment.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(LogisticsShipment.farm_id == farm_id)
            count_q = count_q.where(LogisticsShipment.farm_id == farm_id)
        if status_value is not None:
            q = q.where(LogisticsShipment.status == status_value)
            count_q = count_q.where(LogisticsShipment.status == status_value)
        if destination_search:
            pattern = f"%{destination_search.strip()}%"
            q = q.where(LogisticsShipment.destination_name.ilike(pattern))
            count_q = count_q.where(LogisticsShipment.destination_name.ilike(pattern))
        if departure_from is not None:
            q = q.where(LogisticsShipment.departure_at >= departure_from)
            count_q = count_q.where(LogisticsShipment.departure_at >= departure_from)
        if departure_to is not None:
            q = q.where(LogisticsShipment.departure_at <= departure_to)
            count_q = count_q.where(LogisticsShipment.departure_at <= departure_to)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(LogisticsShipment.departure_at.desc(), LogisticsShipment.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_shipment_by_id(self, shipment_id: int) -> LogisticsShipment | None:
        return self.db.get(LogisticsShipment, shipment_id)

    def update_shipment_fields(
        self,
        shipment: LogisticsShipment,
        *,
        destination_name: str | None,
        transport_type: str | None,
        driver_name: str | None,
        vehicle_plate: str | None,
        departure_at: datetime | None,
        arrival_at: datetime | None,
        freight_cost: float | None,
        notes: str | None,
    ) -> LogisticsShipment:
        if destination_name is not None:
            shipment.destination_name = destination_name
        shipment.transport_type = transport_type
        shipment.driver_name = driver_name
        shipment.vehicle_plate = vehicle_plate
        if departure_at is not None:
            shipment.departure_at = departure_at
        shipment.arrival_at = arrival_at
        shipment.freight_cost = freight_cost
        shipment.notes = notes
        self.db.flush()
        return shipment

    def create_tracking_point(
        self,
        *,
        shipment_id: int,
        latitude: float,
        longitude: float,
        speed_kmh: float | None,
        heading_deg: float | None,
        recorded_at: datetime,
        source: str,
        notes: str | None,
    ) -> LogisticsTrackingPoint:
        point = LogisticsTrackingPoint(
            shipment_id=shipment_id,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            heading_deg=heading_deg,
            recorded_at=recorded_at,
            source=source,
            notes=notes,
        )
        self.db.add(point)
        self.db.flush()
        return point

    def list_tracking_points_by_shipment_id(
        self,
        shipment_id: int,
        *,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[int, list[LogisticsTrackingPoint]]:
        q = select(LogisticsTrackingPoint).where(LogisticsTrackingPoint.shipment_id == shipment_id)
        count_q = select(func.count(LogisticsTrackingPoint.id)).where(LogisticsTrackingPoint.shipment_id == shipment_id)
        if recorded_from is not None:
            q = q.where(LogisticsTrackingPoint.recorded_at >= recorded_from)
            count_q = count_q.where(LogisticsTrackingPoint.recorded_at >= recorded_from)
        if recorded_to is not None:
            q = q.where(LogisticsTrackingPoint.recorded_at <= recorded_to)
            count_q = count_q.where(LogisticsTrackingPoint.recorded_at <= recorded_to)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(LogisticsTrackingPoint.recorded_at.desc(), LogisticsTrackingPoint.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())
