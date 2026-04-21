from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.irrigation import (
    IrrigationEventCreateRequest,
    IrrigationEventListResponse,
    IrrigationEventOut,
    IrrigationEventUpdateRequest,
    IrrigationStatusUpdateRequest,
)
from app.services.irrigation_service import IrrigationService

router = APIRouter()


@router.get('/events', response_model=IrrigationEventListResponse)
def list_irrigation_events(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    scheduled_from: datetime | None = Query(default=None),
    scheduled_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IrrigationService(db).list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        status_value=status_value,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        limit=limit,
        offset=offset,
    )


@router.post('/events', response_model=IrrigationEventOut, status_code=201)
def create_irrigation_event(payload: IrrigationEventCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IrrigationService(db).create_for_user(user=user, plot_id=payload.plot_id, scheduled_at=payload.scheduled_at, applied_mm=payload.applied_mm, cost=payload.cost)


@router.get('/events/{event_id}', response_model=IrrigationEventOut)
def get_irrigation_event(event_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IrrigationService(db).get_for_user(user=user, event_id=event_id)


@router.patch('/events/{event_id}', response_model=IrrigationEventOut)
def update_irrigation_event(event_id: int, payload: IrrigationEventUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IrrigationService(db).update_for_user(
        user=user,
        event_id=event_id,
        scheduled_at=payload.scheduled_at,
        applied_mm=payload.applied_mm,
        cost=payload.cost,
    )


@router.patch('/events/{event_id}/status', response_model=IrrigationEventOut)
def update_irrigation_event_status(event_id: int, payload: IrrigationStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IrrigationService(db).update_status_for_user(user=user, event_id=event_id, status_value=payload.status)
