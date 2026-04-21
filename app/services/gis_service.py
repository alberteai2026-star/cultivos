from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.gis_repository import GISRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.gis import MapFeatureListResponse, MapFeatureVersionListResponse


class GISService:
    def __init__(self, db: Session):
        self.db = db
        self.gis = GISRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        feature_type: str | None = None,
        name_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> MapFeatureListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.gis.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            feature_type=feature_type,
            name_search=name_search,
            limit=limit,
            offset=offset,
        )
        return MapFeatureListResponse(total=total, items=items)

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int | None, feature_type: str, name: str, geometry_geojson: str, properties_json: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        feature = self.gis.create_feature(farm_id=farm_id, plot_id=plot_id, feature_type=feature_type, name=name, geometry_geojson=geometry_geojson, properties_json=properties_json)
        self.gis.create_version(feature=feature, changed_by_user_id=user.id)
        self.audit.add(module='gis', action='create_feature', user_id=user.id, farm_id=farm_id, record_id=str(feature.id))
        self.db.commit(); self.db.refresh(feature)
        return feature

    def get_for_user(self, *, user: User, feature_id: int):
        feature = self.gis.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Elemento SIG no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=feature.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return feature

    def update_for_user(self, *, user: User, feature_id: int, name: str | None, geometry_geojson: str | None, properties_json: str | None):
        feature = self.get_for_user(user=user, feature_id=feature_id)
        updated = self.gis.update_fields(feature, name=name, geometry_geojson=geometry_geojson, properties_json=properties_json)
        self.gis.create_version(feature=updated, changed_by_user_id=user.id)
        self.audit.add(module='gis', action='update_feature', user_id=user.id, farm_id=feature.farm_id, record_id=str(feature.id))
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def list_history_for_user(self, *, user: User, feature_id: int, limit: int = 100, offset: int = 0) -> MapFeatureVersionListResponse:
        feature = self.get_for_user(user=user, feature_id=feature_id)
        total, items = self.gis.list_versions(feature.id, limit=limit, offset=offset)
        return MapFeatureVersionListResponse(total=total, items=items)
