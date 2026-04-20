from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.harvest import HarvestCreateRequest, HarvestOut
from app.services.harvest_service import HarvestService

router = APIRouter()


@router.get('/', response_model=list[HarvestOut])
def list_harvests(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = HarvestService(db)
    return service.list_for_user(user)


@router.post('/', response_model=HarvestOut, status_code=201)
def create_harvest(
    payload: HarvestCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = HarvestService(db)
    return service.create_for_user(
        user=user,
        plot_id=payload.plot_id,
        crop_cycle_id=payload.crop_cycle_id,
        harvested_at=payload.harvested_at,
        quantity=payload.quantity,
        unit=payload.unit,
        quality_grade=payload.quality_grade,
        destination=payload.destination,
    )
