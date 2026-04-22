from datetime import datetime

from sqlalchemy import func, select
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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        species: str | None = None,
        sowing_from: datetime | None = None,
        sowing_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[CropCycle]]:
        if not farm_ids:
            return 0, []

        q = select(CropCycle).where(CropCycle.farm_id.in_(farm_ids))
        count_q = select(func.count(CropCycle.id)).where(CropCycle.farm_id.in_(farm_ids))

        if farm_id is not None:
            q = q.where(CropCycle.farm_id == farm_id)
            count_q = count_q.where(CropCycle.farm_id == farm_id)
        if plot_id is not None:
            q = q.where(CropCycle.plot_id == plot_id)
            count_q = count_q.where(CropCycle.plot_id == plot_id)
        if status_value is not None:
            q = q.where(CropCycle.status == status_value)
            count_q = count_q.where(CropCycle.status == status_value)
        if species is not None:
            q = q.where(CropCycle.species.ilike(f"%{species.strip()}%"))
            count_q = count_q.where(CropCycle.species.ilike(f"%{species.strip()}%"))
        if sowing_from is not None:
            q = q.where(CropCycle.sowing_date >= sowing_from)
            count_q = count_q.where(CropCycle.sowing_date >= sowing_from)
        if sowing_to is not None:
            q = q.where(CropCycle.sowing_date <= sowing_to)
            count_q = count_q.where(CropCycle.sowing_date <= sowing_to)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(CropCycle.sowing_date.desc(), CropCycle.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, cycle_id: int) -> CropCycle | None:
        return self.db.get(CropCycle, cycle_id)

    def update_fields(
        self,
        cycle: CropCycle,
        *,
        species: str | None,
        variety: str | None,
        sowing_date: datetime | None,
    ) -> CropCycle:
        if species is not None:
            cycle.species = species
        cycle.variety = variety
        if sowing_date is not None:
            cycle.sowing_date = sowing_date
        self.db.flush()
        return cycle
