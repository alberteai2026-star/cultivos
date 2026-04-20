from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.crop_cycle import CropCycle
from app.models.dashboard_snapshot import DashboardSnapshot
from app.models.finance_entry import FinanceEntry
from app.models.inventory_item import InventoryItem
from app.models.task import Task


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_kpis(self, farm_id: int) -> tuple[int, int, int, float, float]:
        active_cycles = self.db.execute(select(func.count(CropCycle.id)).where(CropCycle.farm_id == farm_id, CropCycle.status == 'active')).scalar_one()
        pending_tasks = self.db.execute(select(func.count(Task.id)).where(Task.farm_id == farm_id, Task.status.in_(['pending', 'in_progress']))).scalar_one()
        inventory_low = self.db.execute(select(func.count(InventoryItem.id)).where(InventoryItem.farm_id == farm_id, InventoryItem.min_stock.is_not(None), InventoryItem.current_stock <= InventoryItem.min_stock)).scalar_one()
        income = self.db.execute(select(func.coalesce(func.sum(FinanceEntry.amount), 0)).where(FinanceEntry.farm_id == farm_id, FinanceEntry.entry_type == 'income')).scalar_one()
        cost = self.db.execute(select(func.coalesce(func.sum(FinanceEntry.amount), 0)).where(FinanceEntry.farm_id == farm_id, FinanceEntry.entry_type == 'cost')).scalar_one()
        return int(active_cycles), int(pending_tasks), int(inventory_low), float(income), float(cost)

    def create_snapshot(self, *, farm_id: int, active_cycles: int, pending_tasks: int, inventory_low_items: int, income_total: float, cost_total: float, captured_at: datetime) -> DashboardSnapshot:
        snapshot = DashboardSnapshot(
            farm_id=farm_id,
            active_cycles=active_cycles,
            pending_tasks=pending_tasks,
            inventory_low_items=inventory_low_items,
            income_total=income_total,
            cost_total=cost_total,
            captured_at=captured_at,
        )
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def list_snapshots_by_farm_ids(self, farm_ids: list[int]) -> list[DashboardSnapshot]:
        if not farm_ids:
            return []
        q = select(DashboardSnapshot).where(DashboardSnapshot.farm_id.in_(farm_ids)).order_by(DashboardSnapshot.captured_at.desc(), DashboardSnapshot.id.desc())
        return list(self.db.scalars(q).all())
