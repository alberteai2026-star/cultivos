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


class WeatherObservationOut(BaseModel):
    id: int
    farm_id: int
    observed_at: datetime
    temperature_c: float | None
    humidity_pct: float | None
    rainfall_mm: float | None
    wind_kmh: float | None
    source: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
