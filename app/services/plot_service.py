from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.plot import PlotListResponse


class PlotService:
    def __init__(self, db: Session):
        self.db = db
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        search: str | None = None,
        status_value: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> PlotListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro offset debe ser mayor o igual a 0')

        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        total, items = self.plots.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            search=search,
            status_value=status_value,
            limit=limit,
            offset=offset,
        )
        return PlotListResponse(total=total, items=items)

    def get_for_user(self, *, user: User, plot_id: int):
        plot = self.plots.get_by_id(plot_id)
        if plot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a este lote')
        return plot

    def create_for_user(
        self,
        *,
        user: User,
        farm_id: int,
        code: str,
        name: str,
        area_ha: float | None,
        soil_type: str | None,
        status_value: str,
    ):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='No tienes acceso a esta finca',
            )

        existing = self.plots.get_by_code_in_farm(farm_id=farm_id, code=code)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Ya existe un lote con ese código en la finca')

        plot = self.plots.create(
            farm_id=farm_id,
            code=code,
            name=name,
            area_ha=area_ha,
            soil_type=soil_type,
            status=status_value,
        )

        self.audit.add(
            module='plots',
            action='create',
            user_id=user.id,
            farm_id=farm_id,
            record_id=str(plot.id),
            metadata={'code': plot.code, 'name': plot.name},
        )

        self.db.commit()
        self.db.refresh(plot)
        return plot

    def update_for_user(
        self,
        *,
        user: User,
        plot_id: int,
        code: str | None,
        name: str | None,
        area_ha: float | None,
        soil_type: str | None,
        status_value: str | None,
    ):
        plot = self.plots.get_by_id(plot_id)
        if plot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')

        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a este lote')

        if code is not None and code != plot.code:
            existing = self.plots.get_by_code_in_farm(farm_id=plot.farm_id, code=code)
            if existing is not None and existing.id != plot.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Ya existe un lote con ese código en la finca')

        updated = self.plots.update(
            plot,
            code=code,
            name=name,
            area_ha=area_ha,
            soil_type=soil_type,
            status=status_value,
        )

        self.audit.add(
            module='plots',
            action='update',
            user_id=user.id,
            farm_id=plot.farm_id,
            record_id=str(plot.id),
            metadata={'code': updated.code, 'name': updated.name},
        )

        self.db.commit()
        self.db.refresh(updated)
        return updated
