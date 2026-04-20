from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.finance_entry import FinanceEntry


class FinanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, farm_id: int, plot_id: int | None, crop_cycle_id: int | None, entry_type: str, category: str, amount: float, description: str | None, happened_at: datetime) -> FinanceEntry:
        entry = FinanceEntry(
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            entry_type=entry_type,
            category=category,
            amount=amount,
            description=description,
            happened_at=happened_at,
        )
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[FinanceEntry]:
        if not farm_ids:
            return []
        q = select(FinanceEntry).where(FinanceEntry.farm_id.in_(farm_ids)).order_by(FinanceEntry.happened_at.desc(), FinanceEntry.id.desc())
        return list(self.db.scalars(q).all())

    def summarize(self, *, farm_id: int, date_from: datetime | None, date_to: datetime | None) -> tuple[float, float]:
        q = select(
            func.coalesce(func.sum(FinanceEntry.amount).filter(FinanceEntry.entry_type == 'income'), 0),
            func.coalesce(func.sum(FinanceEntry.amount).filter(FinanceEntry.entry_type == 'cost'), 0),
        ).where(FinanceEntry.farm_id == farm_id)
        if date_from is not None:
            q = q.where(FinanceEntry.happened_at >= date_from)
        if date_to is not None:
            q = q.where(FinanceEntry.happened_at <= date_to)
        income, cost = self.db.execute(q).one()
        return float(income), float(cost)
