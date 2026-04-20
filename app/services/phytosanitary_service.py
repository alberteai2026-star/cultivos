from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.phytosanitary_repository import PhytosanitaryRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class PhytosanitaryService:
    def __init__(self, db: Session):
        self.db = db
        self.phytosanitary = PhytosanitaryRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.phytosanitary.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int, crop_cycle_id: int | None, detected_issue: str, severity: str, action_taken: str, observed_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        record = self.phytosanitary.create(farm_id=farm_id, plot_id=plot_id, crop_cycle_id=crop_cycle_id, detected_issue=detected_issue, severity=severity, action_taken=action_taken, observed_at=observed_at)
        self.audit.add(module='phytosanitary', action='create', user_id=user.id, farm_id=farm_id, record_id=str(record.id))
        self.db.commit(); self.db.refresh(record)
        return record
