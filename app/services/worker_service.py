from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.repositories.worker_repository import WorkerRepository


class WorkerService:
    def __init__(self, db: Session):
        self.db = db
        self.workers = WorkerRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.workers.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, farm_id: int, full_name: str, document_id: str | None, role_name: str | None, daily_rate: float | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        worker = self.workers.create(farm_id=farm_id, full_name=full_name, document_id=document_id, role_name=role_name, daily_rate=daily_rate)
        self.audit.add(module='workers', action='create', user_id=user.id, farm_id=farm_id, record_id=str(worker.id))
        self.db.commit(); self.db.refresh(worker)
        return worker
