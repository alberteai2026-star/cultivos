from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PhytosanitaryRecord(Base):
    __tablename__ = 'phytosanitary_records'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    plot_id: Mapped[int] = mapped_column(ForeignKey('plots.id'), nullable=False, index=True)
    crop_cycle_id: Mapped[int | None] = mapped_column(ForeignKey('crop_cycles.id'), nullable=True, index=True)
    detected_issue: Mapped[str] = mapped_column(String(150), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default='media')
    action_taken: Mapped[str] = mapped_column(Text, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
