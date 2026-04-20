from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.map_feature import MapFeature


class GISRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_feature(self, *, farm_id: int, plot_id: int | None, feature_type: str, name: str, geometry_geojson: str, properties_json: str | None) -> MapFeature:
        feature = MapFeature(farm_id=farm_id, plot_id=plot_id, feature_type=feature_type, name=name, geometry_geojson=geometry_geojson, properties_json=properties_json)
        self.db.add(feature)
        self.db.flush()
        return feature

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[MapFeature]:
        if not farm_ids:
            return []
        q = select(MapFeature).where(MapFeature.farm_id.in_(farm_ids)).order_by(MapFeature.id.desc())
        return list(self.db.scalars(q).all())
