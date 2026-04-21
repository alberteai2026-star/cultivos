from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.crop_cycle_repository import CropCycleRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.crop_cycle import CropCycleListResponse


class CropCycleService:
    _allowed_status_transitions = {
        'activo': {'cerrado'},
        'cerrado': set(),
    }

    def __init__(self, db: Session):
        self.db = db
        self.cycles = CropCycleRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        species: str | None = None,
        sowing_from: datetime | None = None,
        sowing_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> CropCycleListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro offset debe ser mayor o igual a 0')
        if sowing_from is not None and sowing_to is not None and sowing_from > sowing_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Rango de fechas inválido')

        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        if plot_id is not None:
            plot = self.plots.get_by_id(plot_id)
            if not plot:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')
            if plot.farm_id not in farm_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a este lote')

        total, items = self.cycles.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            status_value=status_value,
            species=species,
            sowing_from=sowing_from,
            sowing_to=sowing_to,
            limit=limit,
            offset=offset,
        )
        return CropCycleListResponse(total=total, items=items)

    def get_for_user(self, *, user: User, cycle_id: int):
        cycle = self.cycles.get_by_id(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ciclo no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=cycle.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return cycle

    def create_for_user(self, *, user: User, plot_id: int, species: str, variety: str | None, sowing_date):
        plot = self.plots.get_by_id(plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')

        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        cycle = self.cycles.create(
            farm_id=plot.farm_id,
            plot_id=plot.id,
            species=species,
            variety=variety,
            sowing_date=sowing_date,
        )

        self.audit.add(
            module='crop_cycles',
            action='create',
            user_id=user.id,
            farm_id=plot.farm_id,
            record_id=str(cycle.id),
            metadata={'plot_id': plot.id, 'species': species},
        )

        self.db.commit()
        self.db.refresh(cycle)
        return cycle

    def update_for_user(
        self,
        *,
        user: User,
        cycle_id: int,
        species: str | None,
        variety: str | None,
        sowing_date: datetime | None,
    ):
        cycle = self.cycles.get_by_id(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ciclo no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=cycle.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        updated = self.cycles.update_fields(cycle, species=species, variety=variety, sowing_date=sowing_date)
        self.audit.add(
            module='crop_cycles',
            action='update',
            user_id=user.id,
            farm_id=cycle.farm_id,
            record_id=str(cycle.id),
            metadata={'species': updated.species, 'status': updated.status},
        )
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def update_status_for_user(self, *, user: User, cycle_id: int, status_value: str):
        cycle = self.cycles.get_by_id(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ciclo no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=cycle.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        current_status = cycle.status
        if current_status != status_value:
            allowed = self._allowed_status_transitions.get(current_status, set())
            if status_value not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Transición de estado inválida: {current_status} -> {status_value}',
                )

        cycle.status = status_value
        self.audit.add(
            module='crop_cycles',
            action='update_status',
            user_id=user.id,
            farm_id=cycle.farm_id,
            record_id=str(cycle.id),
            metadata={'from': current_status, 'to': status_value},
        )
        self.db.commit()
        self.db.refresh(cycle)
        return cycle
