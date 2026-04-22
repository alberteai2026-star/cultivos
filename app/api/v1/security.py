from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.security import (
    SecurityIncidentCreateRequest,
    SecurityIncidentListResponse,
    SecurityIncidentOut,
    SecurityIncidentStatusUpdateRequest,
)
from app.services.security_service import SecurityService

router = APIRouter()


@router.get('/incidents', response_model=SecurityIncidentListResponse)
def list_security_incidents(
    farm_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    severity: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SecurityService(db).list_for_user(user=user, farm_id=farm_id, status_value=status_value, severity=severity, limit=limit, offset=offset)


@router.post('/incidents', response_model=SecurityIncidentOut, status_code=201)
def create_security_incident(payload: SecurityIncidentCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SecurityService(db).create_for_user(
        user=user,
        farm_id=payload.farm_id,
        alert_type=payload.alert_type,
        severity=payload.severity,
        description=payload.description,
        detected_at=payload.detected_at,
    )


@router.get('/incidents/{incident_id}', response_model=SecurityIncidentOut)
def get_security_incident(incident_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SecurityService(db).get_for_user(user=user, incident_id=incident_id)


@router.patch('/incidents/{incident_id}/status', response_model=SecurityIncidentOut)
def update_security_incident_status(incident_id: int, payload: SecurityIncidentStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SecurityService(db).update_status_for_user(user=user, incident_id=incident_id, status_value=payload.status, resolved_at=payload.resolved_at)
