from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.repositories.worker_repository import WorkerRepository
from app.schemas.worker import WorkerListResponse, WorkerTrackingPointListResponse


class WorkerService:
    def __init__(self, db: Session):
        self.db = db
        self.workers = WorkerRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> WorkerListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.workers.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            is_active=is_active,
            search=search,
            limit=limit,
            offset=offset,
        )
        return WorkerListResponse(total=total, items=items)

    def create_for_user(self, *, user: User, farm_id: int, full_name: str, document_id: str | None, role_name: str | None, daily_rate: float | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        worker = self.workers.create(farm_id=farm_id, full_name=full_name, document_id=document_id, role_name=role_name, daily_rate=daily_rate)
        self.audit.add(module='workers', action='create', user_id=user.id, farm_id=farm_id, record_id=str(worker.id))
        self.db.commit(); self.db.refresh(worker)
        return worker

    def get_for_user(self, *, user: User, worker_id: int):
        worker = self.workers.get_by_id(worker_id)
        if not worker:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Trabajador no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=worker.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return worker

    def update_for_user(
        self,
        *,
        user: User,
        worker_id: int,
        full_name: str | None,
        document_id: str | None,
        role_name: str | None,
        daily_rate: float | None,
    ):
        worker = self.get_for_user(user=user, worker_id=worker_id)
        updated = self.workers.update_fields(
            worker,
            full_name=full_name,
            document_id=document_id,
            role_name=role_name,
            daily_rate=daily_rate,
        )
        self.audit.add(module='workers', action='update', user_id=user.id, farm_id=worker.farm_id, record_id=str(worker.id))
        self.db.commit(); self.db.refresh(updated)
        return updated

    def update_status_for_user(self, *, user: User, worker_id: int, is_active: bool):
        worker = self.get_for_user(user=user, worker_id=worker_id)
        worker.is_active = is_active
        self.audit.add(module='workers', action='update_status', user_id=user.id, farm_id=worker.farm_id, record_id=str(worker.id))
        self.db.commit(); self.db.refresh(worker)
        return worker

    def add_tracking_point_for_user(
        self,
        *,
        user: User,
        worker_id: int,
        latitude: float,
        longitude: float,
        speed_kmh: float | None,
        recorded_at: datetime,
        source: str,
        notes: str | None,
    ):
        worker = self.get_for_user(user=user, worker_id=worker_id)
        point = self.workers.create_tracking_point(
            worker_id=worker.id,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            recorded_at=recorded_at,
            source=source,
            notes=notes,
        )
        self.audit.add(module='workers', action='add_tracking_point', user_id=user.id, farm_id=worker.farm_id, record_id=str(point.id))
        self.db.commit(); self.db.refresh(point)
        return point

    def list_tracking_for_user(
        self,
        *,
        user: User,
        worker_id: int,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> WorkerTrackingPointListResponse:
        if recorded_from is not None and recorded_to is not None and recorded_from > recorded_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Rango de fechas inválido')
        worker = self.get_for_user(user=user, worker_id=worker_id)
        total, items = self.workers.list_tracking_points_by_worker_id(
            worker.id,
            recorded_from=recorded_from,
            recorded_to=recorded_to,
            limit=limit,
            offset=offset,
        )
        return WorkerTrackingPointListResponse(total=total, items=items)
