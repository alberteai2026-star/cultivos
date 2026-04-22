from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.finance_service import FinanceService


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


class _Entry:
    def __init__(self):
        self.id = 1


class _JournalEntry:
    def __init__(self):
        self.id = 5
        self.farm_id = 10
        self.entry_date = datetime(2026, 1, 1)
        self.reference = 'NIIF-1'
        self.description = 'asiento'
        self.status = 'posted'
        self.created_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.journal = _JournalEntry()
        self.last_args = None

    def list_by_farm_ids(self, farm_ids):
        return []

    def create(self, **kwargs):
        return _Entry()

    def summarize(self, *, farm_id: int, date_from, date_to):
        return 1000.0, 250.0

    def create_journal_entry(self, **kwargs):
        self.last_args = kwargs
        return self.journal

    def list_journal_entries_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.journal]

    def trial_balance(self, *, farm_id: int, entry_date_from=None, entry_date_to=None):
        return [('1101', 'Caja', 500.0, 0.0), ('4101', 'Ventas', 0.0, 500.0)]


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


def test_create_journal_entry_for_user_requires_balanced_lines():
    service = FinanceService(db=None)
    service.finance = _Repo()
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.create_journal_entry_for_user(
            user=_User(1),
            farm_id=10,
            entry_date=datetime.utcnow(),
            reference=None,
            description=None,
            lines=[{'account_code': '1101', 'account_name': 'Caja', 'debit': 100, 'credit': 0}, {'account_code': '4101', 'account_name': 'Ventas', 'debit': 0, 'credit': 90}],
        )

    assert exc.value.status_code == 422


def test_create_journal_entry_for_user_creates_and_audits():
    db = _DB()
    service = FinanceService(db=db)
    service.finance = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    entry = service.create_journal_entry_for_user(
        user=_User(1),
        farm_id=10,
        entry_date=datetime.utcnow(),
        reference='N1',
        description='asiento',
        lines=[{'account_code': '1101', 'account_name': 'Caja', 'debit': 100, 'credit': 0}, {'account_code': '4101', 'account_name': 'Ventas', 'debit': 0, 'credit': 100}],
    )

    assert entry.id == 5
    assert db.commits == 1
    assert service.audit.entries[0]['action'] == 'create_journal_entry'


def test_list_journal_entries_for_user_denies_unallowed_farm():
    service = FinanceService(db=None)
    service.finance = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.list_journal_entries_for_user(user=_User(1), farm_id=10)

    assert exc.value.status_code == 403


def test_trial_balance_for_user_returns_balances():
    service = FinanceService(db=None)
    service.finance = _Repo()
    service.relations = _RelationsAllow()

    payload = service.trial_balance_for_user(user=_User(1), farm_id=10)

    assert payload.total_accounts == 2
    assert payload.items[0].account_code == '1101'
