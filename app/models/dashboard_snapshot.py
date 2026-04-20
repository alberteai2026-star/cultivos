from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DashboardSnapshot(Base):
    __tablename__ = 'dashboard_snapshots'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    active_cycles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pending_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    inventory_low_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    income_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    cost_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
