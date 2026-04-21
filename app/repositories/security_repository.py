from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.security_incident import SecurityIncident


class SecurityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_incident(
        self,
        *,
        farm_id: int,
        alert_type: str,
        severity: str,
        description: str | None,
        detected_at: datetime,
    ) -> SecurityIncident:
        incident = SecurityIncident(
            farm_id=farm_id,
            alert_type=alert_type,
            severity=severity,
            status='abierta',
            description=description,
            detected_at=detected_at,
        )
        self.db.add(incident)
        self.db.flush()
        return incident

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        status_value: str | None = None,
        severity: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[SecurityIncident]]:
        if not farm_ids:
            return 0, []
        q = select(SecurityIncident).where(SecurityIncident.farm_id.in_(farm_ids))
        count_q = select(func.count(SecurityIncident.id)).where(SecurityIncident.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(SecurityIncident.farm_id == farm_id)
            count_q = count_q.where(SecurityIncident.farm_id == farm_id)
        if status_value is not None:
            q = q.where(SecurityIncident.status == status_value)
            count_q = count_q.where(SecurityIncident.status == status_value)
        if severity is not None:
            q = q.where(SecurityIncident.severity == severity)
            count_q = count_q.where(SecurityIncident.severity == severity)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(SecurityIncident.detected_at.desc(), SecurityIncident.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, incident_id: int) -> SecurityIncident | None:
        return self.db.get(SecurityIncident, incident_id)
