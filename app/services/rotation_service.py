from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.rotation_repository import RotationRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class RotationService:
    def __init__(self, db: Session):
        self.db = db
        self.rotation = RotationRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.rotation.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, plot_id: int, next_species: str, recommendation: str | None):
        plot = self.plots.get_by_id(plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        plan = self.rotation.create(farm_id=plot.farm_id, plot_id=plot.id, next_species=next_species, recommendation=recommendation)
        self.audit.add(module='rotation', action='create', user_id=user.id, farm_id=plot.farm_id, record_id=str(plan.id))
        self.db.commit(); self.db.refresh(plan)
        return plan
