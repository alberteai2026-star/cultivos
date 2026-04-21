from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.weather import (
    WeatherObservationCreateRequest,
    WeatherObservationListResponse,
    WeatherObservationOut,
    WeatherObservationUpdateRequest,
)
from app.services.weather_service import WeatherService

router = APIRouter()


@router.get('/observations', response_model=WeatherObservationListResponse)
def list_weather_observations(
    farm_id: int | None = Query(default=None, ge=1),
    source: str | None = Query(default=None),
    observed_from: datetime | None = Query(default=None),
    observed_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)
    return service.list_for_user(
        user,
        farm_id=farm_id,
        source=source,
        observed_from=observed_from,
        observed_to=observed_to,
        limit=limit,
        offset=offset,
    )


@router.get('/observations/{observation_id}', response_model=WeatherObservationOut)
def get_weather_observation(
    observation_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)
    return service.get_for_user(user=user, observation_id=observation_id)


@router.post('/observations', response_model=WeatherObservationOut, status_code=201)
def create_weather_observation(
    payload: WeatherObservationCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)
    return service.create_for_user(
        user=user,
        farm_id=payload.farm_id,
        observed_at=payload.observed_at,
        temperature_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
        rainfall_mm=payload.rainfall_mm,
        wind_kmh=payload.wind_kmh,
        source=payload.source,
    )


@router.patch('/observations/{observation_id}', response_model=WeatherObservationOut)
def update_weather_observation(
    observation_id: int,
    payload: WeatherObservationUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)
    return service.update_for_user(
        user=user,
        observation_id=observation_id,
        observed_at=payload.observed_at,
        temperature_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
        rainfall_mm=payload.rainfall_mm,
        wind_kmh=payload.wind_kmh,
        source=payload.source,
    )
