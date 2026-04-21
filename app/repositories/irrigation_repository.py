from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.irrigation_event import IrrigationEvent


class IrrigationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, farm_id: int, plot_id: int, scheduled_at, applied_mm: float | None, cost: float | None) -> IrrigationEvent:
        event = IrrigationEvent(
            farm_id=farm_id,
            plot_id=plot_id,
            scheduled_at=scheduled_at,
            applied_mm=applied_mm,
            cost=cost,
            status='programado',
        )
        self.db.add(event)
        self.db.flush()
        return event

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[IrrigationEvent]]:
        if not farm_ids:
            return 0, []
        q = select(IrrigationEvent).where(IrrigationEvent.farm_id.in_(farm_ids))
        count_q = select(func.count(IrrigationEvent.id)).where(IrrigationEvent.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(IrrigationEvent.farm_id == farm_id)
            count_q = count_q.where(IrrigationEvent.farm_id == farm_id)
        if plot_id is not None:
            q = q.where(IrrigationEvent.plot_id == plot_id)
            count_q = count_q.where(IrrigationEvent.plot_id == plot_id)
        if status_value is not None:
            q = q.where(IrrigationEvent.status == status_value)
            count_q = count_q.where(IrrigationEvent.status == status_value)
        if scheduled_from is not None:
            q = q.where(IrrigationEvent.scheduled_at >= scheduled_from)
            count_q = count_q.where(IrrigationEvent.scheduled_at >= scheduled_from)
        if scheduled_to is not None:
            q = q.where(IrrigationEvent.scheduled_at <= scheduled_to)
            count_q = count_q.where(IrrigationEvent.scheduled_at <= scheduled_to)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(IrrigationEvent.scheduled_at.desc(), IrrigationEvent.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, event_id: int) -> IrrigationEvent | None:
        return self.db.get(IrrigationEvent, event_id)

    def update_fields(self, event: IrrigationEvent, *, scheduled_at: datetime | None, applied_mm: float | None, cost: float | None) -> IrrigationEvent:
        if scheduled_at is not None:
            event.scheduled_at = scheduled_at
        event.applied_mm = applied_mm
        event.cost = cost
        self.db.flush()
        return event
