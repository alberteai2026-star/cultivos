from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.rotation import RotationPlanCreateRequest, RotationPlanListResponse, RotationPlanOut, RotationPlanStatusUpdateRequest, RotationPlanUpdateRequest
from app.services.rotation_service import RotationService

router = APIRouter()


@router.get('/plans', response_model=RotationPlanListResponse)
def list_rotation_plans(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    search: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RotationService(db).list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        status_value=status_value,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.post('/plans', response_model=RotationPlanOut, status_code=201)
def create_rotation_plan(payload: RotationPlanCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RotationService(db).create_for_user(user=user, plot_id=payload.plot_id, next_species=payload.next_species, recommendation=payload.recommendation)


@router.get('/plans/{plan_id}', response_model=RotationPlanOut)
def get_rotation_plan(plan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RotationService(db).get_for_user(user=user, plan_id=plan_id)


@router.patch('/plans/{plan_id}', response_model=RotationPlanOut)
def update_rotation_plan(plan_id: int, payload: RotationPlanUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RotationService(db).update_for_user(user=user, plan_id=plan_id, next_species=payload.next_species, recommendation=payload.recommendation)


@router.patch('/plans/{plan_id}/status', response_model=RotationPlanOut)
def update_rotation_plan_status(plan_id: int, payload: RotationPlanStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RotationService(db).update_status_for_user(user=user, plan_id=plan_id, status_value=payload.status)
