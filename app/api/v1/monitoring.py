from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.monitoring import (
    MonitoringVisitCreateRequest,
    MonitoringVisitListResponse,
    MonitoringVisitOut,
    MonitoringVisitUpdateRequest,
)
from app.services.monitoring_service import MonitoringService

router = APIRouter()


@router.get('/visits', response_model=MonitoringVisitListResponse)
def list_monitoring_visits(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    crop_cycle_id: int | None = Query(default=None, ge=1),
    issue_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    observed_from: datetime | None = Query(default=None),
    observed_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringService(db)
    return service.list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        crop_cycle_id=crop_cycle_id,
        issue_type=issue_type,
        severity=severity,
        observed_from=observed_from,
        observed_to=observed_to,
        limit=limit,
        offset=offset,
    )


@router.get('/visits/{visit_id}', response_model=MonitoringVisitOut)
def get_monitoring_visit(
    visit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringService(db)
    return service.get_for_user(user=user, visit_id=visit_id)


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


@router.patch('/visits/{visit_id}', response_model=MonitoringVisitOut)
def update_monitoring_visit(
    visit_id: int,
    payload: MonitoringVisitUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringService(db)
    return service.update_for_user(
        user=user,
        visit_id=visit_id,
        observed_at=payload.observed_at,
        bbch_stage=payload.bbch_stage,
        issue_type=payload.issue_type,
        severity=payload.severity,
        notes=payload.notes,
    )
