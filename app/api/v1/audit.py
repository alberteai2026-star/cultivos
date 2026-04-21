from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit import (
    AuditExportCreateRequest,
    AuditExportListResponse,
    AuditExportOut,
    AuditExportStatusUpdateRequest,
    AuditExportUpdateRequest,
    AuditLogListResponse,
)
from app.services.audit_service import AuditService

router = APIRouter()


@router.get('/logs', response_model=AuditLogListResponse)
def list_audit_logs(
    farm_id: int | None = Query(default=None),
    module: str | None = Query(default=None),
    action: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuditService(db).list_logs_for_user(
        user=user,
        farm_id=farm_id,
        module=module,
        action=action,
        limit=limit,
        offset=offset,
    )


@router.post('/exports', response_model=AuditExportOut, status_code=201)
def create_audit_export(payload: AuditExportCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AuditService(db).create_export_for_user(
        user=user,
        farm_id=payload.farm_id,
        format=payload.format,
        module=payload.module,
        action=payload.action,
    )


@router.get('/exports', response_model=AuditExportListResponse)
def list_audit_exports(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuditService(db).list_exports_for_user(user=user, limit=limit, offset=offset)


@router.get('/exports/{export_id}', response_model=AuditExportOut)
def get_audit_export(export_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AuditService(db).get_export_for_user(user=user, export_id=export_id)


@router.patch('/exports/{export_id}', response_model=AuditExportOut)
def update_audit_export(export_id: int, payload: AuditExportUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AuditService(db).update_export_for_user(
        user=user,
        export_id=export_id,
        format=payload.format,
        file_url=payload.file_url,
        signature=payload.signature,
    )


@router.patch('/exports/{export_id}/status', response_model=AuditExportOut)
def update_audit_export_status(export_id: int, payload: AuditExportStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AuditService(db).update_export_status_for_user(
        user=user,
        export_id=export_id,
        status_value=payload.status,
        error_message=payload.error_message,
        completed_at=payload.completed_at,
    )
