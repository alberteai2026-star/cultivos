import hashlib
import json
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.audit import AuditExportListResponse, AuditExportOut, AuditLogListResponse, AuditLogOut


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditRepository(db)
        self.relations = UserFarmRoleRepository(db)

    def list_logs_for_user(
        self,
        *,
        user: User,
        farm_id: int | None,
        module: str | None,
        action: str | None,
        limit: int,
        offset: int,
    ) -> AuditLogListResponse:
        if farm_id is not None and not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        allowed_farms = self.relations.list_farm_ids_by_user(user.id)
        total, logs = self.audit.list_logs(
            farm_ids=allowed_farms,
            farm_id=farm_id,
            module=module,
            action=action,
            limit=limit,
            offset=offset,
        )
        items = [self._to_log_out(log) for log in logs]
        return AuditLogListResponse(total=total, items=items)

    def create_export_for_user(self, *, user: User, farm_id: int | None, format: str, module: str | None, action: str | None) -> AuditExportOut:
        if farm_id is not None and not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        filters = {'farm_id': farm_id, 'module': module, 'action': action}
        digest = hashlib.sha256(json.dumps(filters, sort_keys=True).encode('utf-8')).hexdigest()
        export = self.audit.create_export(
            user_id=user.id,
            farm_id=farm_id,
            format=format,
            filters_json=json.dumps(filters, ensure_ascii=False),
            file_url=None,
            signature=digest,
        )
        self.db.commit()
        self.db.refresh(export)
        return self._to_export_out(export)

    def list_exports_for_user(self, *, user: User, limit: int, offset: int) -> AuditExportListResponse:
        allowed_farms = self.relations.list_farm_ids_by_user(user.id)
        total, exports = self.audit.list_exports(user_id=user.id, farm_ids=allowed_farms, limit=limit, offset=offset)
        items = [self._to_export_out(item) for item in exports]
        return AuditExportListResponse(total=total, items=items)

    def get_export_for_user(self, *, user: User, export_id: int) -> AuditExportOut:
        export = self.audit.get_export_by_id(export_id)
        if not export:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Exportación de auditoría no encontrada')
        if export.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta exportación')
        if export.farm_id is not None and not self.relations.user_has_farm(user_id=user.id, farm_id=export.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return self._to_export_out(export)

    def update_export_for_user(
        self,
        *,
        user: User,
        export_id: int,
        format: str | None,
        file_url: str | None,
        signature: str | None,
    ) -> AuditExportOut:
        export = self.audit.get_export_by_id(export_id)
        if not export:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Exportación de auditoría no encontrada')
        if export.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta exportación')
        if export.farm_id is not None and not self.relations.user_has_farm(user_id=user.id, farm_id=export.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        updated = self.audit.update_export_fields(export, format=format, file_url=file_url, signature=signature)
        self.audit.add(module='audit', action='update_export', user_id=user.id, farm_id=updated.farm_id, record_id=str(updated.id))
        self.db.commit()
        self.db.refresh(updated)
        return self._to_export_out(updated)



    def update_export_status_for_user(
        self,
        *,
        user: User,
        export_id: int,
        status_value: str,
        error_message: str | None,
        completed_at: datetime | None,
    ) -> AuditExportOut:
        export = self.audit.get_export_by_id(export_id)
        if not export:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Exportación de auditoría no encontrada')
        if export.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta exportación')
        if export.farm_id is not None and not self.relations.user_has_farm(user_id=user.id, farm_id=export.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        allowed_transitions = {
            'solicitado': {'procesando', 'fallido'},
            'procesando': {'completado', 'fallido'},
            'completado': set(),
            'fallido': {'procesando'},
        }
        current = export.status or 'solicitado'
        if status_value != current and status_value not in allowed_transitions.get(current, set()):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Transición de estado no permitida')

        effective_completed_at = completed_at
        if status_value == 'completado' and effective_completed_at is None:
            effective_completed_at = datetime.utcnow()

        updated = self.audit.update_export_status(
            export,
            status=status_value,
            error_message=error_message,
            completed_at=effective_completed_at,
        )
        self.audit.add(module='audit', action='update_export_status', user_id=user.id, farm_id=updated.farm_id, record_id=str(updated.id))
        self.db.commit()
        self.db.refresh(updated)
        return self._to_export_out(updated)

    @staticmethod
    def _safe_load_json(raw: str | None) -> dict[str, Any] | None:
        if not raw:
            return None
        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return loaded if isinstance(loaded, dict) else None

    def _to_log_out(self, row) -> AuditLogOut:
        return AuditLogOut(
            id=row.id,
            user_id=row.user_id,
            farm_id=row.farm_id,
            module=row.module,
            action=row.action,
            record_id=row.record_id,
            metadata=self._safe_load_json(row.metadata_json),
            created_at=row.created_at,
        )

    def _to_export_out(self, row) -> AuditExportOut:
        return AuditExportOut(
            id=row.id,
            user_id=row.user_id,
            farm_id=row.farm_id,
            format=row.format,
            filters=self._safe_load_json(row.filters_json),
            file_url=row.file_url,
            signature=row.signature,
            status=row.status,
            error_message=row.error_message,
            completed_at=row.completed_at,
            created_at=row.created_at,
        )
