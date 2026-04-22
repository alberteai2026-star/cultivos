from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.ai_repository import AIRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.ai import (
    AIPredictiveAlertListResponse,
    AIInsightListResponse,
    AIInsightRecommendationListResponse,
    AIInsightSummaryItem,
    AIInsightSummaryResponse,
    AIYieldForecastListResponse,
    AIYieldForecastOut,
)


class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        insight_type: str | None = None,
        priority: str | None = None,
        confidence_min: float | None = None,
        confidence_max: float | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> AIInsightListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.ai.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            insight_type=insight_type,
            priority=priority,
            confidence_min=confidence_min,
            confidence_max=confidence_max,
            limit=limit,
            offset=offset,
        )
        return AIInsightListResponse(total=total, items=items)

    def recommendations_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        min_confidence: float | None = 60,
        only_pending: bool = True,
        limit: int = 50,
    ) -> AIInsightRecommendationListResponse:
        if min_confidence is not None and (min_confidence < 0 or min_confidence > 100):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='confidence debe estar entre 0 y 100')
        if limit < 1 or limit > 200:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='limit debe estar entre 1 y 200')

        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        total, items = self.ai.list_recommendations_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            min_confidence=min_confidence,
            only_pending=only_pending,
            limit=limit,
        )
        return AIInsightRecommendationListResponse(total=total, items=items)

    def summary_for_user(self, *, user: User, farm_id: int | None = None) -> AIInsightSummaryResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        rows = self.ai.summary_by_dimensions(farm_ids=farm_ids, farm_id=farm_id)
        items = [AIInsightSummaryItem(insight_type=t, status=s, priority=p, total=total) for t, s, p, total in rows]
        return AIInsightSummaryResponse(total_groups=len(items), items=items)

    def yield_forecast_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        lookback_limit: int = 24,
    ) -> AIYieldForecastListResponse:
        if lookback_limit < 1 or lookback_limit > 200:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='lookback_limit debe estar entre 1 y 200')
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        history = self.ai.harvest_history_by_plot(farm_ids=farm_ids, farm_id=farm_id, lookback_limit=lookback_limit)
        latest_ai = self.ai.latest_yield_insights_by_plot(farm_ids=farm_ids, farm_id=farm_id)
        generated_at = datetime.utcnow()

        items: list[AIYieldForecastOut] = []
        for hist_farm_id, plot_id, historical_avg, samples, _last_harvested_at in history:
            ai_insight = latest_ai.get(plot_id)
            ai_predicted = float(ai_insight.predicted_value) if ai_insight and ai_insight.predicted_value is not None else None
            ai_conf = float(ai_insight.confidence) if ai_insight and ai_insight.confidence is not None else None

            if ai_predicted is None:
                projected = historical_avg
            elif ai_conf is None:
                projected = ai_predicted
            else:
                alpha = min(max(ai_conf / 100.0, 0.0), 1.0)
                projected = round((historical_avg * (1 - alpha)) + (ai_predicted * alpha), 2)

            items.append(
                AIYieldForecastOut(
                    farm_id=hist_farm_id,
                    plot_id=plot_id,
                    historical_avg_quantity=round(historical_avg, 2),
                    historical_samples=samples,
                    ai_predicted_quantity=ai_predicted,
                    ai_confidence=ai_conf,
                    projected_quantity=round(projected, 2),
                    generated_at=generated_at,
                )
            )
        return AIYieldForecastListResponse(total=len(items), items=items)

    def predictive_alerts_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        min_confidence: float = 70,
        limit: int = 100,
    ) -> AIPredictiveAlertListResponse:
        if min_confidence < 0 or min_confidence > 100:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='confidence debe estar entre 0 y 100')
        if limit < 1 or limit > 300:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='limit debe estar entre 1 y 300')

        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.ai.list_predictive_alerts_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            min_confidence=min_confidence,
            limit=limit,
        )
        return AIPredictiveAlertListResponse(total=total, items=items)

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int | None, crop_cycle_id: int | None, insight_type: str, title: str, recommendation: str, predicted_value: float | None, confidence: float | None, priority: str, generated_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        insight = self.ai.create_insight(farm_id=farm_id, plot_id=plot_id, crop_cycle_id=crop_cycle_id, insight_type=insight_type, title=title, recommendation=recommendation, predicted_value=predicted_value, confidence=confidence, priority=priority, generated_at=generated_at)
        self.audit.add(module='ai', action='create_insight', user_id=user.id, farm_id=farm_id, record_id=str(insight.id))
        self.db.commit(); self.db.refresh(insight)
        return insight

    def get_for_user(self, *, user: User, insight_id: int):
        insight = self.ai.get_by_id(insight_id)
        if not insight:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Insight no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=insight.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return insight

    def update_for_user(
        self,
        *,
        user: User,
        insight_id: int,
        title: str | None,
        recommendation: str | None,
        predicted_value: float | None,
        confidence: float | None,
        priority: str | None,
    ):
        insight = self.get_for_user(user=user, insight_id=insight_id)
        updated = self.ai.update_fields(
            insight,
            title=title,
            recommendation=recommendation,
            predicted_value=predicted_value,
            confidence=confidence,
            priority=priority,
        )
        self.audit.add(module='ai', action='update_insight', user_id=user.id, farm_id=insight.farm_id, record_id=str(insight.id))
        self.db.commit()
        self.db.refresh(updated)
        return updated


    def update_status_for_user(
        self,
        *,
        user: User,
        insight_id: int,
        status_value: str,
        outcome_notes: str | None,
        resolved_at: datetime | None,
    ):
        insight = self.get_for_user(user=user, insight_id=insight_id)
        allowed_transitions = {
            'nuevo': {'en_revision', 'descartado'},
            'en_revision': {'aplicado', 'descartado'},
            'aplicado': {'validado', 'descartado'},
            'descartado': set(),
            'validado': set(),
        }
        current = insight.status or 'nuevo'
        if status_value != current and status_value not in allowed_transitions.get(current, set()):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Transición de estado no permitida')

        effective_resolved_at = resolved_at
        if status_value in {'descartado', 'validado'} and effective_resolved_at is None:
            effective_resolved_at = datetime.utcnow()

        updated = self.ai.update_status(
            insight,
            status=status_value,
            outcome_notes=outcome_notes,
            resolved_at=effective_resolved_at,
        )
        self.audit.add(module='ai', action='update_insight_status', user_id=user.id, farm_id=insight.farm_id, record_id=str(insight.id))
        self.db.commit()
        self.db.refresh(updated)
        return updated
