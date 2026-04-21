from datetime import datetime

from pydantic import BaseModel, Field


class RotationPlanCreateRequest(BaseModel):
    plot_id: int
    next_species: str = Field(min_length=2, max_length=120)
    recommendation: str | None = Field(default=None, max_length=500)


class RotationPlanUpdateRequest(BaseModel):
    next_species: str | None = Field(default=None, min_length=2, max_length=120)
    recommendation: str | None = Field(default=None, max_length=500)


class RotationPlanStatusUpdateRequest(BaseModel):
    status: str


class RotationPlanOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int
    next_species: str
    recommendation: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RotationPlanListResponse(BaseModel):
    total: int
    items: list[RotationPlanOut]
