from datetime import datetime

from pydantic import BaseModel, Field


class IoTDeviceCreateRequest(BaseModel):
    farm_id: int
    plot_id: int | None = None
    name: str = Field(min_length=2, max_length=120)
    device_type: str = Field(min_length=2, max_length=60)
    status: str = Field(default='active', max_length=30)


class IoTDeviceOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    name: str
    device_type: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IoTReadingCreateRequest(BaseModel):
    device_id: int
    metric: str = Field(min_length=2, max_length=60)
    value: float
    unit: str | None = Field(default=None, max_length=20)
    recorded_at: datetime


class IoTReadingOut(BaseModel):
    id: int
    device_id: int
    metric: str
    value: float
    unit: str | None
    recorded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
