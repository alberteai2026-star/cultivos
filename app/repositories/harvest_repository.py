from datetime import datetime

from sqlalchemy import func, select
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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        crop_cycle_id: int | None = None,
        harvested_from: datetime | None = None,
        harvested_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[Harvest]]:
        if not farm_ids:
            return 0, []

        query = select(Harvest).where(Harvest.farm_id.in_(farm_ids))
        count_query = select(func.count(Harvest.id)).where(Harvest.farm_id.in_(farm_ids))

        if farm_id is not None:
            query = query.where(Harvest.farm_id == farm_id)
            count_query = count_query.where(Harvest.farm_id == farm_id)
        if plot_id is not None:
            query = query.where(Harvest.plot_id == plot_id)
            count_query = count_query.where(Harvest.plot_id == plot_id)
        if crop_cycle_id is not None:
            query = query.where(Harvest.crop_cycle_id == crop_cycle_id)
            count_query = count_query.where(Harvest.crop_cycle_id == crop_cycle_id)
        if harvested_from is not None:
            query = query.where(Harvest.harvested_at >= harvested_from)
            count_query = count_query.where(Harvest.harvested_at >= harvested_from)
        if harvested_to is not None:
            query = query.where(Harvest.harvested_at <= harvested_to)
            count_query = count_query.where(Harvest.harvested_at <= harvested_to)

        total = int(self.db.scalar(count_query) or 0)
        query = query.order_by(Harvest.harvested_at.desc(), Harvest.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(query).all())

    def get_by_id(self, harvest_id: int) -> Harvest | None:
        return self.db.get(Harvest, harvest_id)

    def update_fields(
        self,
        harvest: Harvest,
        *,
        harvested_at: datetime | None,
        quantity: float | None,
        unit: str | None,
        quality_grade: str | None,
        destination: str | None,
    ) -> Harvest:
        if harvested_at is not None:
            harvest.harvested_at = harvested_at
        if quantity is not None:
            harvest.quantity = quantity
        if unit is not None:
            harvest.unit = unit
        harvest.quality_grade = quality_grade
        harvest.destination = destination
        self.db.flush()
        return harvest
