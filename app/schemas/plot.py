from datetime import datetime

from pydantic import BaseModel, Field


class PlotCreateRequest(BaseModel):
    farm_id: int
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=2, max_length=150)
    area_ha: float | None = None
    soil_type: str | None = Field(default=None, max_length=80)
    status: str = Field(default='libre', max_length=30)


class PlotUpdateRequest(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=2, max_length=150)
    area_ha: float | None = None
    soil_type: str | None = Field(default=None, max_length=80)
    status: str | None = Field(default=None, max_length=30)


class PlotOut(BaseModel):
    id: int
    farm_id: int
    code: str
    name: str
    area_ha: float | None
    soil_type: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PlotListResponse(BaseModel):
    total: int
    items: list[PlotOut]
