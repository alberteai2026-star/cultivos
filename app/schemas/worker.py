from datetime import datetime

from pydantic import BaseModel, Field


class WorkerCreateRequest(BaseModel):
    farm_id: int
    full_name: str = Field(min_length=3, max_length=150)
    document_id: str | None = Field(default=None, max_length=50)
    role_name: str | None = Field(default=None, max_length=80)
    daily_rate: float | None = None


class WorkerOut(BaseModel):
    id: int
    farm_id: int
    full_name: str
    document_id: str | None
    role_name: str | None
    daily_rate: float | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
