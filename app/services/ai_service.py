from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.ai_repository import AIRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.ai.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int | None, crop_cycle_id: int | None, insight_type: str, title: str, recommendation: str, predicted_value: float | None, confidence: float | None, priority: str, generated_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        insight = self.ai.create_insight(farm_id=farm_id, plot_id=plot_id, crop_cycle_id=crop_cycle_id, insight_type=insight_type, title=title, recommendation=recommendation, predicted_value=predicted_value, confidence=confidence, priority=priority, generated_at=generated_at)
        self.audit.add(module='ai', action='create_insight', user_id=user.id, farm_id=farm_id, record_id=str(insight.id))
        self.db.commit(); self.db.refresh(insight)
        return insight
