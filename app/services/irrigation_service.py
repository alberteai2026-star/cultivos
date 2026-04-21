from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.irrigation_repository import IrrigationRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.irrigation import IrrigationEventListResponse


class IrrigationService:
    _allowed_status_transitions = {
        'programado': {'ejecutado', 'cancelado'},
        'ejecutado': set(),
        'cancelado': set(),
    }

    def __init__(self, db: Session):
        self.db = db
        self.irrigation = IrrigationRepository(db)
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
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> IrrigationEventListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.irrigation.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            status_value=status_value,
            scheduled_from=scheduled_from,
            scheduled_to=scheduled_to,
            limit=limit,
            offset=offset,
        )
        return IrrigationEventListResponse(total=total, items=items)

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

    def get_for_user(self, *, user: User, event_id: int):
        event = self.irrigation.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Evento de riego no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=event.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return event

    def update_for_user(
        self,
        *,
        user: User,
        event_id: int,
        scheduled_at: datetime | None,
        applied_mm: float | None,
        cost: float | None,
    ):
        event = self.get_for_user(user=user, event_id=event_id)
        updated = self.irrigation.update_fields(event, scheduled_at=scheduled_at, applied_mm=applied_mm, cost=cost)
        self.audit.add(module='irrigation', action='update', user_id=user.id, farm_id=event.farm_id, record_id=str(event.id))
        self.db.commit(); self.db.refresh(updated)
        return updated

    def update_status_for_user(self, *, user: User, event_id: int, status_value: str):
        event = self.get_for_user(user=user, event_id=event_id)
        current_status = event.status
        if current_status != status_value:
            if status_value not in self._allowed_status_transitions.get(current_status, set()):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Transición de estado inválida: {current_status} -> {status_value}",
                )
        event.status = status_value
        self.audit.add(module='irrigation', action='update_status', user_id=user.id, farm_id=event.farm_id, record_id=str(event.id))
        self.db.commit(); self.db.refresh(event)
        return event
