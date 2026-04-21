from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.farm_setting import FarmSetting
from app.models.farm_setting_history import FarmSettingHistory
from app.models.setting_template import SettingTemplate


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_setting(self, *, farm_id: int, category: str, setting_key: str, setting_value: str) -> FarmSetting:
        q = select(FarmSetting).where(FarmSetting.farm_id == farm_id, FarmSetting.category == category, FarmSetting.setting_key == setting_key)
        existing = self.db.scalar(q)
        if existing is None:
            existing = FarmSetting(farm_id=farm_id, category=category, setting_key=setting_key, setting_value=setting_value)
            self.db.add(existing)
            self.db.flush()
            return existing
        existing.setting_value = setting_value
        self.db.flush()
        return existing

    def add_history(
        self,
        *,
        setting_id: int,
        changed_by_user_id: int | None,
        previous_value: str | None,
        new_value: str,
    ) -> FarmSettingHistory:
        event = FarmSettingHistory(
            setting_id=setting_id,
            changed_by_user_id=changed_by_user_id,
            previous_value=previous_value,
            new_value=new_value,
        )
        self.db.add(event)
        self.db.flush()
        return event

    def list_history_by_setting_id(
        self,
        setting_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[FarmSettingHistory]]:
        q = select(FarmSettingHistory).where(FarmSettingHistory.setting_id == setting_id)
        count_q = select(func.count(FarmSettingHistory.id)).where(FarmSettingHistory.setting_id == setting_id)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(FarmSettingHistory.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())


    def get_by_unique_key(self, *, farm_id: int, category: str, setting_key: str) -> FarmSetting | None:
        q = select(FarmSetting).where(
            FarmSetting.farm_id == farm_id,
            FarmSetting.category == category,
            FarmSetting.setting_key == setting_key,
        )
        return self.db.scalar(q)


    def list_templates(self, *, crop_type: str | None = None) -> list[SettingTemplate]:
        q = select(SettingTemplate).where(SettingTemplate.is_active.is_(True))
        if crop_type is not None:
            q = q.where(SettingTemplate.crop_type == crop_type)
        q = q.order_by(SettingTemplate.crop_type.asc(), SettingTemplate.category.asc(), SettingTemplate.setting_key.asc())
        return list(self.db.scalars(q).all())

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        category: str | None = None,
        setting_key_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[FarmSetting]]:
        if not farm_ids:
            return 0, []

        q = select(FarmSetting).where(FarmSetting.farm_id.in_(farm_ids))
        count_q = select(func.count(FarmSetting.id)).where(FarmSetting.farm_id.in_(farm_ids))

        if farm_id is not None:
            q = q.where(FarmSetting.farm_id == farm_id)
            count_q = count_q.where(FarmSetting.farm_id == farm_id)
        if category is not None:
            q = q.where(FarmSetting.category == category)
            count_q = count_q.where(FarmSetting.category == category)
        if setting_key_search is not None:
            pattern = f'%{setting_key_search}%'
            q = q.where(FarmSetting.setting_key.ilike(pattern))
            count_q = count_q.where(FarmSetting.setting_key.ilike(pattern))

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(FarmSetting.category.asc(), FarmSetting.setting_key.asc(), FarmSetting.id.asc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, setting_id: int) -> FarmSetting | None:
        return self.db.get(FarmSetting, setting_id)
