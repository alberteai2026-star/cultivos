from datetime import datetime

from pydantic import BaseModel, Field


class FarmSettingCreateRequest(BaseModel):
    farm_id: int
    category: str = Field(min_length=2, max_length=60)
    setting_key: str = Field(min_length=2, max_length=80)
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
