from sqlalchemy import select
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

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[Task]:
        if not farm_ids:
            return []
        query = select(Task).where(Task.farm_id.in_(farm_ids)).order_by(Task.id.desc())
        return list(self.db.scalars(query).all())

    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)
