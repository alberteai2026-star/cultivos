from datetime import datetime

from sqlalchemy import func, select
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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        source: str | None = None,
        observed_from: datetime | None = None,
        observed_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[WeatherObservation]]:
        if not farm_ids:
            return 0, []

        query = select(WeatherObservation).where(WeatherObservation.farm_id.in_(farm_ids))
        count_query = select(func.count(WeatherObservation.id)).where(WeatherObservation.farm_id.in_(farm_ids))

        if farm_id is not None:
            query = query.where(WeatherObservation.farm_id == farm_id)
            count_query = count_query.where(WeatherObservation.farm_id == farm_id)
        if source is not None:
            query = query.where(WeatherObservation.source == source)
            count_query = count_query.where(WeatherObservation.source == source)
        if observed_from is not None:
            query = query.where(WeatherObservation.observed_at >= observed_from)
            count_query = count_query.where(WeatherObservation.observed_at >= observed_from)
        if observed_to is not None:
            query = query.where(WeatherObservation.observed_at <= observed_to)
            count_query = count_query.where(WeatherObservation.observed_at <= observed_to)

        total = int(self.db.scalar(count_query) or 0)
        query = query.order_by(WeatherObservation.observed_at.desc(), WeatherObservation.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(query).all())

    def get_by_id(self, observation_id: int) -> WeatherObservation | None:
        return self.db.get(WeatherObservation, observation_id)

    def update_fields(
        self,
        obs: WeatherObservation,
        *,
        observed_at: datetime | None,
        temperature_c: float | None,
        humidity_pct: float | None,
        rainfall_mm: float | None,
        wind_kmh: float | None,
        source: str | None,
    ) -> WeatherObservation:
        if observed_at is not None:
            obs.observed_at = observed_at
        obs.temperature_c = temperature_c
        obs.humidity_pct = humidity_pct
        obs.rainfall_mm = rainfall_mm
        obs.wind_kmh = wind_kmh
        obs.source = source
        self.db.flush()
        return obs
