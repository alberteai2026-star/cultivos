from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.monitoring_visit import MonitoringVisit


class MonitoringRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        farm_id: int,
        plot_id: int,
        crop_cycle_id: int | None,
        observed_at,
        bbch_stage: str | None,
        issue_type: str | None,
        severity: str | None,
        notes: str | None,
    ) -> MonitoringVisit:
        visit = MonitoringVisit(
            farm_id=farm_id,
            plot_id=plot_id,
            crop_cycle_id=crop_cycle_id,
            observed_at=observed_at,
            bbch_stage=bbch_stage,
            issue_type=issue_type,
            severity=severity,
            notes=notes,
        )
        self.db.add(visit)
        self.db.flush()
        return visit

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[MonitoringVisit]:
        if not farm_ids:
            return []
        query = select(MonitoringVisit).where(MonitoringVisit.farm_id.in_(farm_ids)).order_by(MonitoringVisit.id.desc())
        return list(self.db.scalars(query).all())
