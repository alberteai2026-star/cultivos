from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.map_feature import MapFeature
from app.models.map_feature_version import MapFeatureVersion


class GISRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_feature(self, *, farm_id: int, plot_id: int | None, feature_type: str, name: str, geometry_geojson: str, properties_json: str | None) -> MapFeature:
        feature = MapFeature(farm_id=farm_id, plot_id=plot_id, feature_type=feature_type, name=name, geometry_geojson=geometry_geojson, properties_json=properties_json)
        self.db.add(feature)
        self.db.flush()
        return feature

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        feature_type: str | None = None,
        name_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[MapFeature]]:
        if not farm_ids:
            return 0, []
        q = select(MapFeature).where(MapFeature.farm_id.in_(farm_ids))
        count_q = select(func.count(MapFeature.id)).where(MapFeature.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(MapFeature.farm_id == farm_id)
            count_q = count_q.where(MapFeature.farm_id == farm_id)
        if plot_id is not None:
            q = q.where(MapFeature.plot_id == plot_id)
            count_q = count_q.where(MapFeature.plot_id == plot_id)
        if feature_type is not None:
            q = q.where(MapFeature.feature_type == feature_type)
            count_q = count_q.where(MapFeature.feature_type == feature_type)
        if name_search is not None:
            pattern = f'%{name_search}%'
            q = q.where(MapFeature.name.ilike(pattern))
            count_q = count_q.where(MapFeature.name.ilike(pattern))
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(MapFeature.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, feature_id: int) -> MapFeature | None:
        return self.db.get(MapFeature, feature_id)

    def update_fields(
        self,
        feature: MapFeature,
        *,
        name: str | None = None,
        geometry_geojson: str | None = None,
        properties_json: str | None = None,
    ) -> MapFeature:
        if name is not None:
            feature.name = name
        if geometry_geojson is not None:
            feature.geometry_geojson = geometry_geojson
        if properties_json is not None:
            feature.properties_json = properties_json
        self.db.add(feature)
        return feature

    def create_version(self, *, feature: MapFeature, changed_by_user_id: int | None) -> MapFeatureVersion:
        next_version = int(
            self.db.scalar(select(func.coalesce(func.max(MapFeatureVersion.version_no), 0)).where(MapFeatureVersion.feature_id == feature.id))
            or 0
        ) + 1
        version = MapFeatureVersion(
            feature_id=feature.id,
            version_no=next_version,
            name=feature.name,
            geometry_geojson=feature.geometry_geojson,
            properties_json=feature.properties_json,
            changed_by_user_id=changed_by_user_id,
        )
        self.db.add(version)
        self.db.flush()
        return version

    def list_versions(self, feature_id: int, *, limit: int = 100, offset: int = 0) -> tuple[int, list[MapFeatureVersion]]:
        count_q = select(func.count(MapFeatureVersion.id)).where(MapFeatureVersion.feature_id == feature_id)
        total = int(self.db.scalar(count_q) or 0)
        q = (
            select(MapFeatureVersion)
            .where(MapFeatureVersion.feature_id == feature_id)
            .order_by(MapFeatureVersion.version_no.desc(), MapFeatureVersion.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return total, list(self.db.scalars(q).all())
