from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.rotation_repository import RotationRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.rotation import RotationPlanListResponse


class RotationService:
    def __init__(self, db: Session):
        self.db = db
        self.rotation = RotationRepository(db)
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
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> RotationPlanListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.rotation.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            status_value=status_value,
            search=search,
            limit=limit,
            offset=offset,
        )
        return RotationPlanListResponse(total=total, items=items)

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

    def get_for_user(self, *, user: User, plan_id: int):
        plan = self.rotation.get_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Plan de rotación no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=plan.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return plan

    def update_for_user(self, *, user: User, plan_id: int, next_species: str | None, recommendation: str | None):
        plan = self.get_for_user(user=user, plan_id=plan_id)
        updated = self.rotation.update_fields(plan, next_species=next_species, recommendation=recommendation)
        self.audit.add(module='rotation', action='update', user_id=user.id, farm_id=plan.farm_id, record_id=str(plan.id))
        self.db.commit(); self.db.refresh(updated)
        return updated

    def update_status_for_user(self, *, user: User, plan_id: int, status_value: str):
        plan = self.get_for_user(user=user, plan_id=plan_id)
        plan.status = status_value
        self.audit.add(module='rotation', action='update_status', user_id=user.id, farm_id=plan.farm_id, record_id=str(plan.id))
        self.db.commit(); self.db.refresh(plan)
        return plan
