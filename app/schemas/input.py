from datetime import datetime

from pydantic import BaseModel, Field


class InputProductCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    category: str = Field(min_length=2, max_length=80)
    ica_register: str | None = Field(default=None, max_length=80)
    withholding_days: int | None = None


class InputProductUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    ica_register: str | None = Field(default=None, max_length=80)
    withholding_days: int | None = None


class InputProductOut(BaseModel):
    id: int
    name: str
    category: str
    ica_register: str | None
    withholding_days: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InputProductListResponse(BaseModel):
    total: int
    items: list[InputProductOut]


class InputApplicationCreateRequest(BaseModel):
    plot_id: int
    input_product_id: int
    task_id: int | None = None
    applied_at: datetime
    quantity: float
    unit: str = Field(min_length=1, max_length=20)


class InputApplicationUpdateRequest(BaseModel):
    applied_at: datetime | None = None
    quantity: float | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=20)


class InputApplicationOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int
    task_id: int | None
    input_product_id: int
    applied_at: datetime
    quantity: float
    unit: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InputApplicationListResponse(BaseModel):
    total: int
    items: list[InputApplicationOut]
