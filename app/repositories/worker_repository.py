from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.worker import Worker
from app.models.worker_tracking_point import WorkerTrackingPoint


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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[Worker]]:
        if not farm_ids:
            return 0, []
        q = select(Worker).where(Worker.farm_id.in_(farm_ids))
        count_q = select(func.count(Worker.id)).where(Worker.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(Worker.farm_id == farm_id)
            count_q = count_q.where(Worker.farm_id == farm_id)
        if is_active is not None:
            q = q.where(Worker.is_active == is_active)
            count_q = count_q.where(Worker.is_active == is_active)
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where(Worker.full_name.ilike(pattern))
            count_q = count_q.where(Worker.full_name.ilike(pattern))
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(Worker.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, worker_id: int) -> Worker | None:
        return self.db.get(Worker, worker_id)

    def update_fields(
        self,
        worker: Worker,
        *,
        full_name: str | None,
        document_id: str | None,
        role_name: str | None,
        daily_rate: float | None,
    ) -> Worker:
        if full_name is not None:
            worker.full_name = full_name
        worker.document_id = document_id
        worker.role_name = role_name
        worker.daily_rate = daily_rate
        self.db.flush()
        return worker

    def create_tracking_point(
        self,
        *,
        worker_id: int,
        latitude: float,
        longitude: float,
        speed_kmh: float | None,
        recorded_at: datetime,
        source: str,
        notes: str | None,
    ) -> WorkerTrackingPoint:
        point = WorkerTrackingPoint(
            worker_id=worker_id,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            recorded_at=recorded_at,
            source=source,
            notes=notes,
        )
        self.db.add(point)
        self.db.flush()
        return point

    def list_tracking_points_by_worker_id(
        self,
        worker_id: int,
        *,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[int, list[WorkerTrackingPoint]]:
        q = select(WorkerTrackingPoint).where(WorkerTrackingPoint.worker_id == worker_id)
        count_q = select(func.count(WorkerTrackingPoint.id)).where(WorkerTrackingPoint.worker_id == worker_id)
        if recorded_from is not None:
            q = q.where(WorkerTrackingPoint.recorded_at >= recorded_from)
            count_q = count_q.where(WorkerTrackingPoint.recorded_at >= recorded_from)
        if recorded_to is not None:
            q = q.where(WorkerTrackingPoint.recorded_at <= recorded_to)
            count_q = count_q.where(WorkerTrackingPoint.recorded_at <= recorded_to)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(WorkerTrackingPoint.recorded_at.desc(), WorkerTrackingPoint.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())
