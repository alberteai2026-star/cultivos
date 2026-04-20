from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LogisticsShipment(Base):
    __tablename__ = 'logistics_shipments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey('invoices.id'), nullable=True, index=True)
    destination_name: Mapped[str] = mapped_column(String(150), nullable=False)
    transport_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    driver_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    vehicle_plate: Mapped[str | None] = mapped_column(String(30), nullable=True)
    departure_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    arrival_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pendiente')
    freight_cost: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
