from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.gis_repository import GISRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class GISService:
    def __init__(self, db: Session):
        self.db = db
        self.gis = GISRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.gis.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int | None, feature_type: str, name: str, geometry_geojson: str, properties_json: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        feature = self.gis.create_feature(farm_id=farm_id, plot_id=plot_id, feature_type=feature_type, name=name, geometry_geojson=geometry_geojson, properties_json=properties_json)
        self.audit.add(module='gis', action='create_feature', user_id=user.id, farm_id=farm_id, record_id=str(feature.id))
        self.db.commit(); self.db.refresh(feature)
        return feature
