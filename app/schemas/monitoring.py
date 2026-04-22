from datetime import datetime

from pydantic import BaseModel, Field


class MonitoringVisitCreateRequest(BaseModel):
    plot_id: int
    crop_cycle_id: int | None = None
    observed_at: datetime
    bbch_stage: str | None = Field(default=None, max_length=20)
    issue_type: str | None = Field(default=None, max_length=80)
    severity: str | None = Field(default=None, max_length=20)
    notes: str | None = Field(default=None, max_length=500)


class MonitoringVisitUpdateRequest(BaseModel):
    observed_at: datetime | None = None
    bbch_stage: str | None = Field(default=None, max_length=20)
    issue_type: str | None = Field(default=None, max_length=80)
    severity: str | None = Field(default=None, max_length=20)
    notes: str | None = Field(default=None, max_length=500)


class MonitoringVisitOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None = None
    crop_cycle_id: int | None = None
    observed_at: datetime | None = None
    bbch_stage: str | None = None
    issue_type: str | None = None
    severity: str | None = None
    notes: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class MonitoringVisitListResponse(BaseModel):
    total: int
    items: list[MonitoringVisitOut]
