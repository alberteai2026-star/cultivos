from sqlalchemy import func, select
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

    def get_by_id(self, farm_id: int) -> Farm | None:
        return self.db.get(Farm, farm_id)

    def list_all(self) -> list[Farm]:
        return list(self.db.scalars(select(Farm).order_by(Farm.id.desc())).all())

    def list_by_ids(
        self,
        farm_ids: list[int],
        *,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[Farm]]:
        if not farm_ids:
            return 0, []

        q = select(Farm).where(Farm.id.in_(farm_ids))
        count_q = select(func.count(Farm.id)).where(Farm.id.in_(farm_ids))

        if search:
            pattern = f"%{search.strip()}%"
            q = q.where(Farm.name.ilike(pattern))
            count_q = count_q.where(Farm.name.ilike(pattern))

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(Farm.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def update(
        self,
        farm: Farm,
        *,
        name: str | None,
        total_area_ha: float | None,
        department: str | None,
        municipality: str | None,
    ) -> Farm:
        if name is not None:
            farm.name = name
        farm.total_area_ha = total_area_ha
        farm.department = department
        farm.municipality = municipality
        self.db.flush()
        return farm
