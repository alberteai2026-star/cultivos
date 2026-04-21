from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportExport(Base):
    __tablename__ = 'report_exports'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(60), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False, default='pdf')
    period_label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='generado')
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    signed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    signature_hash: Mapped[str | None] = mapped_column(String(160), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
