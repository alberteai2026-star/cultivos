import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta
import hashlib
import json

from app.services.audit_service import AuditService


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


class _Export:
    def __init__(self, *, export_id: int = 5, user_id: int = 1, farm_id: int | None = 10):
        self.id = export_id
        self.user_id = user_id
        self.farm_id = farm_id
        self.format = 'csv'
        self.filters_json = '{"farm_id": 10}'
        self.file_url = None
        self.signature = 'abc123'
        self.status = 'solicitado'
        self.error_message = None
        self.completed_at = None
        self.created_at = '2026-01-01T00:00:00'


class _AuditRepo:
    def __init__(self):
        self.export = _Export()
        self.updated_kwargs = None
        self.entries = []

    def get_export_by_id(self, export_id: int):
        return self.export if export_id == self.export.id else None

    def update_export_fields(self, export, **kwargs):
        self.updated_kwargs = kwargs
        if kwargs.get('file_url') is not None:
            export.file_url = kwargs['file_url']
        return export

    def update_export_status(self, export, *, status: str, error_message: str | None, completed_at):
        export.status = status
        export.error_message = error_message
        export.completed_at = completed_at
        return export

    def add(self, **kwargs):
        self.entries.append(kwargs)

    def summary_logs(self, *, farm_ids, farm_id=None, module=None, action=None, created_from=None, created_to=None):
        self.updated_kwargs = {
            'farm_ids': farm_ids,
            'farm_id': farm_id,
            'module': module,
            'action': action,
            'created_from': created_from,
            'created_to': created_to,
        }
        return [('audit', 'update_export_status', 7), ('reports', 'sign_export', 3)]


class _DB:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1

    def refresh(self, _obj):
        return None


def test_get_export_for_user_returns_export_when_owner_and_farm_allowed():
    service = AuditService(db=None)
    service.audit = _AuditRepo()
    service.relations = _RelationsAllow()

    result = service.get_export_for_user(user=_User(1), export_id=5)

    assert result.id == 5
    assert result.farm_id == 10


def test_get_export_for_user_denies_when_export_is_from_another_user():
    service = AuditService(db=None)
    repo = _AuditRepo()
    repo.export = _Export(export_id=8, user_id=99, farm_id=10)
    service.audit = repo
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.get_export_for_user(user=_User(1), export_id=8)

    assert exc.value.status_code == 403


def test_update_export_for_user_updates_and_adds_audit_entry():
    db = _DB()
    service = AuditService(db=db)
    repo = _AuditRepo()
    service.audit = repo
    service.relations = _RelationsAllow()

    result = service.update_export_for_user(
        user=_User(1),
        export_id=5,
        format='json',
        file_url='https://files.local/audit-export-5.json',
        signature='new-signature',
    )

    assert result.file_url == 'https://files.local/audit-export-5.json'
    assert repo.updated_kwargs == {
        'format': 'json',
        'file_url': 'https://files.local/audit-export-5.json',
        'signature': 'new-signature',
    }
    assert len(repo.entries) == 1
    assert repo.entries[0]['action'] == 'update_export'
    assert db.commits == 1


def test_update_export_for_user_denies_when_user_has_no_farm_access():
    db = _DB()
    service = AuditService(db=db)
    service.audit = _AuditRepo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.update_export_for_user(user=_User(1), export_id=5, format='csv', file_url=None, signature=None)

    assert exc.value.status_code == 403


def test_update_export_status_for_user_updates_and_adds_audit_entry():
    db = _DB()
    service = AuditService(db=db)
    repo = _AuditRepo()
    service.audit = repo
    service.relations = _RelationsAllow()

    result = service.update_export_status_for_user(
        user=_User(1),
        export_id=5,
        status_value='procesando',
        error_message=None,
        completed_at=None,
    )

    assert result.status == 'procesando'
    assert len(repo.entries) == 1
    assert repo.entries[0]['action'] == 'update_export_status'
    assert db.commits == 1


def test_update_export_status_for_user_rejects_invalid_transition():
    db = _DB()
    service = AuditService(db=db)
    repo = _AuditRepo()
    repo.export.status = 'solicitado'
    service.audit = repo
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.update_export_status_for_user(
            user=_User(1),
            export_id=5,
            status_value='completado',
            error_message=None,
            completed_at=None,
        )

    assert exc.value.status_code == 409


def test_summary_for_user_returns_grouped_metrics():
    service = AuditService(db=None)
    repo = _AuditRepo()
    service.audit = repo
    service.relations = _RelationsAllow()

    start = datetime.utcnow() - timedelta(days=7)
    end = datetime.utcnow()
    result = service.summary_for_user(
        user=_User(1),
        farm_id=10,
        module='audit',
        action=None,
        created_from=start,
        created_to=end,
    )

    assert result.total_groups == 2
    assert result.items[0].module == 'audit'
    assert repo.updated_kwargs['farm_ids'] == [10]
    assert repo.updated_kwargs['farm_id'] == 10


def test_summary_for_user_rejects_invalid_date_range():
    service = AuditService(db=None)
    service.audit = _AuditRepo()
    service.relations = _RelationsAllow()

    start = datetime.utcnow()
    end = start - timedelta(days=1)

    with pytest.raises(HTTPException) as exc:
        service.summary_for_user(user=_User(1), created_from=start, created_to=end)

    assert exc.value.status_code == 422


def test_verify_export_signature_for_user_returns_valid_true():
    service = AuditService(db=None)
    repo = _AuditRepo()
    repo.export.filters_json = '{"action":"x","farm_id":10,"module":"audit"}'
    parsed = json.loads(repo.export.filters_json)
    repo.export.signature = hashlib.sha256(json.dumps(parsed, sort_keys=True).encode('utf-8')).hexdigest()
    service.audit = repo
    service.relations = _RelationsAllow()

    result = service.verify_export_signature_for_user(user=_User(1), export_id=5)

    assert result.valid is True
    assert result.current_signature == result.expected_signature


def test_verify_export_signature_for_user_returns_false_when_mismatch():
    service = AuditService(db=None)
    repo = _AuditRepo()
    repo.export.filters_json = '{"farm_id":10}'
    repo.export.signature = 'bad-signature'
    service.audit = repo
    service.relations = _RelationsAllow()

    result = service.verify_export_signature_for_user(user=_User(1), export_id=5)

    assert result.valid is False
