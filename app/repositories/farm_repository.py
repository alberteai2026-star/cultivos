from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm


class FarmRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        name: str,
        total_area_ha: float | None,
        department: str | None,
        municipality: str | None,
    ) -> Farm:
        farm = Farm(
            name=name,
            total_area_ha=total_area_ha,
            department=department,
            municipality=municipality,
        )
        self.db.add(farm)
        self.db.flush()
        return farm

    def list_all(self) -> list[Farm]:
        return list(self.db.scalars(select(Farm).order_by(Farm.id.desc())).all())

    def list_by_ids(self, farm_ids: list[int]) -> list[Farm]:
        if not farm_ids:
            return []
        query = select(Farm).where(Farm.id.in_(farm_ids)).order_by(Farm.id.desc())
        return list(self.db.scalars(query).all())
