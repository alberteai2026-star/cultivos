from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.settings import (
    ApplySettingTemplateRequest,
    ApplySettingTemplateResponse,
    FarmSettingCreateRequest,
    FarmSettingHistoryListResponse,
    FarmSettingListResponse,
    FarmSettingOut,
    FarmSettingUpdateRequest,
    SettingTemplateListResponse,
)
from app.services.settings_service import SettingsService

router = APIRouter()


@router.get('/farm', response_model=FarmSettingListResponse)
def list_farm_settings(
    farm_id: int | None = Query(default=None, ge=1),
    category: str | None = None,
    setting_key_search: str | None = Query(default=None, alias='search'),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SettingsService(db).list_for_user(
        user,
        farm_id=farm_id,
        category=category,
        setting_key_search=setting_key_search,
        limit=limit,
        offset=offset,
    )


@router.post('/farm', response_model=FarmSettingOut, status_code=201)
def upsert_farm_setting(payload: FarmSettingCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SettingsService(db).upsert_for_user(user=user, farm_id=payload.farm_id, category=payload.category, setting_key=payload.setting_key, setting_value=payload.setting_value)


@router.get('/farm/{setting_id}', response_model=FarmSettingOut)
def get_farm_setting(setting_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SettingsService(db).get_for_user(user=user, setting_id=setting_id)


@router.patch('/farm/{setting_id}', response_model=FarmSettingOut)
def update_farm_setting(setting_id: int, payload: FarmSettingUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SettingsService(db).update_value_for_user(user=user, setting_id=setting_id, setting_value=payload.setting_value)


@router.get('/farm/{setting_id}/history', response_model=FarmSettingHistoryListResponse)
def list_farm_setting_history(
    setting_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SettingsService(db).list_history_for_user(user=user, setting_id=setting_id, limit=limit, offset=offset)


@router.get('/templates', response_model=SettingTemplateListResponse)
def list_setting_templates(crop_type: str | None = Query(default=None), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SettingsService(db).list_templates_for_user(user=user, crop_type=crop_type)


@router.post('/farm/apply-template', response_model=ApplySettingTemplateResponse)
def apply_setting_template(payload: ApplySettingTemplateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SettingsService(db).apply_template_for_user(user=user, farm_id=payload.farm_id, crop_type=payload.crop_type)
