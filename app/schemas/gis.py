from datetime import datetime

from pydantic import BaseModel, Field


class MapFeatureCreateRequest(BaseModel):
    farm_id: int
    plot_id: int | None = None
    feature_type: str = Field(default='polygon', max_length=40)
    name: str = Field(min_length=2, max_length=120)
    geometry_geojson: str = Field(min_length=2)
    properties_json: str | None = None


class MapFeatureUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    geometry_geojson: str | None = Field(default=None, min_length=2)
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


class MapFeatureListResponse(BaseModel):
    total: int
    items: list[MapFeatureOut]


class MapFeatureVersionOut(BaseModel):
    id: int
    feature_id: int
    version_no: int
    name: str
    geometry_geojson: str
    properties_json: str | None
    changed_by_user_id: int | None
    changed_at: datetime

    model_config = {"from_attributes": True}


class MapFeatureVersionListResponse(BaseModel):
    total: int
    items: list[MapFeatureVersionOut]
