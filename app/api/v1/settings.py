from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.settings import FarmSettingCreateRequest, FarmSettingOut
from app.services.settings_service import SettingsService

router = APIRouter()


@router.get('/farm', response_model=list[FarmSettingOut])
def list_farm_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SettingsService(db).list_for_user(user)


@router.post('/farm', response_model=FarmSettingOut, status_code=201)
def upsert_farm_setting(payload: FarmSettingCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SettingsService(db).upsert_for_user(user=user, farm_id=payload.farm_id, category=payload.category, setting_key=payload.setting_key, setting_value=payload.setting_value)
