from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class PlotService:
    def __init__(self, db: Session):
        self.db = db
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        return self.plots.list_by_farm_ids(farm_ids)

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
                detail="No tienes acceso a esta finca",
            )

        plot = self.plots.create(
            farm_id=farm_id,
            code=code,
            name=name,
            area_ha=area_ha,
            soil_type=soil_type,
            status=status_value,
        )

        self.audit.add(
            module="plots",
            action="create",
            user_id=user.id,
            farm_id=farm_id,
            record_id=str(plot.id),
            metadata={"code": plot.code, "name": plot.name},
        )

        self.db.commit()
        self.db.refresh(plot)
        return plot
