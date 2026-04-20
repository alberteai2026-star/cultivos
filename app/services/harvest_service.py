from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.harvest_repository import HarvestRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class HarvestService:
    def __init__(self, db: Session):
        self.db = db
        self.harvests = HarvestRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        return self.harvests.list_by_farm_ids(farm_ids)

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
