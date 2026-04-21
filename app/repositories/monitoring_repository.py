from datetime import datetime

from sqlalchemy import func, select
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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        crop_cycle_id: int | None = None,
        issue_type: str | None = None,
        severity: str | None = None,
        observed_from: datetime | None = None,
        observed_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[MonitoringVisit]]:
        if not farm_ids:
            return 0, []

        query = select(MonitoringVisit).where(MonitoringVisit.farm_id.in_(farm_ids))
        count_query = select(func.count(MonitoringVisit.id)).where(MonitoringVisit.farm_id.in_(farm_ids))

        if farm_id is not None:
            query = query.where(MonitoringVisit.farm_id == farm_id)
            count_query = count_query.where(MonitoringVisit.farm_id == farm_id)
        if plot_id is not None:
            query = query.where(MonitoringVisit.plot_id == plot_id)
            count_query = count_query.where(MonitoringVisit.plot_id == plot_id)
        if crop_cycle_id is not None:
            query = query.where(MonitoringVisit.crop_cycle_id == crop_cycle_id)
            count_query = count_query.where(MonitoringVisit.crop_cycle_id == crop_cycle_id)
        if issue_type is not None:
            query = query.where(MonitoringVisit.issue_type == issue_type)
            count_query = count_query.where(MonitoringVisit.issue_type == issue_type)
        if severity is not None:
            query = query.where(MonitoringVisit.severity == severity)
            count_query = count_query.where(MonitoringVisit.severity == severity)
        if observed_from is not None:
            query = query.where(MonitoringVisit.observed_at >= observed_from)
            count_query = count_query.where(MonitoringVisit.observed_at >= observed_from)
        if observed_to is not None:
            query = query.where(MonitoringVisit.observed_at <= observed_to)
            count_query = count_query.where(MonitoringVisit.observed_at <= observed_to)

        total = int(self.db.scalar(count_query) or 0)
        query = query.order_by(MonitoringVisit.observed_at.desc(), MonitoringVisit.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(query).all())

    def get_by_id(self, visit_id: int) -> MonitoringVisit | None:
        return self.db.get(MonitoringVisit, visit_id)

    def update_fields(
        self,
        visit: MonitoringVisit,
        *,
        observed_at: datetime | None,
        bbch_stage: str | None,
        issue_type: str | None,
        severity: str | None,
        notes: str | None,
    ) -> MonitoringVisit:
        if observed_at is not None:
            visit.observed_at = observed_at
        visit.bbch_stage = bbch_stage
        visit.issue_type = issue_type
        visit.severity = severity
        visit.notes = notes
        self.db.flush()
        return visit
