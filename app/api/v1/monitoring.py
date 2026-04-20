from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.monitoring import MonitoringVisitCreateRequest, MonitoringVisitOut
from app.services.monitoring_service import MonitoringService

router = APIRouter()


@router.get('/visits', response_model=list[MonitoringVisitOut])
def list_monitoring_visits(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringService(db)
    return service.list_for_user(user)


@router.post('/visits', response_model=MonitoringVisitOut, status_code=201)
def create_monitoring_visit(
    payload: MonitoringVisitCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringService(db)
    return service.create_for_user(
        user=user,
        plot_id=payload.plot_id,
        crop_cycle_id=payload.crop_cycle_id,
        observed_at=payload.observed_at,
        bbch_stage=payload.bbch_stage,
        issue_type=payload.issue_type,
        severity=payload.severity,
        notes=payload.notes,
    )
