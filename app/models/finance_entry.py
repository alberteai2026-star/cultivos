from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FinanceEntry(Base):
    __tablename__ = 'finance_entries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    plot_id: Mapped[int | None] = mapped_column(ForeignKey('plots.id'), nullable=True, index=True)
    crop_cycle_id: Mapped[int | None] = mapped_column(ForeignKey('crop_cycles.id'), nullable=True, index=True)
    entry_type: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    happened_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
