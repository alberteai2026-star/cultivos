from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.weather import WeatherObservationCreateRequest, WeatherObservationOut
from app.services.weather_service import WeatherService

router = APIRouter()


@router.get('/observations', response_model=list[WeatherObservationOut])
def list_weather_observations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)
    return service.list_for_user(user)


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
