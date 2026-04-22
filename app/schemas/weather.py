from datetime import datetime

from pydantic import BaseModel, Field


class WeatherObservationCreateRequest(BaseModel):
    farm_id: int
    observed_at: datetime
    temperature_c: float | None = None
    humidity_pct: float | None = None
    rainfall_mm: float | None = None
    wind_kmh: float | None = None
    source: str | None = Field(default=None, max_length=50)


class WeatherObservationUpdateRequest(BaseModel):
    observed_at: datetime | None = None
    temperature_c: float | None = None
    humidity_pct: float | None = None
    rainfall_mm: float | None = None
    wind_kmh: float | None = None
    source: str | None = Field(default=None, max_length=50)


class WeatherObservationOut(BaseModel):
    id: int
    farm_id: int
    observed_at: datetime | None = None
    temperature_c: float | None = None
    humidity_pct: float | None = None
    rainfall_mm: float | None = None
    wind_kmh: float | None = None
    source: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class WeatherObservationListResponse(BaseModel):
    total: int
    items: list[WeatherObservationOut]
