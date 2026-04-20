from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InputProduct(Base):
    __tablename__ = 'input_products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    ica_register: Mapped[str | None] = mapped_column(String(80), nullable=True)
    withholding_days: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
