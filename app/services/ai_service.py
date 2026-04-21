from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.ai_repository import AIRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.ai import AIInsightListResponse


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
