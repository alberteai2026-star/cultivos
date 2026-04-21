from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MapFeature(Base):
    __tablename__ = 'map_features'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey('farms.id'), nullable=False, index=True)
    plot_id: Mapped[int | None] = mapped_column(ForeignKey('plots.id'), nullable=True, index=True)
    feature_type: Mapped[str] = mapped_column(String(40), nullable=False, default='polygon')
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    geometry_geojson: Mapped[str] = mapped_column(Text, nullable=False)
    properties_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
