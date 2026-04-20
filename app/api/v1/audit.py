from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit import AuditExportCreateRequest, AuditExportOut, AuditLogOut
from app.services.audit_service import AuditService

router = APIRouter()


@router.get('/logs', response_model=list[AuditLogOut])
def list_audit_logs(
    farm_id: int | None = Query(default=None),
    module: str | None = Query(default=None),
    action: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuditService(db).list_logs_for_user(user=user, farm_id=farm_id, module=module, action=action)


@router.post('/exports', response_model=AuditExportOut, status_code=201)
def create_audit_export(payload: AuditExportCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AuditService(db).create_export_for_user(user=user, farm_id=payload.farm_id, format=payload.format, module=payload.module, action=payload.action)


@router.get('/exports', response_model=list[AuditExportOut])
def list_audit_exports(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AuditService(db).list_exports_for_user(user)
