from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.nursery_repository import NurseryRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.nursery import NurseryBatchListResponse


class NurseryService:
    def __init__(self, db: Session):
        self.db = db
        self.nursery = NurseryRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        species_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> NurseryBatchListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.nursery.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            status_value=status_value,
            species_search=species_search,
            limit=limit,
            offset=offset,
        )
        return NurseryBatchListResponse(total=total, items=items)

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int | None, species: str, variety: str | None, sowing_date: datetime, tray_count: int, status_value: str, notes: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        batch = self.nursery.create(farm_id=farm_id, plot_id=plot_id, species=species, variety=variety, sowing_date=sowing_date, tray_count=tray_count, status=status_value, notes=notes)
        self.audit.add(module='nursery', action='create', user_id=user.id, farm_id=farm_id, record_id=str(batch.id))
        self.db.commit(); self.db.refresh(batch)
        return batch

    def get_for_user(self, *, user: User, batch_id: int):
        batch = self.nursery.get_by_id(batch_id)
        if not batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote de vivero no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=batch.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return batch

    def update_for_user(self, *, user: User, batch_id: int, species: str | None, variety: str | None, sowing_date: datetime | None, tray_count: int | None, notes: str | None):
        batch = self.get_for_user(user=user, batch_id=batch_id)
        updated = self.nursery.update_fields(batch, species=species, variety=variety, sowing_date=sowing_date, tray_count=tray_count, notes=notes)
        self.audit.add(module='nursery', action='update', user_id=user.id, farm_id=batch.farm_id, record_id=str(batch.id))
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def update_status_for_user(self, *, user: User, batch_id: int, status_value: str):
        batch = self.get_for_user(user=user, batch_id=batch_id)
        batch.status = status_value
        self.audit.add(module='nursery', action='update_status', user_id=user.id, farm_id=batch.farm_id, record_id=str(batch.id))
        self.db.commit()
        self.db.refresh(batch)
        return batch
