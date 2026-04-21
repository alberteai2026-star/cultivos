from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.phytosanitary_repository import PhytosanitaryRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.phytosanitary import PhytosanitaryRecordListResponse


class PhytosanitaryService:
    def __init__(self, db: Session):
        self.db = db
        self.phytosanitary = PhytosanitaryRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        severity: str | None = None,
        issue_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> PhytosanitaryRecordListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.phytosanitary.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            severity=severity,
            issue_search=issue_search,
            limit=limit,
            offset=offset,
        )
        return PhytosanitaryRecordListResponse(total=total, items=items)

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int, crop_cycle_id: int | None, detected_issue: str, severity: str, action_taken: str, observed_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        record = self.phytosanitary.create(farm_id=farm_id, plot_id=plot_id, crop_cycle_id=crop_cycle_id, detected_issue=detected_issue, severity=severity, action_taken=action_taken, observed_at=observed_at)
        self.audit.add(module='phytosanitary', action='create', user_id=user.id, farm_id=farm_id, record_id=str(record.id))
        self.db.commit(); self.db.refresh(record)
        return record

    def get_for_user(self, *, user: User, record_id: int):
        record = self.phytosanitary.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Registro fitosanitario no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=record.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return record

    def update_for_user(self, *, user: User, record_id: int, detected_issue: str | None, severity: str | None, action_taken: str | None, observed_at: datetime | None):
        record = self.get_for_user(user=user, record_id=record_id)
        updated = self.phytosanitary.update_fields(
            record,
            detected_issue=detected_issue,
            severity=severity,
            action_taken=action_taken,
            observed_at=observed_at,
        )
        self.audit.add(module='phytosanitary', action='update', user_id=user.id, farm_id=record.farm_id, record_id=str(record.id))
        self.db.commit()
        self.db.refresh(updated)
        return updated
