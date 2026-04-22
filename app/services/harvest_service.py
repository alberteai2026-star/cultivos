from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.harvest_repository import HarvestRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.harvest import HarvestListResponse


class HarvestService:
    def __init__(self, db: Session):
        self.db = db
        self.harvests = HarvestRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        crop_cycle_id: int | None = None,
        harvested_from: datetime | None = None,
        harvested_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> HarvestListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro offset debe ser mayor o igual a 0')
        if harvested_from is not None and harvested_to is not None and harvested_from > harvested_to:
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

        total, items = self.harvests.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            harvested_from=harvested_from,
            harvested_to=harvested_to,
            limit=limit,
            offset=offset,
        )
        return HarvestListResponse(total=total, items=items)

    def get_for_user(self, *, user: User, harvest_id: int):
        harvest = self.harvests.get_by_id(harvest_id)
        if not harvest:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cosecha no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=harvest.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return harvest

    def create_for_user(
        self,
        *,
        user: User,
        plot_id: int,
        crop_cycle_id: int | None,
        harvested_at,
        quantity: float,
        unit: str,
        quality_grade: str | None,
        destination: str | None,
    ):
        plot = self.plots.get_by_id(plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')

        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        harvest = self.harvests.create(
            farm_id=plot.farm_id,
            plot_id=plot.id,
            crop_cycle_id=crop_cycle_id,
            harvested_at=harvested_at,
            quantity=quantity,
            unit=unit,
            quality_grade=quality_grade,
            destination=destination,
        )

        self.audit.add(
            module='harvests',
            action='create',
            user_id=user.id,
            farm_id=plot.farm_id,
            record_id=str(harvest.id),
            metadata={'plot_id': plot.id, 'quantity': quantity, 'unit': unit},
        )

        self.db.commit()
        self.db.refresh(harvest)
        return harvest

    def update_for_user(
        self,
        *,
        user: User,
        harvest_id: int,
        harvested_at: datetime | None,
        quantity: float | None,
        unit: str | None,
        quality_grade: str | None,
        destination: str | None,
    ):
        harvest = self.harvests.get_by_id(harvest_id)
        if not harvest:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cosecha no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=harvest.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        updated = self.harvests.update_fields(
            harvest,
            harvested_at=harvested_at,
            quantity=quantity,
            unit=unit,
            quality_grade=quality_grade,
            destination=destination,
        )
        self.audit.add(
            module='harvests',
            action='update',
            user_id=user.id,
            farm_id=harvest.farm_id,
            record_id=str(harvest.id),
            metadata={'quantity': updated.quantity, 'unit': updated.unit, 'quality_grade': updated.quality_grade},
        )
        self.db.commit()
        self.db.refresh(updated)
        return updated
