from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherObservation(Base):
    __tablename__ = 'weather_observations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    temperature_c: Mapped[float | None] = mapped_column(nullable=True)
    humidity_pct: Mapped[float | None] = mapped_column(nullable=True)
    rainfall_mm: Mapped[float | None] = mapped_column(nullable=True)
    wind_kmh: Mapped[float | None] = mapped_column(nullable=True)
    source: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
