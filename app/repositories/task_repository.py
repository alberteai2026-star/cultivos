from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        farm_id: int,
        plot_id: int,
        crop_cycle_id: int | None,
        task_type: str,
        title: str,
        planned_date,
        notes: str | None,
    ) -> Task:
        task = Task(
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            task_type=task_type,
            title=title,
            planned_date=planned_date,
            status='programada',
            notes=notes,
        )
        self.db.add(task)
        self.db.flush()
        return task

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        search: str | None = None,
        planned_from: datetime | None = None,
        planned_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[Task]]:
        if not farm_ids:
            return 0, []

        q = select(Task).where(Task.farm_id.in_(farm_ids))
        count_q = select(func.count(Task.id)).where(Task.farm_id.in_(farm_ids))

        if farm_id is not None:
            q = q.where(Task.farm_id == farm_id)
            count_q = count_q.where(Task.farm_id == farm_id)
        if plot_id is not None:
            q = q.where(Task.plot_id == plot_id)
            count_q = count_q.where(Task.plot_id == plot_id)
        if status_value is not None:
            q = q.where(Task.status == status_value)
            count_q = count_q.where(Task.status == status_value)
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where((Task.title.ilike(pattern)) | (Task.task_type.ilike(pattern)))
            count_q = count_q.where((Task.title.ilike(pattern)) | (Task.task_type.ilike(pattern)))
        if planned_from is not None:
            q = q.where(Task.planned_date >= planned_from)
            count_q = count_q.where(Task.planned_date >= planned_from)
        if planned_to is not None:
            q = q.where(Task.planned_date <= planned_to)
            count_q = count_q.where(Task.planned_date <= planned_to)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(Task.planned_date.desc(), Task.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def update_fields(
        self,
        task: Task,
        *,
        task_type: str | None,
        title: str | None,
        planned_date: datetime | None,
        notes: str | None,
    ) -> Task:
        if task_type is not None:
            task.task_type = task_type
        if title is not None:
            task.title = title
        if planned_date is not None:
            task.planned_date = planned_date
        task.notes = notes
        self.db.flush()
        return task
