from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.rotation import RotationPlanCreateRequest, RotationPlanOut
from app.services.rotation_service import RotationService

router = APIRouter()


@router.get('/plans', response_model=list[RotationPlanOut])
def list_rotation_plans(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RotationService(db).list_for_user(user)


@router.post('/plans', response_model=RotationPlanOut, status_code=201)
def create_rotation_plan(payload: RotationPlanCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RotationService(db).create_for_user(user=user, plot_id=payload.plot_id, next_species=payload.next_species, recommendation=payload.recommendation)
