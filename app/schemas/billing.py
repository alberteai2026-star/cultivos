from datetime import datetime

from pydantic import BaseModel, Field


class CustomerCreateRequest(BaseModel):
    farm_id: int
    full_name: str = Field(min_length=2, max_length=150)
    document_id: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=50)


class CustomerOut(BaseModel):
    id: int
    farm_id: int
    full_name: str
    document_id: str | None
    email: str | None
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvoiceCreateRequest(BaseModel):
    farm_id: int
    customer_id: int
    invoice_number: str = Field(min_length=1, max_length=60)
    issue_date: datetime
    due_date: datetime | None = None
    total_amount: float = Field(gt=0)
    status: str = Field(default='pendiente', max_length=30)
    notes: str | None = None


class InvoiceOut(BaseModel):
    id: int
    farm_id: int
    customer_id: int
    invoice_number: str
    issue_date: datetime
    due_date: datetime | None
    total_amount: float
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
