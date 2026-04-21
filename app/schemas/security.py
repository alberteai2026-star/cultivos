from datetime import datetime

from pydantic import BaseModel, Field


class SecurityIncidentCreateRequest(BaseModel):
    farm_id: int
    alert_type: str = Field(min_length=2, max_length=50)
    severity: str = Field(default='media', max_length=20)
    description: str | None = None
    detected_at: datetime


class SecurityIncidentStatusUpdateRequest(BaseModel):
    status: str = Field(max_length=20)
    resolved_at: datetime | None = None


class SecurityIncidentOut(BaseModel):
    id: int
    farm_id: int
    alert_type: str
    severity: str
    status: str
    description: str | None
    detected_at: datetime
    resolved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SecurityIncidentListResponse(BaseModel):
    total: int
    items: list[SecurityIncidentOut]
