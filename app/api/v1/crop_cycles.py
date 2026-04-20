from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.crop_cycle import CropCycleCreateRequest, CropCycleOut
from app.services.crop_cycle_service import CropCycleService

router = APIRouter()


@router.get('/', response_model=list[CropCycleOut])
def list_crop_cycles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CropCycleService(db)
    return service.list_for_user(user)


@router.post('/', response_model=CropCycleOut, status_code=201)
def create_crop_cycle(
    payload: CropCycleCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CropCycleService(db)
    return service.create_for_user(
        user=user,
        plot_id=payload.plot_id,
        species=payload.species,
        variety=payload.variety,
        sowing_date=payload.sowing_date,
    )
