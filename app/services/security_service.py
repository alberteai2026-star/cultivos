from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.security_repository import SecurityRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.security import SecurityIncidentListResponse


class SecurityService:
    def __init__(self, db: Session):
        self.db = db
        self.security = SecurityRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def create_for_user(self, *, user: User, farm_id: int, alert_type: str, severity: str, description: str | None, detected_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        incident = self.security.create_incident(
            farm_id=farm_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            detected_at=detected_at,
        )
        self.audit.add(module='security', action='create_incident', user_id=user.id, farm_id=farm_id, record_id=str(incident.id))
        self.db.commit(); self.db.refresh(incident)
        return incident

    def list_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        status_value: str | None = None,
        severity: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> SecurityIncidentListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.security.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            status_value=status_value,
            severity=severity,
            limit=limit,
            offset=offset,
        )
        return SecurityIncidentListResponse(total=total, items=items)

    def get_for_user(self, *, user: User, incident_id: int):
        incident = self.security.get_by_id(incident_id)
        if not incident:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Incidente no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=incident.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return incident

    def update_status_for_user(self, *, user: User, incident_id: int, status_value: str, resolved_at: datetime | None):
        incident = self.get_for_user(user=user, incident_id=incident_id)
        incident.status = status_value
        incident.resolved_at = resolved_at
        self.audit.add(module='security', action='update_incident_status', user_id=user.id, farm_id=incident.farm_id, record_id=str(incident.id))
        self.db.commit(); self.db.refresh(incident)
        return incident
