from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Worker(Base):
    __tablename__ = 'workers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    document_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    role_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    daily_rate: Mapped[float | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
