from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.settings_repository import SettingsRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.settings import ApplySettingTemplateResponse, FarmSettingHistoryListResponse, FarmSettingListResponse, SettingTemplateListResponse


class SettingsService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = SettingsRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        category: str | None = None,
        setting_key_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> FarmSettingListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.settings.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            category=category,
            setting_key_search=setting_key_search,
            limit=limit,
            offset=offset,
        )
        return FarmSettingListResponse(total=total, items=items)

    def upsert_for_user(self, *, user: User, farm_id: int, category: str, setting_key: str, setting_value: str):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        existing = self.settings.get_by_unique_key(farm_id=farm_id, category=category, setting_key=setting_key)
        previous_value = existing.setting_value if existing else None

        setting = self.settings.upsert_setting(farm_id=farm_id, category=category, setting_key=setting_key, setting_value=setting_value)
        self.settings.add_history(
            setting_id=setting.id,
            changed_by_user_id=user.id,
            previous_value=previous_value,
            new_value=setting_value,
        )
        self.audit.add(module='settings', action='upsert', user_id=user.id, farm_id=farm_id, record_id=str(setting.id))
        self.db.commit(); self.db.refresh(setting)
        return setting

    def get_for_user(self, *, user: User, setting_id: int):
        setting = self.settings.get_by_id(setting_id)
        if not setting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Configuración no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=setting.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return setting

    def update_value_for_user(self, *, user: User, setting_id: int, setting_value: str):
        setting = self.get_for_user(user=user, setting_id=setting_id)
        previous_value = setting.setting_value
        setting.setting_value = setting_value
        self.settings.add_history(
            setting_id=setting.id,
            changed_by_user_id=user.id,
            previous_value=previous_value,
            new_value=setting_value,
        )
        self.audit.add(module='settings', action='update_value', user_id=user.id, farm_id=setting.farm_id, record_id=str(setting.id))
        self.db.commit()
        self.db.refresh(setting)
        return setting

    def list_history_for_user(
        self,
        *,
        user: User,
        setting_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> FarmSettingHistoryListResponse:
        setting = self.get_for_user(user=user, setting_id=setting_id)
        total, items = self.settings.list_history_by_setting_id(setting.id, limit=limit, offset=offset)
        return FarmSettingHistoryListResponse(total=total, items=items)


    def list_templates_for_user(self, *, user: User, crop_type: str | None = None) -> SettingTemplateListResponse:
        # Endpoint autenticado para mantener trazabilidad por usuario, sin restricción por finca.
        templates = self.settings.list_templates(crop_type=crop_type)
        return SettingTemplateListResponse(total=len(templates), items=templates)

    def apply_template_for_user(self, *, user: User, farm_id: int, crop_type: str) -> ApplySettingTemplateResponse:
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        templates = self.settings.list_templates(crop_type=crop_type)
        applied_count = 0
        for template in templates:
            existing = self.settings.get_by_unique_key(farm_id=farm_id, category=template.category, setting_key=template.setting_key)
            previous_value = existing.setting_value if existing else None
            setting = self.settings.upsert_setting(
                farm_id=farm_id,
                category=template.category,
                setting_key=template.setting_key,
                setting_value=template.default_value,
            )
            self.settings.add_history(
                setting_id=setting.id,
                changed_by_user_id=user.id,
                previous_value=previous_value,
                new_value=template.default_value,
            )
            applied_count += 1

        self.audit.add(module='settings', action='apply_template', user_id=user.id, farm_id=farm_id, record_id=f'{crop_type}:{applied_count}')
        self.db.commit()
        return ApplySettingTemplateResponse(farm_id=farm_id, crop_type=crop_type, applied_count=applied_count)
