from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.gis import MapFeatureCreateRequest, MapFeatureOut
from app.services.gis_service import GISService

router = APIRouter()


@router.get('/features', response_model=list[MapFeatureOut])
def list_map_features(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return GISService(db).list_for_user(user)


@router.post('/features', response_model=MapFeatureOut, status_code=201)
def create_map_feature(payload: MapFeatureCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return GISService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, feature_type=payload.feature_type, name=payload.name, geometry_geojson=payload.geometry_geojson, properties_json=payload.properties_json)
