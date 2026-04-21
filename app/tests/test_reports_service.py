import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.services.reports_service import ReportsService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _RelationsAllow:
    def list_farm_ids_by_user(self, user_id: int):
        return [10, 20]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return True


class _RelationsDeny:
    def list_farm_ids_by_user(self, user_id: int):
        return []

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return False


class _ReportsRepo:
    def __init__(self):
        self.last_args = None
        now = datetime.utcnow()
        self.export = type('Export', (), {
            'id': 7,
            'farm_id': 10,
            'report_type': 'overview',
            'format': 'pdf',
            'period_label': '2026-Q1',
            'file_url': None,
            'status': 'generado',
            'generated_at': now,
            'signed_by': None,
            'signature_hash': None,
            'signed_at': None,
            'created_at': now,
        })()

    def overview(self, farm_id: int):
        return 3, 5, 2

    def list_exports_by_farm_ids(self, farm_ids, *, farm_id=None, report_type=None, status=None, generated_from=None, generated_to=None, limit=100, offset=0):
        self.last_args = {
            'farm_ids': farm_ids,
            'farm_id': farm_id,
            'report_type': report_type,
            'status': status,
            'generated_from': generated_from,
            'generated_to': generated_to,
            'limit': limit,
            'offset': offset,
        }
        return 1, [self.export]

    def get_export_by_id(self, export_id: int):
        return self.export if export_id == self.export.id else None

    def update_export_fields(self, export, **kwargs):
        self.last_args = kwargs
        return export

    def sign_export(self, export, *, signed_by: str, signature_hash: str, signed_at: datetime):
        export.signed_by = signed_by
        export.signature_hash = signature_hash
        export.signed_at = signed_at
        export.status = 'firmado'
        return export


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


def test_overview_csv_for_user_builds_expected_csv():
    service = ReportsService(db=None)
    service.relations = _RelationsAllow()
    service.reports = _ReportsRepo()

    csv_data = service.overview_csv_for_user(user=_User(1), farm_id=10)

    assert csv_data.splitlines() == [
        'farm_id,total_harvests,total_invoices,total_exports',
        '10,3,5,2',
    ]


def test_overview_json_for_user_builds_expected_payload():
    service = ReportsService(db=None)
    service.relations = _RelationsAllow()
    service.reports = _ReportsRepo()

    payload = service.overview_json_for_user(user=_User(1), farm_id=10)

    assert payload == {'farm_id': 10, 'total_harvests': 3, 'total_invoices': 5, 'total_exports': 2}


def test_overview_for_user_denies_access_when_user_has_no_farm_access():
    service = ReportsService(db=None)
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.overview_for_user(user=_User(1), farm_id=10)

    assert exc.value.status_code == 403


def test_list_exports_for_user_forwards_filters_and_pagination():
    service = ReportsService(db=None)
    reports = _ReportsRepo()
    service.relations = _RelationsAllow()
    service.reports = reports

    start = datetime.utcnow() - timedelta(days=30)
    end = datetime.utcnow()
    exports = service.list_exports_for_user(
        user=_User(1),
        farm_id=10,
        report_type='overview',
        status_value='generado',
        generated_from=start,
        generated_to=end,
        limit=50,
        offset=5,
    )

    assert exports.total == 1
    assert len(exports.items) == 1
    assert reports.last_args == {
        'farm_ids': [10, 20],
        'farm_id': 10,
        'report_type': 'overview',
        'status': 'generado',
        'generated_from': start,
        'generated_to': end,
        'limit': 50,
        'offset': 5,
    }


def test_list_exports_for_user_denies_when_requested_farm_is_not_allowed():
    service = ReportsService(db=None)
    service.relations = _RelationsAllow()
    service.reports = _ReportsRepo()

    with pytest.raises(HTTPException) as exc:
        service.list_exports_for_user(user=_User(1), farm_id=999, limit=10, offset=0)

    assert exc.value.status_code == 403


def test_list_exports_for_user_rejects_invalid_date_range():
    service = ReportsService(db=None)
    service.relations = _RelationsAllow()
    service.reports = _ReportsRepo()
    start = datetime.utcnow()
    end = start - timedelta(days=1)

    with pytest.raises(HTTPException) as exc:
        service.list_exports_for_user(user=_User(1), farm_id=10, generated_from=start, generated_to=end, limit=10, offset=0)

    assert exc.value.status_code == 422


def test_get_export_for_user_denies_access_when_user_has_no_farm_access():
    service = ReportsService(db=None)
    service.relations = _RelationsDeny()
    service.reports = _ReportsRepo()

    with pytest.raises(HTTPException) as exc:
        service.get_export_for_user(user=_User(1), export_id=7)

    assert exc.value.status_code == 403


def test_update_export_status_for_user_updates_and_audits():
    db = _DB()
    service = ReportsService(db=db)
    service.relations = _RelationsAllow()
    service.reports = _ReportsRepo()
    service.audit = _Audit()

    updated = service.update_export_status_for_user(user=_User(1), export_id=7, status_value='procesando')

    assert updated.status == 'procesando'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_export_status'


def test_sign_export_for_user_signs_and_audits():
    db = _DB()
    service = ReportsService(db=db)
    service.relations = _RelationsAllow()
    service.reports = _ReportsRepo()
    service.audit = _Audit()

    signed = service.sign_export_for_user(
        user=_User(1),
        export_id=7,
        signed_by='Ing. Laura Perez',
        signature_hash='sha256:abc123456789',
    )

    assert signed.status == 'firmado'
    assert signed.signed_by == 'Ing. Laura Perez'
    assert signed.signature_hash == 'sha256:abc123456789'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'sign_export'


def test_overview_pdf_for_user_returns_pdf_bytes():
    service = ReportsService(db=None)
    service.relations = _RelationsAllow()
    service.reports = _ReportsRepo()

    payload = service.overview_pdf_for_user(user=_User(1), farm_id=10)

    assert payload.startswith(b'%PDF-1.4')
    assert b'Reporte General de Finca' in payload


def test_overview_xlsx_for_user_returns_xlsx_bytes():
    service = ReportsService(db=None)
    service.relations = _RelationsAllow()
    service.reports = _ReportsRepo()

    payload = service.overview_xlsx_for_user(user=_User(1), farm_id=10)

    assert payload.startswith(b'PK')
    assert b'[Content_Types].xml' in payload
