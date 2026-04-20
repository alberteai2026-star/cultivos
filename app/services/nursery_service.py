from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.nursery_repository import NurseryRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class NurseryService:
    def __init__(self, db: Session):
        self.db = db
        self.nursery = NurseryRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.nursery.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int | None, species: str, variety: str | None, sowing_date: datetime, tray_count: int, status_value: str, notes: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        batch = self.nursery.create(farm_id=farm_id, plot_id=plot_id, species=species, variety=variety, sowing_date=sowing_date, tray_count=tray_count, status=status_value, notes=notes)
        self.audit.add(module='nursery', action='create', user_id=user.id, farm_id=farm_id, record_id=str(batch.id))
        self.db.commit(); self.db.refresh(batch)
        return batch
