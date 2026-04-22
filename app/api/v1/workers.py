from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.worker import (
    WorkerCreateRequest,
    WorkerListResponse,
    WorkerOut,
    WorkerStatusUpdateRequest,
    WorkerTrackingPointCreateRequest,
    WorkerTrackingPointListResponse,
    WorkerTrackingPointOut,
    WorkerUpdateRequest,
)
from app.services.worker_service import WorkerService

router = APIRouter()


@router.get('/', response_model=WorkerListResponse)
def list_workers(
    farm_id: int | None = Query(default=None, ge=1),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WorkerService(db).list_for_user(user, farm_id=farm_id, is_active=is_active, search=search, limit=limit, offset=offset)


@router.post('/', response_model=WorkerOut, status_code=201)
def create_worker(payload: WorkerCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkerService(db).create_for_user(user=user, farm_id=payload.farm_id, full_name=payload.full_name, document_id=payload.document_id, role_name=payload.role_name, daily_rate=payload.daily_rate)


@router.get('/{worker_id}', response_model=WorkerOut)
def get_worker(worker_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkerService(db).get_for_user(user=user, worker_id=worker_id)


@router.patch('/{worker_id}', response_model=WorkerOut)
def update_worker(worker_id: int, payload: WorkerUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkerService(db).update_for_user(
        user=user,
        worker_id=worker_id,
        full_name=payload.full_name,
        document_id=payload.document_id,
        role_name=payload.role_name,
        daily_rate=payload.daily_rate,
    )


@router.patch('/{worker_id}/status', response_model=WorkerOut)
def update_worker_status(worker_id: int, payload: WorkerStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkerService(db).update_status_for_user(user=user, worker_id=worker_id, is_active=payload.is_active)


@router.post('/{worker_id}/tracking', response_model=WorkerTrackingPointOut, status_code=201)
def create_worker_tracking_point(worker_id: int, payload: WorkerTrackingPointCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkerService(db).add_tracking_point_for_user(
        user=user,
        worker_id=worker_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        speed_kmh=payload.speed_kmh,
        recorded_at=payload.recorded_at,
        source=payload.source,
        notes=payload.notes,
    )


@router.get('/{worker_id}/tracking', response_model=WorkerTrackingPointListResponse)
def list_worker_tracking_points(
    worker_id: int,
    recorded_from: datetime | None = Query(default=None),
    recorded_to: datetime | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WorkerService(db).list_tracking_for_user(
        user=user,
        worker_id=worker_id,
        recorded_from=recorded_from,
        recorded_to=recorded_to,
        limit=limit,
        offset=offset,
    )
