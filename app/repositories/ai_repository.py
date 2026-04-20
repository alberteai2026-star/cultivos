from datetime import datetime

from sqlalchemy import select
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

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[AIInsight]:
        if not farm_ids:
            return []
        q = select(AIInsight).where(AIInsight.farm_id.in_(farm_ids)).order_by(AIInsight.generated_at.desc(), AIInsight.id.desc())
        return list(self.db.scalars(q).all())
