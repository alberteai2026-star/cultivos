from datetime import datetime

from pydantic import BaseModel, Field


class FinanceEntryCreateRequest(BaseModel):
    farm_id: int
    plot_id: int | None = None
    crop_cycle_id: int | None = None
    entry_type: str = Field(pattern='^(cost|income)$')
    category: str = Field(min_length=2, max_length=80)
    amount: float = Field(gt=0)
    description: str | None = None
    happened_at: datetime


class FinanceEntryOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    crop_cycle_id: int | None
    entry_type: str
    category: str
    amount: float
    description: str | None
    happened_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class FinanceSummaryOut(BaseModel):
    farm_id: int
    date_from: datetime | None
    date_to: datetime | None
    total_income: float
    total_cost: float
    net_result: float


class JournalLineRequest(BaseModel):
    account_code: str = Field(min_length=2, max_length=30)
    account_name: str = Field(min_length=2, max_length=120)
    debit: float = Field(default=0, ge=0)
    credit: float = Field(default=0, ge=0)


class JournalEntryCreateRequest(BaseModel):
    farm_id: int
    entry_date: datetime
    reference: str | None = Field(default=None, max_length=80)
    description: str | None = None
    lines: list[JournalLineRequest] = Field(min_length=2)


class JournalEntryOut(BaseModel):
    id: int
    farm_id: int
    entry_date: datetime
    reference: str | None
    description: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JournalEntryListResponse(BaseModel):
    total: int
    items: list[JournalEntryOut]


class TrialBalanceLineOut(BaseModel):
    account_code: str
    account_name: str
    total_debit: float
    total_credit: float
    balance: float


class TrialBalanceResponse(BaseModel):
    farm_id: int
    entry_date_from: datetime | None
    entry_date_to: datetime | None
    total_accounts: int
    items: list[TrialBalanceLineOut]
