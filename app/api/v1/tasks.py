from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskCreateRequest, TaskListResponse, TaskOut, TaskStatusUpdateRequest, TaskUpdateRequest
from app.services.task_service import TaskService

router = APIRouter()


@router.get('/', response_model=TaskListResponse)
def list_tasks(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    search: str | None = Query(default=None),
    planned_from: datetime | None = Query(default=None),
    planned_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    return service.list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        status_value=status_value,
        search=search,
        planned_from=planned_from,
        planned_to=planned_to,
        limit=limit,
        offset=offset,
    )


@router.get('/{task_id}', response_model=TaskOut)
def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    return service.get_for_user(user=user, task_id=task_id)


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


@router.patch('/{task_id}', response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    return service.update_for_user(
        user=user,
        task_id=task_id,
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
