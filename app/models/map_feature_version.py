from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MapFeatureVersion(Base):
    __tablename__ = 'map_feature_versions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    feature_id: Mapped[int] = mapped_column(ForeignKey('map_features.id'), nullable=False, index=True)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    geometry_geojson: Mapped[str] = mapped_column(Text, nullable=False)
    properties_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
