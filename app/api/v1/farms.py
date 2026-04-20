from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.farm import FarmCreateRequest, FarmOut
from app.services.farm_service import FarmService

router = APIRouter()


@router.get('/', response_model=list[FarmOut])
def list_farms(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FarmService(db)
    return service.list_for_user(user)


@router.post('/', response_model=FarmOut, status_code=201)
def create_farm(
    payload: FarmCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FarmService(db)
    return service.create_for_owner(
        user=user,
        name=payload.name,
        total_area_ha=payload.total_area_ha,
        department=payload.department,
        municipality=payload.municipality,
    )
