from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Invoice(Base):
    __tablename__ = 'invoices'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(60), nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pendiente')
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
