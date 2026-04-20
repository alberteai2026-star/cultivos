from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskCreateRequest, TaskOut, TaskStatusUpdateRequest
from app.services.task_service import TaskService

router = APIRouter()


@router.get('/', response_model=list[TaskOut])
def list_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    return service.list_for_user(user)


@router.post('/', response_model=TaskOut, status_code=201)
def create_task(
    payload: TaskCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    return service.create_for_user(
        user=user,
        plot_id=payload.plot_id,
        crop_cycle_id=payload.crop_cycle_id,
        task_type=payload.task_type,
        title=payload.title,
        planned_date=payload.planned_date,
        notes=payload.notes,
    )


@router.patch('/{task_id}/status', response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    return service.update_status_for_user(user=user, task_id=task_id, status_value=payload.status)
