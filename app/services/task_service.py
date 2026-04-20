from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        return self.tasks.list_by_farm_ids(farm_ids)

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

    def update_status_for_user(self, *, user: User, task_id: int, status_value: str):
        task = self.tasks.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Labor no encontrada')

        if not self.relations.user_has_farm(user_id=user.id, farm_id=task.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        task.status = status_value
        self.audit.add(
            module='tasks',
            action='update_status',
            user_id=user.id,
            farm_id=task.farm_id,
            record_id=str(task.id),
            metadata={'status': status_value},
        )
        self.db.commit()
        self.db.refresh(task)
        return task
