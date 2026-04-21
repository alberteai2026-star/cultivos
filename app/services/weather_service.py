from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.repositories.weather_repository import WeatherRepository
from app.schemas.weather import WeatherObservationListResponse


class WeatherService:
    def __init__(self, db: Session):
        self.db = db
        self.weather = WeatherRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        source: str | None = None,
        observed_from: datetime | None = None,
        observed_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> WeatherObservationListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro offset debe ser mayor o igual a 0')
        if observed_from is not None and observed_to is not None and observed_from > observed_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Rango de fechas inválido')

        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.weather.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            source=source,
            observed_from=observed_from,
            observed_to=observed_to,
            limit=limit,
            offset=offset,
        )
        return WeatherObservationListResponse(total=total, items=items)

    def get_for_user(self, *, user: User, observation_id: int):
        obs = self.weather.get_by_id(observation_id)
        if not obs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Observación climática no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=obs.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return obs

    def create_for_user(
        self,
        *,
        user: User,
        farm_id: int,
        observed_at,
        temperature_c: float | None,
        humidity_pct: float | None,
        rainfall_mm: float | None,
        wind_kmh: float | None,
        source: str | None,
    ):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        obs = self.weather.create(
            farm_id=farm_id,
            observed_at=observed_at,
            temperature_c=temperature_c,
            humidity_pct=humidity_pct,
            rainfall_mm=rainfall_mm,
            wind_kmh=wind_kmh,
            source=source,
        )

        self.audit.add(
            module='weather',
            action='create_observation',
            user_id=user.id,
            farm_id=farm_id,
            record_id=str(obs.id),
            metadata={'source': source},
        )

        self.db.commit()
        self.db.refresh(obs)
        return obs

    def update_for_user(
        self,
        *,
        user: User,
        observation_id: int,
        observed_at: datetime | None,
        temperature_c: float | None,
        humidity_pct: float | None,
        rainfall_mm: float | None,
        wind_kmh: float | None,
        source: str | None,
    ):
        obs = self.weather.get_by_id(observation_id)
        if not obs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Observación climática no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=obs.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        updated = self.weather.update_fields(
            obs,
            observed_at=observed_at,
            temperature_c=temperature_c,
            humidity_pct=humidity_pct,
            rainfall_mm=rainfall_mm,
            wind_kmh=wind_kmh,
            source=source,
        )
        self.audit.add(
            module='weather',
            action='update_observation',
            user_id=user.id,
            farm_id=obs.farm_id,
            record_id=str(obs.id),
            metadata={'source': updated.source},
        )

        self.db.commit()
        self.db.refresh(updated)
        return updated
