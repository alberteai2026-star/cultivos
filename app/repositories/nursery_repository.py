from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.nursery_batch import NurseryBatch


class NurseryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, farm_id: int, plot_id: int | None, species: str, variety: str | None, sowing_date: datetime, tray_count: int, status: str, notes: str | None) -> NurseryBatch:
        batch = NurseryBatch(
            farm_id=farm_id,
            plot_id=plot_id,
            species=species,
            variety=variety,
            sowing_date=sowing_date,
            tray_count=tray_count,
            status=status,
            notes=notes,
        )
        self.db.add(batch)
        self.db.flush()
        return batch

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        species_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[NurseryBatch]]:
        if not farm_ids:
            return 0, []
        q = select(NurseryBatch).where(NurseryBatch.farm_id.in_(farm_ids))
        count_q = select(func.count(NurseryBatch.id)).where(NurseryBatch.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(NurseryBatch.farm_id == farm_id)
            count_q = count_q.where(NurseryBatch.farm_id == farm_id)
        if plot_id is not None:
            q = q.where(NurseryBatch.plot_id == plot_id)
            count_q = count_q.where(NurseryBatch.plot_id == plot_id)
        if status_value is not None:
            q = q.where(NurseryBatch.status == status_value)
            count_q = count_q.where(NurseryBatch.status == status_value)
        if species_search is not None:
            pattern = f'%{species_search}%'
            q = q.where(NurseryBatch.species.ilike(pattern))
            count_q = count_q.where(NurseryBatch.species.ilike(pattern))
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(NurseryBatch.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, batch_id: int) -> NurseryBatch | None:
        return self.db.get(NurseryBatch, batch_id)

    def update_fields(
        self,
        batch: NurseryBatch,
        *,
        species: str | None = None,
        variety: str | None = None,
        sowing_date: datetime | None = None,
        tray_count: int | None = None,
        notes: str | None = None,
    ) -> NurseryBatch:
        if species is not None:
            batch.species = species
        if variety is not None:
            batch.variety = variety
        if sowing_date is not None:
            batch.sowing_date = sowing_date
        if tray_count is not None:
            batch.tray_count = tray_count
        if notes is not None:
            batch.notes = notes
        self.db.add(batch)
        return batch
