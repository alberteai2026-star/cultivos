from datetime import datetime

from pydantic import BaseModel, Field


class PhytosanitaryRecordCreateRequest(BaseModel):
    farm_id: int
    plot_id: int
    crop_cycle_id: int | None = None
    detected_issue: str = Field(min_length=2, max_length=150)
    severity: str = Field(default='media', max_length=30)
    action_taken: str = Field(min_length=2)
    observed_at: datetime


class PhytosanitaryRecordOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int
    crop_cycle_id: int | None
    detected_issue: str
    severity: str
    action_taken: str
    observed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
