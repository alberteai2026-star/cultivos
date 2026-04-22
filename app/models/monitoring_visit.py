from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MonitoringVisit(Base):
    __tablename__ = 'monitoring_visits'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    plot_id: Mapped[int] = mapped_column(ForeignKey('plots.id'), nullable=False, index=True)
    crop_cycle_id: Mapped[int | None] = mapped_column(ForeignKey('crop_cycles.id'), nullable=True, index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    bbch_stage: Mapped[str | None] = mapped_column(String(20), nullable=True)
    issue_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
