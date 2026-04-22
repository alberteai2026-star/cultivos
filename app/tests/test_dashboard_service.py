from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.services.dashboard_service import DashboardService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _RelationsAllow:
    def list_farm_ids_by_user(self, user_id: int):
        return [10]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return farm_id == 10


class _RelationsDeny:
    def list_farm_ids_by_user(self, user_id: int):
        return []

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return False


class _Snapshot:
    def __init__(self):
        self.id = 6
        self.farm_id = 10
        self.active_cycles = 2
        self.pending_tasks = 5
        self.inventory_low_items = 3
        self.income_total = 2000
        self.cost_total = 900
        self.captured_at = datetime.utcnow()
        self.created_at = datetime.utcnow()


class _Goal:
    def __init__(self):
        self.id = 7
        self.farm_id = 10
        self.kpi_key = 'pending_tasks'
        self.target_value = 4
        self.period_label = 'mensual'
        self.status = 'activa'
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.snapshot = _Snapshot()
        self.goal = _Goal()
        self.last_kwargs = None

    def list_snapshots_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.snapshot]

    def get_snapshot_by_id(self, snapshot_id: int):
        return self.snapshot if snapshot_id == self.snapshot.id else None

    def list_goals_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.goal]

    def create_goal(self, *, farm_id: int, kpi_key: str, target_value: float, period_label: str | None):
        self.goal.farm_id = farm_id
        self.goal.kpi_key = kpi_key
        self.goal.target_value = target_value
        self.goal.period_label = period_label
        return self.goal

    def get_goal_by_id(self, goal_id: int):
        return self.goal if goal_id == self.goal.id else None


def test_list_snapshots_for_user_forwards_filters_and_pagination():
    service = DashboardService(db=None)
    repo = _Repo()
    service.dashboard = repo
    service.relations = _RelationsAllow()

    start = datetime.utcnow() - timedelta(days=2)
    end = datetime.utcnow()
    response = service.list_snapshots_for_user(
        _User(1),
        farm_id=10,
        captured_from=start,
        captured_to=end,
        limit=20,
        offset=4,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'captured_from': start,
        'captured_to': end,
        'limit': 20,
        'offset': 4,
    }


def test_get_snapshot_for_user_denies_without_access():
    service = DashboardService(db=None)
    service.dashboard = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_snapshot_for_user(user=_User(1), snapshot_id=6)

    assert exc.value.status_code == 403


def test_compare_kpis_for_user_returns_items_for_allowed_farms():
    service = DashboardService(db=None)
    service.dashboard = _Repo()

    class _RelationsMulti:
        def list_farm_ids_by_user(self, user_id: int):
            return [10, 11]

        def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
            return farm_id in [10, 11]

    service.relations = _RelationsMulti()

    def _get_kpis(farm_id: int):
        return (1, 2, 0, 100.0 + farm_id, 20.0)

    service.dashboard.get_kpis = _get_kpis

    payload = service.compare_kpis_for_user(user=_User(1), farm_ids=[10, 11])

    assert payload.total_farms == 2
    assert len(payload.items) == 2


def test_compare_kpis_for_user_denies_unallowed_farm():
    service = DashboardService(db=None)
    service.dashboard = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.compare_kpis_for_user(user=_User(1), farm_ids=[10, 999])

    assert exc.value.status_code == 403


def test_create_goal_for_user_rejects_invalid_kpi_key():
    service = DashboardService(db=None)
    service.dashboard = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.create_goal_for_user(user=_User(1), farm_id=10, kpi_key='invalid', target_value=1, period_label='m')

    assert exc.value.status_code == 422


def test_list_alerts_for_user_computes_alert_state():
    service = DashboardService(db=None)
    service.dashboard = _Repo()
    service.relations = _RelationsAllow()

    class _NoopAudit:
        def add(self, **kwargs):
            return None

    service.audit = _NoopAudit()

    def _kpis(_farm_id: int):
        return (2, 6, 0, 1000.0, 100.0)

    service.dashboard.get_kpis = _kpis

    payload = service.list_alerts_for_user(user=_User(1), farm_id=10)

    assert payload.total == 1
    assert payload.items[0].kpi_key == 'pending_tasks'
    assert payload.items[0].state == 'critical'


def test_update_goal_for_user_denies_invalid_status():
    service = DashboardService(db=None)
    service.dashboard = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.update_goal_for_user(user=_User(1), goal_id=7, target_value=None, period_label=None, status_value='otra')

    assert exc.value.status_code == 422
