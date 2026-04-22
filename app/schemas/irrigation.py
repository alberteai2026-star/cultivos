from datetime import datetime

from pydantic import BaseModel


class IrrigationEventCreateRequest(BaseModel):
    plot_id: int
    scheduled_at: datetime
    applied_mm: float | None = None
    cost: float | None = None


class IrrigationEventUpdateRequest(BaseModel):
    scheduled_at: datetime | None = None
    applied_mm: float | None = None
    cost: float | None = None


class IrrigationStatusUpdateRequest(BaseModel):
    status: str


class IrrigationEventOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None = None
    scheduled_at: datetime | None = None
    applied_mm: float | None = None
    cost: float | None = None
    status: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class IrrigationEventListResponse(BaseModel):
    total: int
    items: list[IrrigationEventOut]
