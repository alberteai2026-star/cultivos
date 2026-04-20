from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.irrigation_repository import IrrigationRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class IrrigationService:
    def __init__(self, db: Session):
        self.db = db
        self.irrigation = IrrigationRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.irrigation.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, plot_id: int, scheduled_at, applied_mm: float | None, cost: float | None):
        plot = self.plots.get_by_id(plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        event = self.irrigation.create(farm_id=plot.farm_id, plot_id=plot.id, scheduled_at=scheduled_at, applied_mm=applied_mm, cost=cost)
        self.audit.add(module='irrigation', action='create', user_id=user.id, farm_id=plot.farm_id, record_id=str(event.id))
        self.db.commit(); self.db.refresh(event)
        return event
