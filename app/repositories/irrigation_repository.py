from sqlalchemy import select
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

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[IrrigationEvent]:
        if not farm_ids:
            return []
        q = select(IrrigationEvent).where(IrrigationEvent.farm_id.in_(farm_ids)).order_by(IrrigationEvent.id.desc())
        return list(self.db.scalars(q).all())
