from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IoTRule(Base):
    __tablename__ = 'iot_rules'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey('iot_devices.id'), nullable=True, index=True)
    metric: Mapped[str] = mapped_column(String(60), nullable=False)
    operator: Mapped[str] = mapped_column(String(5), nullable=False)
    threshold_value: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default='medium')
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
