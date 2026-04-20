from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.worker import WorkerCreateRequest, WorkerOut
from app.services.worker_service import WorkerService

router = APIRouter()


@router.get('/', response_model=list[WorkerOut])
def list_workers(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkerService(db).list_for_user(user)


@router.post('/', response_model=WorkerOut, status_code=201)
def create_worker(payload: WorkerCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkerService(db).create_for_user(user=user, farm_id=payload.farm_id, full_name=payload.full_name, document_id=payload.document_id, role_name=payload.role_name, daily_rate=payload.daily_rate)
