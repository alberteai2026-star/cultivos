from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.services.monitoring_service import MonitoringService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _Plot:
    def __init__(self, farm_id: int):
        self.farm_id = farm_id


class _RelationsAllow:
    def list_farm_ids_by_user(self, user_id: int):
        return [10, 20]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return farm_id in {10, 20}


class _RelationsDeny:
    def list_farm_ids_by_user(self, user_id: int):
        return []

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return False


class _PlotsRepo:
    def __init__(self, plot=None):
        self.plot = plot

    def get_by_id(self, plot_id: int):
        return self.plot


class _Visit:
    def __init__(self, visit_id: int, farm_id: int):
        self.id = visit_id
        self.farm_id = farm_id
        self.issue_type = 'maleza'
        self.severity = 'media'


class _MonitoringRepo:
    def __init__(self):
        self.last_args = None
        self.visit = _Visit(visit_id=7, farm_id=10)

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.visit]

    def get_by_id(self, visit_id: int):
        return self.visit if visit_id == self.visit.id else None

    def update_fields(self, visit, **kwargs):
        self.last_args = kwargs
        for key, value in kwargs.items():
            setattr(visit, key, value)
        return visit


class _AuditRepo:
    def __init__(self):
        self.entries = []

    def add(self, **kwargs):
        self.entries.append(kwargs)


class _DB:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1

    def refresh(self, _obj):
        return None


def test_list_for_user_forwards_filters_and_pagination():
    service = MonitoringService(db=None)
    repo = _MonitoringRepo()
    service.monitoring = repo
    service.relations = _RelationsAllow()
    service.plots = _PlotsRepo(plot=_Plot(farm_id=10))

    start = datetime.utcnow() - timedelta(days=10)
    end = datetime.utcnow()

    payload = service.list_for_user(
        _User(1),
        farm_id=10,
        plot_id=3,
        crop_cycle_id=8,
        issue_type='plaga',
        severity='alta',
        observed_from=start,
        observed_to=end,
        limit=20,
        offset=2,
    )

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args == {
        'farm_ids': [10, 20],
        'farm_id': 10,
        'plot_id': 3,
        'crop_cycle_id': 8,
        'issue_type': 'plaga',
        'severity': 'alta',
        'observed_from': start,
        'observed_to': end,
        'limit': 20,
        'offset': 2,
    }


def test_list_for_user_rejects_invalid_date_range():
    service = MonitoringService(db=None)
    service.monitoring = _MonitoringRepo()
    service.relations = _RelationsAllow()

    start = datetime.utcnow()
    end = start - timedelta(days=1)

    with pytest.raises(HTTPException) as exc:
        service.list_for_user(_User(1), observed_from=start, observed_to=end)

    assert exc.value.status_code == 422


def test_get_for_user_denies_access_when_user_not_related_to_farm():
    service = MonitoringService(db=None)
    service.monitoring = _MonitoringRepo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), visit_id=7)

    assert exc.value.status_code == 403


def test_update_for_user_updates_and_audits_visit():
    db = _DB()
    service = MonitoringService(db=db)
    service.monitoring = _MonitoringRepo()
    service.relations = _RelationsAllow()
    service.audit = _AuditRepo()

    updated = service.update_for_user(
        user=_User(1),
        visit_id=7,
        observed_at=None,
        bbch_stage='65',
        issue_type='enfermedad',
        severity='baja',
        notes='Sin avance relevante',
    )

    assert updated.issue_type == 'enfermedad'
    assert updated.severity == 'baja'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_visit'
