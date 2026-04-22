from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_insight import AIInsight
from app.models.harvest import Harvest


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

    def list_recommendations_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        min_confidence: float | None = None,
        only_pending: bool = True,
        limit: int = 50,
    ) -> tuple[int, list[AIInsight]]:
        if not farm_ids:
            return 0, []
        q = select(AIInsight).where(AIInsight.farm_id.in_(farm_ids))
        count_q = select(func.count(AIInsight.id)).where(AIInsight.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(AIInsight.farm_id == farm_id)
            count_q = count_q.where(AIInsight.farm_id == farm_id)
        if min_confidence is not None:
            q = q.where(AIInsight.confidence >= min_confidence)
            count_q = count_q.where(AIInsight.confidence >= min_confidence)
        if only_pending:
            q = q.where(AIInsight.status.in_(['nuevo', 'en_revision']))
            count_q = count_q.where(AIInsight.status.in_(['nuevo', 'en_revision']))

        q = q.order_by(AIInsight.priority.asc(), AIInsight.confidence.desc(), AIInsight.generated_at.desc()).limit(limit)
        total = int(self.db.scalar(count_q) or 0)
        return total, list(self.db.scalars(q).all())

    def summary_by_dimensions(self, *, farm_ids: list[int], farm_id: int | None = None) -> list[tuple[str, str, str, int]]:
        if not farm_ids:
            return []
        q = (
            select(AIInsight.insight_type, AIInsight.status, AIInsight.priority, func.count(AIInsight.id))
            .where(AIInsight.farm_id.in_(farm_ids))
            .group_by(AIInsight.insight_type, AIInsight.status, AIInsight.priority)
            .order_by(func.count(AIInsight.id).desc(), AIInsight.insight_type.asc())
        )
        if farm_id is not None:
            q = q.where(AIInsight.farm_id == farm_id)
        return [(str(r[0]), str(r[1]), str(r[2]), int(r[3])) for r in self.db.execute(q).all()]

    def harvest_history_by_plot(
        self,
        *,
        farm_ids: list[int],
        farm_id: int | None = None,
        lookback_limit: int = 24,
    ) -> list[tuple[int, int, float, int, datetime]]:
        if not farm_ids:
            return []
        base = select(Harvest).where(Harvest.farm_id.in_(farm_ids))
        if farm_id is not None:
            base = base.where(Harvest.farm_id == farm_id)
        base = base.order_by(Harvest.harvested_at.desc()).limit(lookback_limit)
        subq = base.subquery()

        q = (
            select(
                subq.c.farm_id,
                subq.c.plot_id,
                func.avg(subq.c.quantity),
                func.count(subq.c.id),
                func.max(subq.c.harvested_at),
            )
            .group_by(subq.c.farm_id, subq.c.plot_id)
            .order_by(func.avg(subq.c.quantity).desc())
        )
        return [(int(r[0]), int(r[1]), float(r[2]), int(r[3]), r[4]) for r in self.db.execute(q).all()]

    def latest_yield_insights_by_plot(
        self,
        *,
        farm_ids: list[int],
        farm_id: int | None = None,
    ) -> dict[int, AIInsight]:
        if not farm_ids:
            return {}
        q = select(AIInsight).where(AIInsight.farm_id.in_(farm_ids), AIInsight.insight_type == 'yield_forecast')
        if farm_id is not None:
            q = q.where(AIInsight.farm_id == farm_id)
        q = q.order_by(AIInsight.generated_at.desc(), AIInsight.id.desc())
        items = list(self.db.scalars(q).all())
        by_plot: dict[int, AIInsight] = {}
        for item in items:
            if item.plot_id is None:
                continue
            if item.plot_id not in by_plot:
                by_plot[item.plot_id] = item
        return by_plot

    def list_predictive_alerts_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        min_confidence: float = 70,
        limit: int = 100,
    ) -> tuple[int, list[AIInsight]]:
        if not farm_ids:
            return 0, []
        alert_types = ['risk_alert']
        q = select(AIInsight).where(
            AIInsight.farm_id.in_(farm_ids),
            AIInsight.insight_type.in_(alert_types),
            AIInsight.status.in_(['nuevo', 'en_revision']),
        )
        count_q = select(func.count(AIInsight.id)).where(
            AIInsight.farm_id.in_(farm_ids),
            AIInsight.insight_type.in_(alert_types),
            AIInsight.status.in_(['nuevo', 'en_revision']),
        )
        if farm_id is not None:
            q = q.where(AIInsight.farm_id == farm_id)
            count_q = count_q.where(AIInsight.farm_id == farm_id)
        q = q.where(AIInsight.confidence >= min_confidence).order_by(AIInsight.confidence.desc(), AIInsight.generated_at.desc()).limit(limit)
        count_q = count_q.where(AIInsight.confidence >= min_confidence)
        total = int(self.db.scalar(count_q) or 0)
        return total, list(self.db.scalars(q).all())

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
