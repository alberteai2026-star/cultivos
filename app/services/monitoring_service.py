from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.monitoring_repository import MonitoringRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class MonitoringService:
    def __init__(self, db: Session):
        self.db = db
        self.monitoring = MonitoringRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        return self.monitoring.list_by_farm_ids(farm_ids)

    def create_for_user(
        self,
        *,
        user: User,
        plot_id: int,
        crop_cycle_id: int | None,
        observed_at,
        bbch_stage: str | None,
        issue_type: str | None,
        severity: str | None,
        notes: str | None,
    ):
        plot = self.plots.get_by_id(plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')

        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        visit = self.monitoring.create(
            farm_id=plot.farm_id,
            plot_id=plot.id,
            crop_cycle_id=crop_cycle_id,
            observed_at=observed_at,
            bbch_stage=bbch_stage,
            issue_type=issue_type,
            severity=severity,
            notes=notes,
        )

        self.audit.add(
            module='monitoring',
            action='create_visit',
            user_id=user.id,
            farm_id=plot.farm_id,
            record_id=str(visit.id),
            metadata={'plot_id': plot.id, 'issue_type': issue_type},
        )

        self.db.commit()
        self.db.refresh(visit)
        return visit
