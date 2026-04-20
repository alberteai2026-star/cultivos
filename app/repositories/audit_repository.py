import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_export import AuditExport
from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(
        self,
        *,
        module: str,
        action: str,
        user_id: int | None = None,
        farm_id: int | None = None,
        record_id: str | None = None,
        metadata: dict | None = None,
    ) -> AuditLog:
        event = AuditLog(
            user_id=user_id,
            farm_id=farm_id,
            module=module,
            action=action,
            record_id=record_id,
            metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
        )
        self.db.add(event)
        self.db.flush()
        return event


    def list_logs(self, *, farm_ids: list[int], farm_id: int | None, module: str | None, action: str | None) -> list[AuditLog]:
        q = select(AuditLog)
        if farm_ids:
            q = q.where((AuditLog.farm_id.is_(None)) | (AuditLog.farm_id.in_(farm_ids)))
        if farm_id is not None:
            q = q.where(AuditLog.farm_id == farm_id)
        if module is not None:
            q = q.where(AuditLog.module == module)
        if action is not None:
            q = q.where(AuditLog.action == action)
        q = q.order_by(AuditLog.id.desc())
        return list(self.db.scalars(q).all())

    def create_export(self, *, user_id: int, farm_id: int | None, format: str, filters_json: str | None, file_url: str | None, signature: str | None) -> AuditExport:
        export = AuditExport(user_id=user_id, farm_id=farm_id, format=format, filters_json=filters_json, file_url=file_url, signature=signature)
        self.db.add(export)
        self.db.flush()
        return export

    def list_exports(self, *, user_id: int, farm_ids: list[int]) -> list[AuditExport]:
        q = select(AuditExport).where(AuditExport.user_id == user_id)
        if farm_ids:
            q = q.where((AuditExport.farm_id.is_(None)) | (AuditExport.farm_id.in_(farm_ids)))
        q = q.order_by(AuditExport.id.desc())
        return list(self.db.scalars(q).all())
