from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IrrigationEvent(Base):
    __tablename__ = 'irrigation_events'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    plot_id: Mapped[int] = mapped_column(ForeignKey('plots.id'), nullable=False, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    applied_mm: Mapped[float | None] = mapped_column(nullable=True)
    cost: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default='programado')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
