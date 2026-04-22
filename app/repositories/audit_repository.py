from datetime import datetime

import json

from sqlalchemy import func, select
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

    def list_logs(
        self,
        *,
        farm_ids: list[int],
        farm_id: int | None,
        module: str | None,
        action: str | None,
        limit: int,
        offset: int,
    ) -> tuple[int, list[AuditLog]]:
        q = select(AuditLog)
        count_q = select(func.count(AuditLog.id))

        if farm_ids:
            condition = (AuditLog.farm_id.is_(None)) | (AuditLog.farm_id.in_(farm_ids))
            q = q.where(condition)
            count_q = count_q.where(condition)
        if farm_id is not None:
            q = q.where(AuditLog.farm_id == farm_id)
            count_q = count_q.where(AuditLog.farm_id == farm_id)
        if module is not None:
            q = q.where(AuditLog.module == module)
            count_q = count_q.where(AuditLog.module == module)
        if action is not None:
            q = q.where(AuditLog.action == action)
            count_q = count_q.where(AuditLog.action == action)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(AuditLog.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def summary_logs(
        self,
        *,
        farm_ids: list[int],
        farm_id: int | None = None,
        module: str | None = None,
        action: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> list[tuple[str, str, int]]:
        q = select(AuditLog.module, AuditLog.action, func.count(AuditLog.id))
        if farm_ids:
            condition = (AuditLog.farm_id.is_(None)) | (AuditLog.farm_id.in_(farm_ids))
            q = q.where(condition)
        if farm_id is not None:
            q = q.where(AuditLog.farm_id == farm_id)
        if module is not None:
            q = q.where(AuditLog.module == module)
        if action is not None:
            q = q.where(AuditLog.action == action)
        if created_from is not None:
            q = q.where(AuditLog.created_at >= created_from)
        if created_to is not None:
            q = q.where(AuditLog.created_at <= created_to)

        q = q.group_by(AuditLog.module, AuditLog.action).order_by(func.count(AuditLog.id).desc(), AuditLog.module.asc(), AuditLog.action.asc())
        return [(str(row[0]), str(row[1]), int(row[2])) for row in self.db.execute(q).all()]

    def create_export(
        self,
        *,
        user_id: int,
        farm_id: int | None,
        format: str,
        filters_json: str | None,
        file_url: str | None,
        signature: str | None,
    ) -> AuditExport:
        export = AuditExport(
            user_id=user_id,
            farm_id=farm_id,
            format=format,
            filters_json=filters_json,
            file_url=file_url,
            signature=signature,
        )
        self.db.add(export)
        self.db.flush()
        return export

    def list_exports(
        self,
        *,
        user_id: int,
        farm_ids: list[int],
        limit: int,
        offset: int,
    ) -> tuple[int, list[AuditExport]]:
        q = select(AuditExport).where(AuditExport.user_id == user_id)
        count_q = select(func.count(AuditExport.id)).where(AuditExport.user_id == user_id)

        if farm_ids:
            condition = (AuditExport.farm_id.is_(None)) | (AuditExport.farm_id.in_(farm_ids))
            q = q.where(condition)
            count_q = count_q.where(condition)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(AuditExport.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_export_by_id(self, export_id: int) -> AuditExport | None:
        return self.db.get(AuditExport, export_id)

    def update_export_fields(
        self,
        export: AuditExport,
        *,
        format: str | None = None,
        file_url: str | None = None,
        signature: str | None = None,
    ) -> AuditExport:
        if format is not None:
            export.format = format
        if file_url is not None:
            export.file_url = file_url
        if signature is not None:
            export.signature = signature
        self.db.add(export)
        return export


    def update_export_status(
        self,
        export: AuditExport,
        *,
        status: str,
        error_message: str | None,
        completed_at: datetime | None,
    ) -> AuditExport:
        export.status = status
        if error_message is not None:
            export.error_message = error_message
        if completed_at is not None:
            export.completed_at = completed_at
        self.db.add(export)
        return export
