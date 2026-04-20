from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.harvest import Harvest


class HarvestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        farm_id: int,
        plot_id: int,
        crop_cycle_id: int | None,
        harvested_at,
        quantity: float,
        unit: str,
        quality_grade: str | None,
        destination: str | None,
    ) -> Harvest:
        harvest = Harvest(
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            harvested_at=harvested_at,
            quantity=quantity,
            unit=unit,
            quality_grade=quality_grade,
            destination=destination,
        )
        self.db.add(harvest)
        self.db.flush()
        return harvest

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[Harvest]:
        if not farm_ids:
            return []
        query = select(Harvest).where(Harvest.farm_id.in_(farm_ids)).order_by(Harvest.id.desc())
        return list(self.db.scalars(query).all())
