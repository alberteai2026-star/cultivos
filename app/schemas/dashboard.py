from datetime import datetime

from pydantic import BaseModel, Field


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


class DashboardSnapshotListResponse(BaseModel):
    total: int
    items: list[DashboardSnapshotOut]


class DashboardKPICompareResponse(BaseModel):
    total_farms: int
    items: list[DashboardKPIOut]


class DashboardGoalCreateRequest(BaseModel):
    farm_id: int
    kpi_key: str = Field(min_length=2, max_length=50)
    target_value: float
    period_label: str | None = Field(default=None, min_length=2, max_length=30)


class DashboardGoalUpdateRequest(BaseModel):
    target_value: float | None = None
    period_label: str | None = Field(default=None, min_length=2, max_length=30)
    status: str | None = Field(default=None, min_length=2, max_length=20)


class DashboardGoalOut(BaseModel):
    id: int
    farm_id: int
    kpi_key: str
    target_value: float
    period_label: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DashboardGoalListResponse(BaseModel):
    total: int
    items: list[DashboardGoalOut]


class DashboardAlertOut(BaseModel):
    farm_id: int
    kpi_key: str
    period_label: str | None
    current_value: float
    target_value: float
    delta_value: float
    state: str


class DashboardAlertListResponse(BaseModel):
    total: int
    items: list[DashboardAlertOut]
