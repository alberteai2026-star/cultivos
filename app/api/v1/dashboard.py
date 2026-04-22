from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import (
    DashboardAlertListResponse,
    DashboardGoalCreateRequest,
    DashboardGoalListResponse,
    DashboardGoalOut,
    DashboardGoalUpdateRequest,
    DashboardKPICompareResponse,
    DashboardKPIOut,
    DashboardSnapshotCreateRequest,
    DashboardSnapshotListResponse,
    DashboardSnapshotOut,
)
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get('/kpis', response_model=DashboardKPIOut)
def get_dashboard_kpis(farm_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_kpis_for_user(user=user, farm_id=farm_id)


@router.get('/kpis/compare', response_model=DashboardKPICompareResponse)
def compare_dashboard_kpis(
    farm_ids: list[int] = Query(..., min_length=2, max_length=5),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return DashboardService(db).compare_kpis_for_user(user=user, farm_ids=farm_ids)


@router.post('/snapshots', response_model=DashboardSnapshotOut, status_code=201)
def create_dashboard_snapshot(payload: DashboardSnapshotCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).create_snapshot_for_user(user=user, farm_id=payload.farm_id, captured_at=payload.captured_at)


@router.get('/snapshots', response_model=DashboardSnapshotListResponse)
def list_dashboard_snapshots(
    farm_id: int | None = Query(default=None, ge=1),
    captured_from: datetime | None = None,
    captured_to: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return DashboardService(db).list_snapshots_for_user(
        user,
        farm_id=farm_id,
        captured_from=captured_from,
        captured_to=captured_to,
        limit=limit,
        offset=offset,
    )


@router.get('/snapshots/{snapshot_id}', response_model=DashboardSnapshotOut)
def get_dashboard_snapshot(snapshot_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_snapshot_for_user(user=user, snapshot_id=snapshot_id)


@router.get('/goals', response_model=DashboardGoalListResponse)
def list_dashboard_goals(
    farm_id: int | None = Query(default=None, ge=1),
    status: str | None = Query(default=None),
    kpi_key: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return DashboardService(db).list_goals_for_user(
        user,
        farm_id=farm_id,
        status_filter=status,
        kpi_key=kpi_key,
        limit=limit,
        offset=offset,
    )


@router.post('/goals', response_model=DashboardGoalOut, status_code=201)
def create_dashboard_goal(payload: DashboardGoalCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).create_goal_for_user(
        user=user,
        farm_id=payload.farm_id,
        kpi_key=payload.kpi_key,
        target_value=payload.target_value,
        period_label=payload.period_label,
    )


@router.patch('/goals/{goal_id}', response_model=DashboardGoalOut)
def update_dashboard_goal(goal_id: int, payload: DashboardGoalUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).update_goal_for_user(
        user=user,
        goal_id=goal_id,
        target_value=payload.target_value,
        period_label=payload.period_label,
        status_value=payload.status,
    )


@router.get('/alerts', response_model=DashboardAlertListResponse)
def list_dashboard_alerts(
    farm_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return DashboardService(db).list_alerts_for_user(user=user, farm_id=farm_id, limit=limit, offset=offset)
