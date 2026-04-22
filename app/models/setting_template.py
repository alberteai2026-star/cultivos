from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SettingTemplate(Base):
    __tablename__ = 'setting_templates'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crop_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    setting_key: Mapped[str] = mapped_column(String(80), nullable=False)
    default_value: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
