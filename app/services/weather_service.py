from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.repositories.weather_repository import WeatherRepository


class WeatherService:
    def __init__(self, db: Session):
        self.db = db
        self.weather = WeatherRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        return self.weather.list_by_farm_ids(farm_ids)

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
