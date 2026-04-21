from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.crop_cycle import (
    CropCycleCreateRequest,
    CropCycleListResponse,
    CropCycleOut,
    CropCycleStatusUpdateRequest,
    CropCycleUpdateRequest,
)
from app.services.crop_cycle_service import CropCycleService

router = APIRouter()


@router.get('/', response_model=CropCycleListResponse)
def list_crop_cycles(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    species: str | None = Query(default=None),
    sowing_from: datetime | None = Query(default=None),
    sowing_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CropCycleService(db)
    return service.list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        status_value=status_value,
        species=species,
        sowing_from=sowing_from,
        sowing_to=sowing_to,
        limit=limit,
        offset=offset,
    )


@router.get('/{cycle_id}', response_model=CropCycleOut)
def get_crop_cycle(
    cycle_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CropCycleService(db)
    return service.get_for_user(user=user, cycle_id=cycle_id)


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


@router.patch('/{cycle_id}', response_model=CropCycleOut)
def update_crop_cycle(
    cycle_id: int,
    payload: CropCycleUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CropCycleService(db)
    return service.update_for_user(
        user=user,
        cycle_id=cycle_id,
        species=payload.species,
        variety=payload.variety,
        sowing_date=payload.sowing_date,
    )


@router.patch('/{cycle_id}/status', response_model=CropCycleOut)
def update_crop_cycle_status(
    cycle_id: int,
    payload: CropCycleStatusUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CropCycleService(db)
    return service.update_status_for_user(user=user, cycle_id=cycle_id, status_value=payload.status)
