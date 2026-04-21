from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.nursery import (
    NurseryBatchCreateRequest,
    NurseryBatchListResponse,
    NurseryBatchOut,
    NurseryBatchStatusUpdateRequest,
    NurseryBatchUpdateRequest,
)
from app.services.nursery_service import NurseryService

router = APIRouter()


@router.get('/', response_model=NurseryBatchListResponse)
def list_nursery_batches(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    species_search: str | None = Query(default=None, alias='search'),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NurseryService(db).list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        status_value=status_value,
        species_search=species_search,
        limit=limit,
        offset=offset,
    )


@router.post('/', response_model=NurseryBatchOut, status_code=201)
def create_nursery_batch(payload: NurseryBatchCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NurseryService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, species=payload.species, variety=payload.variety, sowing_date=payload.sowing_date, tray_count=payload.tray_count, status_value=payload.status, notes=payload.notes)


@router.get('/{batch_id}', response_model=NurseryBatchOut)
def get_nursery_batch(batch_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NurseryService(db).get_for_user(user=user, batch_id=batch_id)


@router.patch('/{batch_id}', response_model=NurseryBatchOut)
def update_nursery_batch(batch_id: int, payload: NurseryBatchUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NurseryService(db).update_for_user(
        user=user,
        batch_id=batch_id,
        species=payload.species,
        variety=payload.variety,
        sowing_date=payload.sowing_date,
        tray_count=payload.tray_count,
        notes=payload.notes,
    )


@router.patch('/{batch_id}/status', response_model=NurseryBatchOut)
def update_nursery_batch_status(batch_id: int, payload: NurseryBatchStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NurseryService(db).update_status_for_user(user=user, batch_id=batch_id, status_value=payload.status)
