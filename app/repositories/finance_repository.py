from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.accounting_journal_entry import AccountingJournalEntry
from app.models.accounting_journal_line import AccountingJournalLine
from app.models.finance_entry import FinanceEntry


class FinanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, farm_id: int, plot_id: int | None, crop_cycle_id: int | None, entry_type: str, category: str, amount: float, description: str | None, happened_at: datetime) -> FinanceEntry:
        entry = FinanceEntry(
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            entry_type=entry_type,
            category=category,
            amount=amount,
            description=description,
            happened_at=happened_at,
        )
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[FinanceEntry]:
        if not farm_ids:
            return []
        q = select(FinanceEntry).where(FinanceEntry.farm_id.in_(farm_ids)).order_by(FinanceEntry.happened_at.desc(), FinanceEntry.id.desc())
        return list(self.db.scalars(q).all())

    def summarize(self, *, farm_id: int, date_from: datetime | None, date_to: datetime | None) -> tuple[float, float]:
        q = select(
            func.coalesce(func.sum(FinanceEntry.amount).filter(FinanceEntry.entry_type == 'income'), 0),
            func.coalesce(func.sum(FinanceEntry.amount).filter(FinanceEntry.entry_type == 'cost'), 0),
        ).where(FinanceEntry.farm_id == farm_id)
        if date_from is not None:
            q = q.where(FinanceEntry.happened_at >= date_from)
        if date_to is not None:
            q = q.where(FinanceEntry.happened_at <= date_to)
        income, cost = self.db.execute(q).one()
        return float(income), float(cost)

    def create_journal_entry(
        self,
        *,
        farm_id: int,
        entry_date: datetime,
        reference: str | None,
        description: str | None,
        lines: list[dict],
    ) -> AccountingJournalEntry:
        entry = AccountingJournalEntry(
            farm_id=farm_id,
            entry_date=entry_date,
            reference=reference,
            description=description,
            status='posted',
        )
        self.db.add(entry)
        self.db.flush()
        for line in lines:
            obj = AccountingJournalLine(
                journal_entry_id=entry.id,
                account_code=line['account_code'],
                account_name=line['account_name'],
                debit=line.get('debit', 0) or 0,
                credit=line.get('credit', 0) or 0,
            )
            self.db.add(obj)
        self.db.flush()
        return entry

    def list_journal_entries_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        entry_date_from: datetime | None = None,
        entry_date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[AccountingJournalEntry]]:
        if not farm_ids:
            return 0, []
        q = select(AccountingJournalEntry).where(AccountingJournalEntry.farm_id.in_(farm_ids))
        count_q = select(func.count(AccountingJournalEntry.id)).where(AccountingJournalEntry.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(AccountingJournalEntry.farm_id == farm_id)
            count_q = count_q.where(AccountingJournalEntry.farm_id == farm_id)
        if entry_date_from is not None:
            q = q.where(AccountingJournalEntry.entry_date >= entry_date_from)
            count_q = count_q.where(AccountingJournalEntry.entry_date >= entry_date_from)
        if entry_date_to is not None:
            q = q.where(AccountingJournalEntry.entry_date <= entry_date_to)
            count_q = count_q.where(AccountingJournalEntry.entry_date <= entry_date_to)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(AccountingJournalEntry.entry_date.desc(), AccountingJournalEntry.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def trial_balance(
        self,
        *,
        farm_id: int,
        entry_date_from: datetime | None = None,
        entry_date_to: datetime | None = None,
    ) -> list[tuple[str, str, float, float]]:
        q = (
            select(
                AccountingJournalLine.account_code,
                AccountingJournalLine.account_name,
                func.coalesce(func.sum(AccountingJournalLine.debit), 0),
                func.coalesce(func.sum(AccountingJournalLine.credit), 0),
            )
            .join(AccountingJournalEntry, AccountingJournalEntry.id == AccountingJournalLine.journal_entry_id)
            .where(AccountingJournalEntry.farm_id == farm_id)
            .group_by(AccountingJournalLine.account_code, AccountingJournalLine.account_name)
            .order_by(AccountingJournalLine.account_code.asc())
        )
        if entry_date_from is not None:
            q = q.where(AccountingJournalEntry.entry_date >= entry_date_from)
        if entry_date_to is not None:
            q = q.where(AccountingJournalEntry.entry_date <= entry_date_to)
        rows = self.db.execute(q).all()
        return [(str(c), str(n), float(d), float(cr)) for c, n, d, cr in rows]
