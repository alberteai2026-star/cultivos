from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.worker import Worker


class WorkerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, farm_id: int, full_name: str, document_id: str | None, role_name: str | None, daily_rate: float | None) -> Worker:
        worker = Worker(
            farm_id=farm_id,
            full_name=full_name,
            document_id=document_id,
            role_name=role_name,
            daily_rate=daily_rate,
            is_active=True,
        )
        self.db.add(worker)
        self.db.flush()
        return worker

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[Worker]:
        if not farm_ids:
            return []
        q = select(Worker).where(Worker.farm_id.in_(farm_ids)).order_by(Worker.id.desc())
        return list(self.db.scalars(q).all())
