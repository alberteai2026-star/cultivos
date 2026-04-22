from datetime import datetime

from pydantic import BaseModel, Field


class FarmSettingCreateRequest(BaseModel):
    farm_id: int
    category: str = Field(min_length=2, max_length=60)
    setting_key: str = Field(min_length=2, max_length=80)
    setting_value: str = Field(min_length=1)


class FarmSettingUpdateRequest(BaseModel):
    setting_value: str = Field(min_length=1)


class FarmSettingOut(BaseModel):
    id: int
    farm_id: int
    category: str
    setting_key: str
    setting_value: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FarmSettingListResponse(BaseModel):
    total: int
    items: list[FarmSettingOut]


class FarmSettingHistoryOut(BaseModel):
    id: int
    setting_id: int
    changed_by_user_id: int | None
    previous_value: str | None
    new_value: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FarmSettingHistoryListResponse(BaseModel):
    total: int
    items: list[FarmSettingHistoryOut]


class SettingTemplateOut(BaseModel):
    id: int
    crop_type: str
    category: str
    setting_key: str
    default_value: str

    model_config = {"from_attributes": True}


class SettingTemplateListResponse(BaseModel):
    total: int
    items: list[SettingTemplateOut]


class ApplySettingTemplateRequest(BaseModel):
    farm_id: int
    crop_type: str = Field(min_length=2, max_length=60)


class ApplySettingTemplateResponse(BaseModel):
    farm_id: int
    crop_type: str
    applied_count: int
