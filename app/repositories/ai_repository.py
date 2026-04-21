from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_insight import AIInsight


class AIRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_insight(self, *, farm_id: int, plot_id: int | None, crop_cycle_id: int | None, insight_type: str, title: str, recommendation: str, predicted_value: float | None, confidence: float | None, priority: str, generated_at: datetime) -> AIInsight:
        insight = AIInsight(
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            insight_type=insight_type,
            title=title,
            recommendation=recommendation,
            predicted_value=predicted_value,
            confidence=confidence,
            priority=priority,
            generated_at=generated_at,
        )
        self.db.add(insight)
        self.db.flush()
        return insight

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        insight_type: str | None = None,
        priority: str | None = None,
        confidence_min: float | None = None,
        confidence_max: float | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[AIInsight]]:
        if not farm_ids:
            return 0, []
        q = select(AIInsight).where(AIInsight.farm_id.in_(farm_ids))
        count_q = select(func.count(AIInsight.id)).where(AIInsight.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(AIInsight.farm_id == farm_id)
            count_q = count_q.where(AIInsight.farm_id == farm_id)
        if insight_type is not None:
            q = q.where(AIInsight.insight_type == insight_type)
            count_q = count_q.where(AIInsight.insight_type == insight_type)
        if priority is not None:
            q = q.where(AIInsight.priority == priority)
            count_q = count_q.where(AIInsight.priority == priority)
        if confidence_min is not None:
            q = q.where(AIInsight.confidence >= confidence_min)
            count_q = count_q.where(AIInsight.confidence >= confidence_min)
        if confidence_max is not None:
            q = q.where(AIInsight.confidence <= confidence_max)
            count_q = count_q.where(AIInsight.confidence <= confidence_max)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(AIInsight.generated_at.desc(), AIInsight.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, insight_id: int) -> AIInsight | None:
        return self.db.get(AIInsight, insight_id)

    def update_fields(
        self,
        insight: AIInsight,
        *,
        title: str | None = None,
        recommendation: str | None = None,
        predicted_value: float | None = None,
        confidence: float | None = None,
        priority: str | None = None,
    ) -> AIInsight:
        if title is not None:
            insight.title = title
        if recommendation is not None:
            insight.recommendation = recommendation
        if predicted_value is not None:
            insight.predicted_value = predicted_value
        if confidence is not None:
            insight.confidence = confidence
        if priority is not None:
            insight.priority = priority
        self.db.add(insight)
        return insight


    def update_status(
        self,
        insight: AIInsight,
        *,
        status: str,
        outcome_notes: str | None,
        resolved_at: datetime | None,
    ) -> AIInsight:
        insight.status = status
        if outcome_notes is not None:
            insight.outcome_notes = outcome_notes
        if resolved_at is not None:
            insight.resolved_at = resolved_at
        self.db.add(insight)
        return insight
