from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.gis import (
    MapFeatureCreateRequest,
    MapFeatureListResponse,
    MapFeatureOut,
    MapFeatureUpdateRequest,
    MapFeatureVersionListResponse,
)
from app.services.gis_service import GISService

router = APIRouter()


@router.get('/features', response_model=MapFeatureListResponse)
def list_map_features(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    feature_type: str | None = None,
    name_search: str | None = Query(default=None, alias='search'),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return GISService(db).list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        feature_type=feature_type,
        name_search=name_search,
        limit=limit,
        offset=offset,
    )


@router.post('/features', response_model=MapFeatureOut, status_code=201)
def create_map_feature(payload: MapFeatureCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return GISService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, feature_type=payload.feature_type, name=payload.name, geometry_geojson=payload.geometry_geojson, properties_json=payload.properties_json)


@router.get('/features/{feature_id}', response_model=MapFeatureOut)
def get_map_feature(feature_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return GISService(db).get_for_user(user=user, feature_id=feature_id)


@router.patch('/features/{feature_id}', response_model=MapFeatureOut)
def update_map_feature(feature_id: int, payload: MapFeatureUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return GISService(db).update_for_user(
        user=user,
        feature_id=feature_id,
        name=payload.name,
        geometry_geojson=payload.geometry_geojson,
        properties_json=payload.properties_json,
    )


@router.get('/features/{feature_id}/history', response_model=MapFeatureVersionListResponse)
def list_map_feature_history(
    feature_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return GISService(db).list_history_for_user(user=user, feature_id=feature_id, limit=limit, offset=offset)
