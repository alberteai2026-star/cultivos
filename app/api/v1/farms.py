from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.farm import FarmCreateRequest, FarmListResponse, FarmOut, FarmUpdateRequest
from app.services.farm_service import FarmService

router = APIRouter()


@router.get('/', response_model=FarmListResponse)
def list_farms(
    search: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FarmService(db)
    return service.list_for_user(user, search=search, limit=limit, offset=offset)


@router.get('/{farm_id}', response_model=FarmOut)
def get_farm(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FarmService(db)
    return service.get_for_user(user=user, farm_id=farm_id)


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


@router.patch('/{farm_id}', response_model=FarmOut)
def update_farm(
    farm_id: int,
    payload: FarmUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FarmService(db)
    return service.update_for_user(
        user=user,
        farm_id=farm_id,
        name=payload.name,
        total_area_ha=payload.total_area_ha,
        department=payload.department,
        municipality=payload.municipality,
    )
