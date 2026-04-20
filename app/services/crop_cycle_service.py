from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.crop_cycle_repository import CropCycleRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class CropCycleService:
    def __init__(self, db: Session):
        self.db = db
        self.cycles = CropCycleRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        return self.cycles.list_by_farm_ids(farm_ids)

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
