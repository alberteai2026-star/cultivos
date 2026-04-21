from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IoTValveCommand(Base):
    __tablename__ = 'iot_valve_commands'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey('iot_devices.id'), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='queued')
    source: Mapped[str] = mapped_column(String(20), nullable=False, default='manual')
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
