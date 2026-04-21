from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.dashboard import (
    DashboardAlertListResponse,
    DashboardAlertOut,
    DashboardGoalListResponse,
    DashboardKPICompareResponse,
    DashboardKPIOut,
    DashboardSnapshotListResponse,
)


class DashboardService:
    ALLOWED_KPI_KEYS = {'active_cycles', 'pending_tasks', 'inventory_low_items', 'income_total', 'cost_total', 'net_total'}
    GOAL_STATUS = {'activa', 'pausada', 'archivada'}

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

    def list_snapshots_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        captured_from: datetime | None = None,
        captured_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> DashboardSnapshotListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.dashboard.list_snapshots_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            captured_from=captured_from,
            captured_to=captured_to,
            limit=limit,
            offset=offset,
        )
        return DashboardSnapshotListResponse(total=total, items=items)

    def get_snapshot_for_user(self, *, user: User, snapshot_id: int):
        snapshot = self.dashboard.get_snapshot_by_id(snapshot_id)
        if not snapshot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Snapshot no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=snapshot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return snapshot

    def compare_kpis_for_user(self, *, user: User, farm_ids: list[int]) -> DashboardKPICompareResponse:
        allowed_farm_ids = self.relations.list_farm_ids_by_user(user.id)
        for farm_id in farm_ids:
            if farm_id not in allowed_farm_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a una de las fincas solicitadas')

        items = [self.get_kpis_for_user(user=user, farm_id=farm_id) for farm_id in farm_ids]
        return DashboardKPICompareResponse(total_farms=len(items), items=items)

    def create_goal_for_user(self, *, user: User, farm_id: int, kpi_key: str, target_value: float, period_label: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        if kpi_key not in self.ALLOWED_KPI_KEYS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='kpi_key inválido')
        goal = self.dashboard.create_goal(farm_id=farm_id, kpi_key=kpi_key, target_value=target_value, period_label=period_label)
        self.audit.add(module='dashboard', action='create_goal', user_id=user.id, farm_id=farm_id, record_id=str(goal.id))
        self.db.commit(); self.db.refresh(goal)
        return goal

    def list_goals_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        status_filter: str | None = None,
        kpi_key: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> DashboardGoalListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.dashboard.list_goals_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            status=status_filter,
            kpi_key=kpi_key,
            limit=limit,
            offset=offset,
        )
        return DashboardGoalListResponse(total=total, items=items)

    def update_goal_for_user(
        self,
        *,
        user: User,
        goal_id: int,
        target_value: float | None,
        period_label: str | None,
        status_value: str | None,
    ):
        goal = self.dashboard.get_goal_by_id(goal_id)
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Meta no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=goal.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        if status_value is not None and status_value not in self.GOAL_STATUS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='status inválido')

        if target_value is not None:
            goal.target_value = target_value
        if period_label is not None:
            goal.period_label = period_label
        if status_value is not None:
            goal.status = status_value

        self.audit.add(module='dashboard', action='update_goal', user_id=user.id, farm_id=goal.farm_id, record_id=str(goal.id))
        self.db.commit(); self.db.refresh(goal)
        return goal

    def list_alerts_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> DashboardAlertListResponse:
        goals = self.list_goals_for_user(
            user,
            farm_id=farm_id,
            status_filter='activa',
            limit=limit,
            offset=offset,
        )
        alerts: list[DashboardAlertOut] = []
        for goal in goals.items:
            kpis = self.get_kpis_for_user(user=user, farm_id=goal.farm_id)
            current_value = float(getattr(kpis, goal.kpi_key))
            delta = round(current_value - float(goal.target_value), 2)
            state = self._compute_alert_state(kpi_key=goal.kpi_key, current_value=current_value, target_value=float(goal.target_value))
            alerts.append(
                DashboardAlertOut(
                    farm_id=goal.farm_id,
                    kpi_key=goal.kpi_key,
                    period_label=goal.period_label,
                    current_value=current_value,
                    target_value=float(goal.target_value),
                    delta_value=delta,
                    state=state,
                )
            )
        return DashboardAlertListResponse(total=len(alerts), items=alerts)

    def _compute_alert_state(self, *, kpi_key: str, current_value: float, target_value: float) -> str:
        lower_is_better = {'pending_tasks', 'inventory_low_items', 'cost_total'}
        if kpi_key in lower_is_better:
            if current_value <= target_value:
                return 'ok'
            if current_value <= target_value * 1.15:
                return 'warning'
            return 'critical'
        if current_value >= target_value:
            return 'ok'
        if current_value >= target_value * 0.85:
            return 'warning'
        return 'critical'
