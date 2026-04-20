import hashlib
import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditRepository(db)
        self.relations = UserFarmRoleRepository(db)

    def list_logs_for_user(self, *, user: User, farm_id: int | None, module: str | None, action: str | None):
        if farm_id is not None and not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        allowed_farms = self.relations.list_farm_ids_by_user(user.id)
        return self.audit.list_logs(farm_ids=allowed_farms, farm_id=farm_id, module=module, action=action)

    def create_export_for_user(self, *, user: User, farm_id: int | None, format: str, module: str | None, action: str | None):
        if farm_id is not None and not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        filters = {'farm_id': farm_id, 'module': module, 'action': action}
        digest = hashlib.sha256(json.dumps(filters, sort_keys=True).encode('utf-8')).hexdigest()
        export = self.audit.create_export(user_id=user.id, farm_id=farm_id, format=format, filters_json=json.dumps(filters, ensure_ascii=False), file_url=None, signature=digest)
        self.db.commit(); self.db.refresh(export)
        return export

    def list_exports_for_user(self, user: User):
        allowed_farms = self.relations.list_farm_ids_by_user(user.id)
        return self.audit.list_exports(user_id=user.id, farm_ids=allowed_farms)
