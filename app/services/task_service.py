from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.task import TaskListResponse


class TaskService:
    _allowed_status_transitions = {
        'programada': {'en_progreso', 'cancelada'},
        'en_progreso': {'completada', 'cancelada'},
        'completada': set(),
        'cancelada': set(),
    }

    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        search: str | None = None,
        planned_from: datetime | None = None,
        planned_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> TaskListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro offset debe ser mayor o igual a 0')
        if planned_from is not None and planned_to is not None and planned_from > planned_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Rango de fechas inválido')

        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        if plot_id is not None:
            plot = self.plots.get_by_id(plot_id)
            if plot is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')
            if plot.farm_id not in farm_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a este lote')

        total, items = self.tasks.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            status_value=status_value,
            search=search,
            planned_from=planned_from,
            planned_to=planned_to,
            limit=limit,
            offset=offset,
        )
        return TaskListResponse(total=total, items=items)

    def get_for_user(self, *, user: User, task_id: int):
        task = self.tasks.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Labor no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=task.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return task

    def create_for_user(
        self,
        *,
        user: User,
        plot_id: int,
        crop_cycle_id: int | None,
        task_type: str,
        title: str,
        planned_date,
        notes: str | None,
    ):
        plot = self.plots.get_by_id(plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')

        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        task = self.tasks.create(
            farm_id=plot.farm_id,
            plot_id=plot.id,
            crop_cycle_id=crop_cycle_id,
            task_type=task_type,
            title=title,
            planned_date=planned_date,
            notes=notes,
        )

        self.audit.add(
            module='tasks',
            action='create',
            user_id=user.id,
            farm_id=plot.farm_id,
            record_id=str(task.id),
            metadata={'plot_id': plot.id, 'task_type': task.task_type},
        )

        self.db.commit()
        self.db.refresh(task)
        return task

    def update_for_user(
        self,
        *,
        user: User,
        task_id: int,
        task_type: str | None,
        title: str | None,
        planned_date: datetime | None,
        notes: str | None,
    ):
        task = self.tasks.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Labor no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=task.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        updated = self.tasks.update_fields(
            task,
            task_type=task_type,
            title=title,
            planned_date=planned_date,
            notes=notes,
        )
        self.audit.add(
            module='tasks',
            action='update',
            user_id=user.id,
            farm_id=task.farm_id,
            record_id=str(task.id),
            metadata={'task_type': updated.task_type, 'title': updated.title},
        )
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def update_status_for_user(self, *, user: User, task_id: int, status_value: str):
        task = self.tasks.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Labor no encontrada')

        if not self.relations.user_has_farm(user_id=user.id, farm_id=task.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        current_status = task.status
        if current_status != status_value:
            allowed_next = self._allowed_status_transitions.get(current_status, set())
            if status_value not in allowed_next:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Transición de estado inválida: {current_status} -> {status_value}",
                )

        task.status = status_value
        self.audit.add(
            module='tasks',
            action='update_status',
            user_id=user.id,
            farm_id=task.farm_id,
            record_id=str(task.id),
            metadata={'from': current_status, 'to': status_value},
        )
        self.db.commit()
        self.db.refresh(task)
        return task
