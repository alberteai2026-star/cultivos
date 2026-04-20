from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardKPIOut, DashboardSnapshotCreateRequest, DashboardSnapshotOut
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get('/kpis', response_model=DashboardKPIOut)
def get_dashboard_kpis(farm_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_kpis_for_user(user=user, farm_id=farm_id)


@router.post('/snapshots', response_model=DashboardSnapshotOut, status_code=201)
def create_dashboard_snapshot(payload: DashboardSnapshotCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).create_snapshot_for_user(user=user, farm_id=payload.farm_id, captured_at=payload.captured_at)


@router.get('/snapshots', response_model=list[DashboardSnapshotOut])
def list_dashboard_snapshots(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).list_snapshots_for_user(user)
