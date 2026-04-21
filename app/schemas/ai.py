from datetime import datetime

from pydantic import BaseModel, Field


class AIInsightCreateRequest(BaseModel):
    farm_id: int
    plot_id: int | None = None
    crop_cycle_id: int | None = None
    insight_type: str = Field(max_length=40, pattern='^(recommendation|yield_forecast|risk_alert)$')
    title: str = Field(min_length=2, max_length=150)
    recommendation: str = Field(min_length=2)
    predicted_value: float | None = None
    confidence: float | None = Field(default=None, ge=0, le=100)
    priority: str = Field(default='media', max_length=20)
    generated_at: datetime


class AIInsightUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=150)
    recommendation: str | None = Field(default=None, min_length=2)
    predicted_value: float | None = None
    confidence: float | None = Field(default=None, ge=0, le=100)
    priority: str | None = Field(default=None, max_length=20)


class AIInsightStatusUpdateRequest(BaseModel):
    status: str = Field(pattern='^(nuevo|en_revision|aplicado|descartado|validado)$')
    outcome_notes: str | None = None
    resolved_at: datetime | None = None


class AIInsightOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    crop_cycle_id: int | None
    insight_type: str
    title: str
    recommendation: str
    predicted_value: float | None
    confidence: float | None
    priority: str
    status: str
    outcome_notes: str | None
    resolved_at: datetime | None
    generated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class AIInsightListResponse(BaseModel):
    total: int
    items: list[AIInsightOut]
