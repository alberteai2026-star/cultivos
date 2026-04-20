from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crop_cycle import CropCycle


class CropCycleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        farm_id: int,
        plot_id: int,
        species: str,
        variety: str | None,
        sowing_date,
    ) -> CropCycle:
        cycle = CropCycle(
            farm_id=farm_id,
            plot_id=plot_id,
            species=species,
            variety=variety,
            sowing_date=sowing_date,
            status='activo',
        )
        self.db.add(cycle)
        self.db.flush()
        return cycle

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[CropCycle]:
        if not farm_ids:
            return []
        query = select(CropCycle).where(CropCycle.farm_id.in_(farm_ids)).order_by(CropCycle.id.desc())
        return list(self.db.scalars(query).all())
