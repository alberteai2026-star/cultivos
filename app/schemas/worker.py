from datetime import datetime

from pydantic import BaseModel, Field


class WorkerCreateRequest(BaseModel):
    farm_id: int
    full_name: str = Field(min_length=3, max_length=150)
    document_id: str | None = Field(default=None, max_length=50)
    role_name: str | None = Field(default=None, max_length=80)
    daily_rate: float | None = None


class WorkerUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=3, max_length=150)
    document_id: str | None = Field(default=None, max_length=50)
    role_name: str | None = Field(default=None, max_length=80)
    daily_rate: float | None = None


class WorkerStatusUpdateRequest(BaseModel):
    is_active: bool


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


class WorkerListResponse(BaseModel):
    total: int
    items: list[WorkerOut]


class WorkerTrackingPointCreateRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_kmh: float | None = Field(default=None, ge=0)
    recorded_at: datetime
    source: str = Field(default='mobile', max_length=20)
    notes: str | None = None


class WorkerTrackingPointOut(BaseModel):
    id: int
    worker_id: int
    latitude: float
    longitude: float
    speed_kmh: float | None
    recorded_at: datetime
    source: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerTrackingPointListResponse(BaseModel):
    total: int
    items: list[WorkerTrackingPointOut]
