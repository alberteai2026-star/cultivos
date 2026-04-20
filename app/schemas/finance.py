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
