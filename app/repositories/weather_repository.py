from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.weather_observation import WeatherObservation


class WeatherRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        farm_id: int,
        observed_at,
        temperature_c: float | None,
        humidity_pct: float | None,
        rainfall_mm: float | None,
        wind_kmh: float | None,
        source: str | None,
    ) -> WeatherObservation:
        obs = WeatherObservation(
            farm_id=farm_id,
            observed_at=observed_at,
            temperature_c=temperature_c,
            humidity_pct=humidity_pct,
            rainfall_mm=rainfall_mm,
            wind_kmh=wind_kmh,
            source=source,
        )
        self.db.add(obs)
        self.db.flush()
        return obs

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[WeatherObservation]:
        if not farm_ids:
            return []
        query = select(WeatherObservation).where(WeatherObservation.farm_id.in_(farm_ids)).order_by(WeatherObservation.id.desc())
        return list(self.db.scalars(query).all())
