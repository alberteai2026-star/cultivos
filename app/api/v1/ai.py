from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import (
    AIPredictiveAlertListResponse,
    AIInsightCreateRequest,
    AIInsightListResponse,
    AIInsightOut,
    AIInsightRecommendationListResponse,
    AIInsightStatusUpdateRequest,
    AIInsightSummaryResponse,
    AIInsightUpdateRequest,
    AIYieldForecastListResponse,
)
from app.services.ai_service import AIService

router = APIRouter()


@router.get('/insights', response_model=AIInsightListResponse)
def list_ai_insights(
    farm_id: int | None = Query(default=None, ge=1),
    insight_type: str | None = None,
    priority: str | None = None,
    confidence_min: float | None = Query(default=None, ge=0, le=100),
    confidence_max: float | None = Query(default=None, ge=0, le=100),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AIService(db).list_for_user(
        user,
        farm_id=farm_id,
        insight_type=insight_type,
        priority=priority,
        confidence_min=confidence_min,
        confidence_max=confidence_max,
        limit=limit,
        offset=offset,
    )


@router.get('/insights/recommendations', response_model=AIInsightRecommendationListResponse)
def list_ai_recommendations(
    farm_id: int | None = Query(default=None, ge=1),
    min_confidence: float | None = Query(default=60, ge=0, le=100),
    only_pending: bool = True,
    limit: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AIService(db).recommendations_for_user(
        user=user,
        farm_id=farm_id,
        min_confidence=min_confidence,
        only_pending=only_pending,
        limit=limit,
    )


@router.get('/insights/summary', response_model=AIInsightSummaryResponse)
def get_ai_insights_summary(
    farm_id: int | None = Query(default=None, ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AIService(db).summary_for_user(user=user, farm_id=farm_id)


@router.get('/insights/yield-forecast', response_model=AIYieldForecastListResponse)
def get_ai_yield_forecast(
    farm_id: int | None = Query(default=None, ge=1),
    lookback_limit: int = Query(default=24, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AIService(db).yield_forecast_for_user(user=user, farm_id=farm_id, lookback_limit=lookback_limit)


@router.get('/insights/predictive-alerts', response_model=AIPredictiveAlertListResponse)
def list_ai_predictive_alerts(
    farm_id: int | None = Query(default=None, ge=1),
    min_confidence: float = Query(default=70, ge=0, le=100),
    limit: int = Query(default=100, ge=1, le=300),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AIService(db).predictive_alerts_for_user(
        user=user,
        farm_id=farm_id,
        min_confidence=min_confidence,
        limit=limit,
    )


@router.post('/insights', response_model=AIInsightOut, status_code=201)
def create_ai_insight(payload: AIInsightCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AIService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, crop_cycle_id=payload.crop_cycle_id, insight_type=payload.insight_type, title=payload.title, recommendation=payload.recommendation, predicted_value=payload.predicted_value, confidence=payload.confidence, priority=payload.priority, generated_at=payload.generated_at)


@router.get('/insights/{insight_id}', response_model=AIInsightOut)
def get_ai_insight(insight_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AIService(db).get_for_user(user=user, insight_id=insight_id)


@router.patch('/insights/{insight_id}', response_model=AIInsightOut)
def update_ai_insight(insight_id: int, payload: AIInsightUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AIService(db).update_for_user(
        user=user,
        insight_id=insight_id,
        title=payload.title,
        recommendation=payload.recommendation,
        predicted_value=payload.predicted_value,
        confidence=payload.confidence,
        priority=payload.priority,
    )


@router.patch('/insights/{insight_id}/status', response_model=AIInsightOut)
def update_ai_insight_status(insight_id: int, payload: AIInsightStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AIService(db).update_status_for_user(
        user=user,
        insight_id=insight_id,
        status_value=payload.status,
        outcome_notes=payload.outcome_notes,
        resolved_at=payload.resolved_at,
    )
