from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.phytosanitary_record import PhytosanitaryRecord


class PhytosanitaryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, farm_id: int, plot_id: int, crop_cycle_id: int | None, detected_issue: str, severity: str, action_taken: str, observed_at: datetime) -> PhytosanitaryRecord:
        record = PhytosanitaryRecord(
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            detected_issue=detected_issue,
            severity=severity,
            action_taken=action_taken,
            observed_at=observed_at,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[PhytosanitaryRecord]:
        if not farm_ids:
            return []
        q = select(PhytosanitaryRecord).where(PhytosanitaryRecord.farm_id.in_(farm_ids)).order_by(PhytosanitaryRecord.id.desc())
        return list(self.db.scalars(q).all())
