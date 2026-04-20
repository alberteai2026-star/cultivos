from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    plot_id: int
    crop_cycle_id: int | None = None
    task_type: str = Field(min_length=2, max_length=80)
    title: str = Field(min_length=2, max_length=180)
    planned_date: datetime
    notes: str | None = Field(default=None, max_length=500)


class TaskStatusUpdateRequest(BaseModel):
    status: str = Field(max_length=30)


class TaskOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int
    crop_cycle_id: int | None
    task_type: str
    title: str
    planned_date: datetime
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
