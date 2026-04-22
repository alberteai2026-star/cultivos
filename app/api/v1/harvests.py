from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.harvest import HarvestCreateRequest, HarvestListResponse, HarvestOut, HarvestUpdateRequest
from app.services.harvest_service import HarvestService

router = APIRouter()


@router.get('/', response_model=HarvestListResponse)
def list_harvests(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    crop_cycle_id: int | None = Query(default=None, ge=1),
    harvested_from: datetime | None = Query(default=None),
    harvested_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = HarvestService(db)
    return service.list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        crop_cycle_id=crop_cycle_id,
        harvested_from=harvested_from,
        harvested_to=harvested_to,
        limit=limit,
        offset=offset,
    )


@router.get('/{harvest_id}', response_model=HarvestOut)
def get_harvest(
    harvest_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = HarvestService(db)
    return service.get_for_user(user=user, harvest_id=harvest_id)


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


@router.patch('/{harvest_id}', response_model=HarvestOut)
def update_harvest(
    harvest_id: int,
    payload: HarvestUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = HarvestService(db)
    return service.update_for_user(
        user=user,
        harvest_id=harvest_id,
        harvested_at=payload.harvested_at,
        quantity=payload.quantity,
        unit=payload.unit,
        quality_grade=payload.quality_grade,
        destination=payload.destination,
    )
