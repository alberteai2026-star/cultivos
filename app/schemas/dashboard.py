from datetime import datetime

from pydantic import BaseModel


class DashboardKPIOut(BaseModel):
    farm_id: int
    active_cycles: int
    pending_tasks: int
    inventory_low_items: int
    income_total: float
    cost_total: float
    net_total: float


class DashboardSnapshotCreateRequest(BaseModel):
    farm_id: int
    captured_at: datetime


class DashboardSnapshotOut(BaseModel):
    id: int
    farm_id: int
    active_cycles: int
    pending_tasks: int
    inventory_low_items: int
    income_total: float
    cost_total: float
    captured_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
