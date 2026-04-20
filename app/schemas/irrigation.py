from datetime import datetime

from pydantic import BaseModel


class IrrigationEventCreateRequest(BaseModel):
    plot_id: int
    scheduled_at: datetime
    applied_mm: float | None = None
    cost: float | None = None


class IrrigationEventOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int
    scheduled_at: datetime
    applied_mm: float | None
    cost: float | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
