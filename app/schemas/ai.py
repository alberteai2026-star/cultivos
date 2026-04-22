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


class AIInsightRecommendationOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    title: str
    recommendation: str
    priority: str
    confidence: float | None
    generated_at: datetime

    model_config = {"from_attributes": True}


class AIInsightRecommendationListResponse(BaseModel):
    total: int
    items: list[AIInsightRecommendationOut]


class AIInsightSummaryItem(BaseModel):
    insight_type: str
    status: str
    priority: str
    total: int


class AIInsightSummaryResponse(BaseModel):
    total_groups: int
    items: list[AIInsightSummaryItem]


class AIYieldForecastOut(BaseModel):
    farm_id: int
    plot_id: int
    historical_avg_quantity: float
    historical_samples: int
    ai_predicted_quantity: float | None
    ai_confidence: float | None
    projected_quantity: float
    generated_at: datetime


class AIYieldForecastListResponse(BaseModel):
    total: int
    items: list[AIYieldForecastOut]


class AIPredictiveAlertOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    insight_type: str
    title: str
    recommendation: str
    priority: str
    confidence: float | None
    status: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class AIPredictiveAlertListResponse(BaseModel):
    total: int
    items: list[AIPredictiveAlertOut]
