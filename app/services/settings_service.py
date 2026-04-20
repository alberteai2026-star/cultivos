from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.settings_repository import SettingsRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class SettingsService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = SettingsRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.settings.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def upsert_for_user(self, *, user: User, farm_id: int, category: str, setting_key: str, setting_value: str):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        setting = self.settings.upsert_setting(farm_id=farm_id, category=category, setting_key=setting_key, setting_value=setting_value)
        self.audit.add(module='settings', action='upsert', user_id=user.id, farm_id=farm_id, record_id=str(setting.id))
        self.db.commit(); self.db.refresh(setting)
        return setting
