from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.iot_service import IoTService


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


class _Device:
    def __init__(self):
        self.id = 5
        self.farm_id = 10


class _Rule:
    def __init__(self):
        self.id = 9
        self.farm_id = 10
        self.device_id = 5
        self.metric = 'soil_moisture'
        self.operator = '<='
        self.threshold_value = 30.0
        self.severity = 'high'
        self.status = 'active'
        self.created_at = datetime(2026, 1, 1)


class _Reading:
    def __init__(self):
        self.id = 21
        self.device_id = 5
        self.metric = 'soil_moisture'
        self.value = 25.0
        self.recorded_at = datetime(2026, 1, 2)


class _ValveCommand:
    def __init__(self):
        self.id = 31
        self.farm_id = 10
        self.device_id = 5
        self.action = 'open'
        self.status = 'queued'
        self.source = 'manual'
        self.requested_at = datetime(2026, 1, 3)
        self.executed_at = None


class _Repo:
    def __init__(self):
        self.device = _Device()
        self.rule = _Rule()
        self.reading = _Reading()
        self.command = _ValveCommand()
        self.last_kwargs = None

    def list_devices_by_farm_ids(self, farm_ids, **kwargs):
        return 1, [self.device]

    def get_device(self, device_id: int):
        return self.device if device_id == self.device.id else None

    def create_rule(self, **kwargs):
        self.last_kwargs = kwargs
        return self.rule

    def list_rules_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.rule]

    def latest_reading_for_rule(self, *, rule, allowed_device_ids):
        self.last_kwargs = {'rule_id': rule.id, 'allowed_device_ids': allowed_device_ids}
        return self.reading

    def create_valve_command(self, **kwargs):
        self.last_kwargs = kwargs
        return self.command

    def list_valve_commands_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.command]


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


def test_create_rule_for_user_validates_operator():
    service = IoTService(db=None)
    service.iot = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.create_rule_for_user(
            user=_User(1),
            farm_id=10,
            device_id=5,
            metric='soil_moisture',
            operator='!=',
            threshold_value=30,
            severity='high',
            status_value='active',
        )

    assert exc.value.status_code == 422


def test_create_rule_for_user_creates_and_audits():
    db = _DB()
    repo = _Repo()
    service = IoTService(db=db)
    service.iot = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    rule = service.create_rule_for_user(
        user=_User(1),
        farm_id=10,
        device_id=5,
        metric='soil_moisture',
        operator='<=',
        threshold_value=30,
        severity='high',
        status_value='active',
    )

    assert rule.id == 9
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'create_rule'


def test_list_alerts_for_user_returns_triggered_alerts():
    service = IoTService(db=None)
    repo = _Repo()
    service.iot = repo
    service.relations = _RelationsAllow()

    payload = service.list_alerts_for_user(user=_User(1), farm_id=10)

    assert payload.total == 1
    assert payload.items[0].rule_id == 9
    assert payload.items[0].current_value == 25.0


def test_list_rules_for_user_denies_unallowed_farm():
    service = IoTService(db=None)
    service.iot = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.list_rules_for_user(user=_User(1), farm_id=10)

    assert exc.value.status_code == 403


def test_create_valve_command_for_user_validates_action():
    service = IoTService(db=None)
    service.iot = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.create_valve_command_for_user(user=_User(1), farm_id=10, device_id=5, action='invalid', source='manual')

    assert exc.value.status_code == 422


def test_create_valve_command_for_user_creates_and_audits():
    db = _DB()
    repo = _Repo()
    service = IoTService(db=db)
    service.iot = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    command = service.create_valve_command_for_user(user=_User(1), farm_id=10, device_id=5, action='open', source='manual')

    assert command.id == 31
    assert db.commits == 1
    assert service.audit.entries[0]['action'] == 'create_valve_command'


def test_list_valve_commands_for_user_forwards_filters():
    service = IoTService(db=None)
    repo = _Repo()
    service.iot = repo
    service.relations = _RelationsAllow()

    payload = service.list_valve_commands_for_user(user=_User(1), farm_id=10, device_id=5, status_value='queued', limit=10, offset=1)

    assert payload.total == 1
    assert payload.items[0].action == 'open'
    assert repo.last_kwargs == {'farm_ids': [10], 'farm_id': 10, 'device_id': 5, 'status_value': 'queued', 'limit': 10, 'offset': 1}
