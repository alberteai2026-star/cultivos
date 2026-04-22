from datetime import datetime

from pydantic import BaseModel, Field


class HarvestCreateRequest(BaseModel):
    plot_id: int
    crop_cycle_id: int | None = None
    harvested_at: datetime
    quantity: float
    unit: str = Field(default='kg', min_length=1, max_length=20)
    quality_grade: str | None = Field(default=None, max_length=30)
    destination: str | None = Field(default=None, max_length=80)


class HarvestUpdateRequest(BaseModel):
    harvested_at: datetime | None = None
    quantity: float | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    quality_grade: str | None = Field(default=None, max_length=30)
    destination: str | None = Field(default=None, max_length=80)


class HarvestOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None = None
    crop_cycle_id: int | None = None
    harvested_at: datetime | None = None
    quantity: float
    unit: str
    quality_grade: str | None = None
    destination: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class HarvestListResponse(BaseModel):
    total: int
    items: list[HarvestOut]
