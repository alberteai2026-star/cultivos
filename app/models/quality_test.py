from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QualityTest(Base):
    __tablename__ = 'quality_tests'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    plot_id: Mapped[int | None] = mapped_column(ForeignKey('plots.id'), nullable=True, index=True)
    harvest_id: Mapped[int | None] = mapped_column(ForeignKey('harvests.id'), nullable=True, index=True)
    test_type: Mapped[str] = mapped_column(String(80), nullable=False)
    result_value: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='ok')
    tested_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
