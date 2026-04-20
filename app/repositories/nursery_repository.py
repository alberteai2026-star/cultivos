from datetime import datetime

from sqlalchemy import select
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

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[NurseryBatch]:
        if not farm_ids:
            return []
        q = select(NurseryBatch).where(NurseryBatch.farm_id.in_(farm_ids)).order_by(NurseryBatch.id.desc())
        return list(self.db.scalars(q).all())
