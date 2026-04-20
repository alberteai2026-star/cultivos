from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.irrigation import IrrigationEventCreateRequest, IrrigationEventOut
from app.services.irrigation_service import IrrigationService

router = APIRouter()


@router.get('/events', response_model=list[IrrigationEventOut])
def list_irrigation_events(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IrrigationService(db).list_for_user(user)


@router.post('/events', response_model=IrrigationEventOut, status_code=201)
def create_irrigation_event(payload: IrrigationEventCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IrrigationService(db).create_for_user(user=user, plot_id=payload.plot_id, scheduled_at=payload.scheduled_at, applied_mm=payload.applied_mm, cost=payload.cost)
