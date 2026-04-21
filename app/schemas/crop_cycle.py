from datetime import datetime

from pydantic import BaseModel, Field


class CropCycleCreateRequest(BaseModel):
    plot_id: int
    species: str = Field(min_length=2, max_length=120)
    variety: str | None = Field(default=None, max_length=120)
    sowing_date: datetime


class CropCycleUpdateRequest(BaseModel):
    species: str | None = Field(default=None, min_length=2, max_length=120)
    variety: str | None = Field(default=None, max_length=120)
    sowing_date: datetime | None = None


class CropCycleStatusUpdateRequest(BaseModel):
    status: str = Field(max_length=30)


class CropCycleOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int
    species: str
    variety: str | None
    sowing_date: datetime
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CropCycleListResponse(BaseModel):
    total: int
    items: list[CropCycleOut]
