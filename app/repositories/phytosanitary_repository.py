from datetime import datetime

from sqlalchemy import func, select
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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        severity: str | None = None,
        issue_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[PhytosanitaryRecord]]:
        if not farm_ids:
            return 0, []
        q = select(PhytosanitaryRecord).where(PhytosanitaryRecord.farm_id.in_(farm_ids))
        count_q = select(func.count(PhytosanitaryRecord.id)).where(PhytosanitaryRecord.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(PhytosanitaryRecord.farm_id == farm_id)
            count_q = count_q.where(PhytosanitaryRecord.farm_id == farm_id)
        if plot_id is not None:
            q = q.where(PhytosanitaryRecord.plot_id == plot_id)
            count_q = count_q.where(PhytosanitaryRecord.plot_id == plot_id)
        if severity is not None:
            q = q.where(PhytosanitaryRecord.severity == severity)
            count_q = count_q.where(PhytosanitaryRecord.severity == severity)
        if issue_search is not None:
            pattern = f'%{issue_search}%'
            q = q.where(PhytosanitaryRecord.detected_issue.ilike(pattern))
            count_q = count_q.where(PhytosanitaryRecord.detected_issue.ilike(pattern))
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(PhytosanitaryRecord.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, record_id: int) -> PhytosanitaryRecord | None:
        return self.db.get(PhytosanitaryRecord, record_id)

    def update_fields(
        self,
        record: PhytosanitaryRecord,
        *,
        detected_issue: str | None = None,
        severity: str | None = None,
        action_taken: str | None = None,
        observed_at: datetime | None = None,
    ) -> PhytosanitaryRecord:
        if detected_issue is not None:
            record.detected_issue = detected_issue
        if severity is not None:
            record.severity = severity
        if action_taken is not None:
            record.action_taken = action_taken
        if observed_at is not None:
            record.observed_at = observed_at
        self.db.add(record)
        return record
