from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.crop_cycle import CropCycle
from app.models.dashboard_goal import DashboardGoal
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

    def list_snapshots_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        captured_from: datetime | None = None,
        captured_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[DashboardSnapshot]]:
        if not farm_ids:
            return 0, []
        q = select(DashboardSnapshot).where(DashboardSnapshot.farm_id.in_(farm_ids))
        count_q = select(func.count(DashboardSnapshot.id)).where(DashboardSnapshot.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(DashboardSnapshot.farm_id == farm_id)
            count_q = count_q.where(DashboardSnapshot.farm_id == farm_id)
        if captured_from is not None:
            q = q.where(DashboardSnapshot.captured_at >= captured_from)
            count_q = count_q.where(DashboardSnapshot.captured_at >= captured_from)
        if captured_to is not None:
            q = q.where(DashboardSnapshot.captured_at <= captured_to)
            count_q = count_q.where(DashboardSnapshot.captured_at <= captured_to)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(DashboardSnapshot.captured_at.desc(), DashboardSnapshot.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_snapshot_by_id(self, snapshot_id: int) -> DashboardSnapshot | None:
        return self.db.get(DashboardSnapshot, snapshot_id)

    def list_goals_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        status: str | None = None,
        kpi_key: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[DashboardGoal]]:
        if not farm_ids:
            return 0, []

        q = select(DashboardGoal).where(DashboardGoal.farm_id.in_(farm_ids))
        count_q = select(func.count(DashboardGoal.id)).where(DashboardGoal.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(DashboardGoal.farm_id == farm_id)
            count_q = count_q.where(DashboardGoal.farm_id == farm_id)
        if status is not None:
            q = q.where(DashboardGoal.status == status)
            count_q = count_q.where(DashboardGoal.status == status)
        if kpi_key is not None:
            q = q.where(DashboardGoal.kpi_key == kpi_key)
            count_q = count_q.where(DashboardGoal.kpi_key == kpi_key)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(DashboardGoal.farm_id.asc(), DashboardGoal.kpi_key.asc(), DashboardGoal.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_goal_by_id(self, goal_id: int) -> DashboardGoal | None:
        return self.db.get(DashboardGoal, goal_id)

    def create_goal(self, *, farm_id: int, kpi_key: str, target_value: float, period_label: str | None) -> DashboardGoal:
        goal = DashboardGoal(
            farm_id=farm_id,
            kpi_key=kpi_key,
            target_value=target_value,
            period_label=period_label,
            status='activa',
        )
        self.db.add(goal)
        self.db.flush()
        return goal
