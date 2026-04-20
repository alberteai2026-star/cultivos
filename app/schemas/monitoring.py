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


class MonitoringVisitOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int
    crop_cycle_id: int | None
    observed_at: datetime
    bbch_stage: str | None
    issue_type: str | None
    severity: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
