from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportTemplate(Base):
    __tablename__ = 'report_templates'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(nullable=False, index=True)
    template_name: Mapped[str] = mapped_column(String(120), nullable=False)
    report_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(20), nullable=False, default='pdf')
    filters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
