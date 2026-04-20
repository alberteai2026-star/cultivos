from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Harvest(Base):
    __tablename__ = 'harvests'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    plot_id: Mapped[int] = mapped_column(ForeignKey('plots.id'), nullable=False, index=True)
    crop_cycle_id: Mapped[int | None] = mapped_column(ForeignKey('crop_cycles.id'), nullable=True, index=True)
    harvested_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default='kg')
    quality_grade: Mapped[str | None] = mapped_column(String(30), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
