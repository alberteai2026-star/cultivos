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


class HarvestOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int
    crop_cycle_id: int | None
    harvested_at: datetime
    quantity: float
    unit: str
    quality_grade: str | None
    destination: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
