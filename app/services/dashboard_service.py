from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.dashboard import DashboardKPIOut


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.dashboard = DashboardRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def get_kpis_for_user(self, *, user: User, farm_id: int) -> DashboardKPIOut:
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        active_cycles, pending_tasks, inventory_low_items, income_total, cost_total = self.dashboard.get_kpis(farm_id)
        return DashboardKPIOut(
            farm_id=farm_id,
            active_cycles=active_cycles,
            pending_tasks=pending_tasks,
            inventory_low_items=inventory_low_items,
            income_total=income_total,
            cost_total=cost_total,
            net_total=round(income_total - cost_total, 2),
        )

    def create_snapshot_for_user(self, *, user: User, farm_id: int, captured_at: datetime):
        kpis = self.get_kpis_for_user(user=user, farm_id=farm_id)
        snap = self.dashboard.create_snapshot(farm_id=farm_id, active_cycles=kpis.active_cycles, pending_tasks=kpis.pending_tasks, inventory_low_items=kpis.inventory_low_items, income_total=kpis.income_total, cost_total=kpis.cost_total, captured_at=captured_at)
        self.audit.add(module='dashboard', action='create_snapshot', user_id=user.id, farm_id=farm_id, record_id=str(snap.id))
        self.db.commit(); self.db.refresh(snap)
        return snap

    def list_snapshots_for_user(self, user: User):
        return self.dashboard.list_snapshots_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))
