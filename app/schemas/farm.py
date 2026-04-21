from datetime import datetime

from pydantic import BaseModel, Field


class FarmCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    total_area_ha: float | None = None
    department: str | None = Field(default=None, max_length=80)
    municipality: str | None = Field(default=None, max_length=80)


class FarmUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    total_area_ha: float | None = None
    department: str | None = Field(default=None, max_length=80)
    municipality: str | None = Field(default=None, max_length=80)


class FarmOut(BaseModel):
    id: int
    name: str
    total_area_ha: float | None
    department: str | None
    municipality: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FarmListResponse(BaseModel):
    total: int
    items: list[FarmOut]
