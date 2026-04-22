from datetime import datetime

from pydantic import BaseModel, Field


class InventoryItemCreateRequest(BaseModel):
    farm_id: int
    name: str = Field(min_length=2, max_length=180)
    unit: str = Field(min_length=1, max_length=20)
    min_stock: float | None = None


class InventoryItemUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    min_stock: float | None = None


class InventoryMovementCreateRequest(BaseModel):
    item_id: int
    movement_type: str = Field(min_length=3, max_length=20)
    quantity: float
    reason: str | None = Field(default=None, max_length=120)


class InventoryMovementUpdateRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=120)


class InventoryItemOut(BaseModel):
    id: int
    farm_id: int
    name: str | None = None
    unit: str | None = None
    min_stock: float | None = None
    current_stock: float | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class InventoryItemListResponse(BaseModel):
    total: int
    items: list[InventoryItemOut]


class InventoryMovementOut(BaseModel):
    id: int
    farm_id: int
    item_id: int
    movement_type: str
    quantity: float
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InventoryMovementListResponse(BaseModel):
    total: int
    items: list[InventoryMovementOut]
