from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AccountingJournalLine(Base):
    __tablename__ = 'accounting_journal_lines'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    journal_entry_id: Mapped[int] = mapped_column(ForeignKey('accounting_journal_entries.id'), nullable=False, index=True)
    account_code: Mapped[str] = mapped_column(String(30), nullable=False)
    account_name: Mapped[str] = mapped_column(String(120), nullable=False)
    debit: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    credit: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
