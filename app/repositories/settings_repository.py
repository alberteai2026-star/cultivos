from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm_setting import FarmSetting


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

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[FarmSetting]:
        if not farm_ids:
            return []
        q = select(FarmSetting).where(FarmSetting.farm_id.in_(farm_ids)).order_by(FarmSetting.category.asc(), FarmSetting.setting_key.asc())
        return list(self.db.scalars(q).all())
