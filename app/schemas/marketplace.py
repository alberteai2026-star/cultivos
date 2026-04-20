from datetime import datetime

from pydantic import BaseModel, Field


class MarketListingCreateRequest(BaseModel):
    farm_id: int
    title: str = Field(min_length=2, max_length=150)
    product_name: str = Field(min_length=2, max_length=120)
    quantity: float = Field(gt=0)
    unit: str = Field(default='kg', max_length=20)
    unit_price: float = Field(gt=0)
    status: str = Field(default='abierta', max_length=30)
    description: str | None = None
    published_at: datetime


class MarketListingOut(BaseModel):
    id: int
    farm_id: int
    title: str
    product_name: str
    quantity: float
    unit: str
    unit_price: float
    status: str
    description: str | None
    published_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class MarketOfferCreateRequest(BaseModel):
    listing_id: int
    buyer_name: str = Field(min_length=2, max_length=150)
    buyer_contact: str | None = Field(default=None, max_length=120)
    offered_price: float = Field(gt=0)
    requested_quantity: float = Field(gt=0)
    message: str | None = None
    status: str = Field(default='nueva', max_length=30)


class MarketOfferOut(BaseModel):
    id: int
    listing_id: int
    buyer_name: str
    buyer_contact: str | None
    offered_price: float
    requested_quantity: float
    message: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
