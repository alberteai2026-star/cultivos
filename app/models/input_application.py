from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InputApplication(Base):
    __tablename__ = 'input_applications'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    plot_id: Mapped[int] = mapped_column(ForeignKey('plots.id'), nullable=False, index=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey('tasks.id'), nullable=True, index=True)
    input_product_id: Mapped[int] = mapped_column(ForeignKey('input_products.id'), nullable=False, index=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
