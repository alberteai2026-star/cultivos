from datetime import datetime

from pydantic import BaseModel, Field


class ShipmentCreateRequest(BaseModel):
    farm_id: int
    invoice_id: int | None = None
    destination_name: str = Field(min_length=2, max_length=150)
    transport_type: str | None = Field(default=None, max_length=60)
    driver_name: str | None = Field(default=None, max_length=120)
    vehicle_plate: str | None = Field(default=None, max_length=30)
    departure_at: datetime
    arrival_at: datetime | None = None
    status: str = Field(default='pendiente', max_length=30)
    freight_cost: float | None = Field(default=None, ge=0)
    notes: str | None = None


class ShipmentOut(BaseModel):
    id: int
    farm_id: int
    invoice_id: int | None
    destination_name: str
    transport_type: str | None
    driver_name: str | None
    vehicle_plate: str | None
    departure_at: datetime
    arrival_at: datetime | None
    status: str
    freight_cost: float | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
