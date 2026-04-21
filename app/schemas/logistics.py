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


class ShipmentUpdateRequest(BaseModel):
    destination_name: str | None = Field(default=None, min_length=2, max_length=150)
    transport_type: str | None = Field(default=None, max_length=60)
    driver_name: str | None = Field(default=None, max_length=120)
    vehicle_plate: str | None = Field(default=None, max_length=30)
    departure_at: datetime | None = None
    arrival_at: datetime | None = None
    freight_cost: float | None = Field(default=None, ge=0)
    notes: str | None = None


class ShipmentStatusUpdateRequest(BaseModel):
    status: str = Field(max_length=30)


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


class ShipmentListResponse(BaseModel):
    total: int
    items: list[ShipmentOut]


class ShipmentTrackingPointCreateRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_kmh: float | None = Field(default=None, ge=0)
    heading_deg: float | None = Field(default=None, ge=0, le=360)
    recorded_at: datetime
    source: str = Field(default='gps', max_length=20)
    notes: str | None = None


class ShipmentTrackingPointOut(BaseModel):
    id: int
    shipment_id: int
    latitude: float
    longitude: float
    speed_kmh: float | None
    heading_deg: float | None
    recorded_at: datetime
    source: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ShipmentTrackingPointListResponse(BaseModel):
    total: int
    items: list[ShipmentTrackingPointOut]
