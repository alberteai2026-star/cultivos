from datetime import datetime

from pydantic import BaseModel, Field


class NurseryBatchCreateRequest(BaseModel):
    farm_id: int
    plot_id: int | None = None
    species: str = Field(min_length=2, max_length=120)
    variety: str | None = Field(default=None, max_length=120)
    sowing_date: datetime
    tray_count: int = Field(ge=0)
    status: str = Field(default='activo', max_length=30)
    notes: str | None = Field(default=None, max_length=250)


class NurseryBatchUpdateRequest(BaseModel):
    species: str | None = Field(default=None, min_length=2, max_length=120)
    variety: str | None = Field(default=None, max_length=120)
    sowing_date: datetime | None = None
    tray_count: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=250)


class NurseryBatchStatusUpdateRequest(BaseModel):
    status: str = Field(min_length=2, max_length=30)


class NurseryBatchOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    species: str
    variety: str | None
    sowing_date: datetime
    tray_count: int
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NurseryBatchListResponse(BaseModel):
    total: int
    items: list[NurseryBatchOut]
