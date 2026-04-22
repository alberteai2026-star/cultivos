from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.finance_repository import FinanceRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.finance import FinanceSummaryOut, JournalEntryListResponse, TrialBalanceLineOut, TrialBalanceResponse


class FinanceService:
    def __init__(self, db: Session):
        self.db = db
        self.finance = FinanceRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.finance.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, farm_id: int, plot_id: int | None, crop_cycle_id: int | None, entry_type: str, category: str, amount: float, description: str | None, happened_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        entry = self.finance.create(farm_id=farm_id, plot_id=plot_id, crop_cycle_id=crop_cycle_id, entry_type=entry_type, category=category, amount=amount, description=description, happened_at=happened_at)
        self.audit.add(module='finance', action=f'create_{entry_type}', user_id=user.id, farm_id=farm_id, record_id=str(entry.id))
        self.db.commit(); self.db.refresh(entry)
        return entry

    def summary_for_user(self, *, user: User, farm_id: int, date_from: datetime | None, date_to: datetime | None) -> FinanceSummaryOut:
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total_income, total_cost = self.finance.summarize(farm_id=farm_id, date_from=date_from, date_to=date_to)
        return FinanceSummaryOut(
            farm_id=farm_id,
            date_from=date_from,
            date_to=date_to,
            total_income=total_income,
            total_cost=total_cost,
            net_result=round(total_income - total_cost, 2),
        )

    def create_journal_entry_for_user(
        self,
        *,
        user: User,
        farm_id: int,
        entry_date: datetime,
        reference: str | None,
        description: str | None,
        lines: list[dict],
    ):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total_debit = round(sum(float(line.get('debit', 0) or 0) for line in lines), 2)
        total_credit = round(sum(float(line.get('credit', 0) or 0) for line in lines), 2)
        if total_debit <= 0 or total_credit <= 0 or total_debit != total_credit:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='La partida no está balanceada (debe = haber)')

        entry = self.finance.create_journal_entry(
            farm_id=farm_id,
            entry_date=entry_date,
            reference=reference,
            description=description,
            lines=lines,
        )
        self.audit.add(module='finance', action='create_journal_entry', user_id=user.id, farm_id=farm_id, record_id=str(entry.id))
        self.db.commit(); self.db.refresh(entry)
        return entry

    def list_journal_entries_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        entry_date_from: datetime | None = None,
        entry_date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> JournalEntryListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.finance.list_journal_entries_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            entry_date_from=entry_date_from,
            entry_date_to=entry_date_to,
            limit=limit,
            offset=offset,
        )
        return JournalEntryListResponse(total=total, items=items)

    def trial_balance_for_user(
        self,
        *,
        user: User,
        farm_id: int,
        entry_date_from: datetime | None = None,
        entry_date_to: datetime | None = None,
    ) -> TrialBalanceResponse:
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        rows = self.finance.trial_balance(farm_id=farm_id, entry_date_from=entry_date_from, entry_date_to=entry_date_to)
        items = [
            TrialBalanceLineOut(
                account_code=code,
                account_name=name,
                total_debit=debit,
                total_credit=credit,
                balance=round(debit - credit, 2),
            )
            for code, name, debit, credit in rows
        ]
        return TrialBalanceResponse(
            farm_id=farm_id,
            entry_date_from=entry_date_from,
            entry_date_to=entry_date_to,
            total_accounts=len(items),
            items=items,
        )
