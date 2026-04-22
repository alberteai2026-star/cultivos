from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.monitoring_repository import MonitoringRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.monitoring import MonitoringVisitListResponse


class MonitoringService:
    def __init__(self, db: Session):
        self.db = db
        self.monitoring = MonitoringRepository(db)
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
        issue_type: str | None = None,
        severity: str | None = None,
        observed_from: datetime | None = None,
        observed_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> MonitoringVisitListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro offset debe ser mayor o igual a 0')
        if observed_from is not None and observed_to is not None and observed_from > observed_to:
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

        total, items = self.monitoring.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            issue_type=issue_type,
            severity=severity,
            observed_from=observed_from,
            observed_to=observed_to,
            limit=limit,
            offset=offset,
        )
        return MonitoringVisitListResponse(total=total, items=items)

    def get_for_user(self, *, user: User, visit_id: int):
        visit = self.monitoring.get_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Visita de monitoreo no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=visit.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return visit

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

    def update_for_user(
        self,
        *,
        user: User,
        visit_id: int,
        observed_at: datetime | None,
        bbch_stage: str | None,
        issue_type: str | None,
        severity: str | None,
        notes: str | None,
    ):
        visit = self.monitoring.get_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Visita de monitoreo no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=visit.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        updated = self.monitoring.update_fields(
            visit,
            observed_at=observed_at,
            bbch_stage=bbch_stage,
            issue_type=issue_type,
            severity=severity,
            notes=notes,
        )
        self.audit.add(
            module='monitoring',
            action='update_visit',
            user_id=user.id,
            farm_id=visit.farm_id,
            record_id=str(visit.id),
            metadata={'issue_type': updated.issue_type, 'severity': updated.severity},
        )

        self.db.commit()
        self.db.refresh(updated)
        return updated
