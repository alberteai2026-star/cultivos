from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FarmSettingHistory(Base):
    __tablename__ = 'farm_setting_history'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    setting_id: Mapped[int] = mapped_column(ForeignKey('farm_settings.id'), nullable=False, index=True)
    changed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True, index=True)
    previous_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
