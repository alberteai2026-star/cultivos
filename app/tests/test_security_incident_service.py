from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.security_service import SecurityService


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


class _Incident:
    def __init__(self):
        self.id = 12
        self.farm_id = 10
        self.alert_type = 'movimiento_perimetral'
        self.severity = 'alta'
        self.status = 'abierta'
        self.description = None
        self.detected_at = datetime.utcnow()
        self.resolved_at = None
        self.created_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.incident = _Incident()
        self.last_args = None

    def create_incident(self, **kwargs):
        self.last_args = kwargs
        return self.incident

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.incident]

    def get_by_id(self, incident_id: int):
        return self.incident if incident_id == self.incident.id else None


class _Audit:
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


def test_list_for_user_forwards_filters():
    service = SecurityService(db=None)
    repo = _Repo()
    service.security = repo
    service.relations = _RelationsAllow()

    payload = service.list_for_user(user=_User(1), farm_id=10, status_value='abierta', severity='alta', limit=20, offset=2)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args == {'farm_ids': [10], 'farm_id': 10, 'status_value': 'abierta', 'severity': 'alta', 'limit': 20, 'offset': 2}


def test_get_for_user_denies_without_access():
    service = SecurityService(db=None)
    service.security = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), incident_id=12)

    assert exc.value.status_code == 403


def test_update_status_for_user_updates_and_audits():
    db = _DB()
    service = SecurityService(db=db)
    service.security = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_status_for_user(user=_User(1), incident_id=12, status_value='cerrada', resolved_at=datetime.utcnow())

    assert updated.status == 'cerrada'
    assert db.commits == 1
    assert service.audit.entries[0]['action'] == 'update_incident_status'
