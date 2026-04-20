from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.nursery import NurseryBatchCreateRequest, NurseryBatchOut
from app.services.nursery_service import NurseryService

router = APIRouter()


@router.get('/', response_model=list[NurseryBatchOut])
def list_nursery_batches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NurseryService(db).list_for_user(user)


@router.post('/', response_model=NurseryBatchOut, status_code=201)
def create_nursery_batch(payload: NurseryBatchCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NurseryService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, species=payload.species, variety=payload.variety, sowing_date=payload.sowing_date, tray_count=payload.tray_count, status_value=payload.status, notes=payload.notes)
