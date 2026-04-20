from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.reports import ReportExportCreateRequest, ReportExportOut, ReportOverviewOut
from app.services.reports_service import ReportsService

router = APIRouter()


@router.get('/exports', response_model=list[ReportExportOut])
def list_report_exports(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).list_exports_for_user(user)


@router.post('/exports', response_model=ReportExportOut, status_code=201)
def create_report_export(payload: ReportExportCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).create_export_for_user(user=user, farm_id=payload.farm_id, report_type=payload.report_type, format=payload.format, period_label=payload.period_label, file_url=payload.file_url, status_value=payload.status, generated_at=payload.generated_at)


@router.get('/overview', response_model=ReportOverviewOut)
def get_report_overview(farm_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).overview_for_user(user=user, farm_id=farm_id)
