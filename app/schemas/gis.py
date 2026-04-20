from datetime import datetime

from pydantic import BaseModel, Field


class MapFeatureCreateRequest(BaseModel):
    farm_id: int
    plot_id: int | None = None
    feature_type: str = Field(default='polygon', max_length=40)
    name: str = Field(min_length=2, max_length=120)
    geometry_geojson: str = Field(min_length=2)
    properties_json: str | None = None


class MapFeatureOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    feature_type: str
    name: str
    geometry_geojson: str
    properties_json: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
