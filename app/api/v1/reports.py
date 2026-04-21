from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.reports import (
    ReportExportCreateRequest,
    ReportExportListResponse,
    ReportExportOut,
    ReportExportSignRequest,
    ReportExportStatusUpdateRequest,
    ReportExportUpdateRequest,
    ReportOverviewOut,
    ReportTypeSummaryListResponse,
)
from app.services.reports_service import ReportsService

router = APIRouter()


@router.get('/exports', response_model=ReportExportListResponse)
def list_report_exports(
    farm_id: int | None = Query(default=None, ge=1),
    report_type: str | None = None,
    status_value: str | None = Query(default=None, alias='status'),
    generated_from: datetime | None = None,
    generated_to: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ReportsService(db).list_exports_for_user(
        user=user,
        farm_id=farm_id,
        report_type=report_type,
        status_value=status_value,
        generated_from=generated_from,
        generated_to=generated_to,
        limit=limit,
        offset=offset,
    )


@router.post('/exports', response_model=ReportExportOut, status_code=201)
def create_report_export(payload: ReportExportCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).create_export_for_user(user=user, farm_id=payload.farm_id, report_type=payload.report_type, format=payload.format, period_label=payload.period_label, file_url=payload.file_url, status_value=payload.status, generated_at=payload.generated_at)


@router.get('/exports/{export_id}', response_model=ReportExportOut)
def get_report_export(export_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).get_export_for_user(user=user, export_id=export_id)


@router.put('/exports/{export_id}', response_model=ReportExportOut)
def update_report_export(export_id: int, payload: ReportExportUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).update_export_for_user(
        user=user,
        export_id=export_id,
        report_type=payload.report_type,
        format=payload.format,
        period_label=payload.period_label,
        file_url=payload.file_url,
        generated_at=payload.generated_at,
    )


@router.patch('/exports/{export_id}/status', response_model=ReportExportOut)
def update_report_export_status(export_id: int, payload: ReportExportStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).update_export_status_for_user(user=user, export_id=export_id, status_value=payload.status)




@router.patch('/exports/{export_id}/sign', response_model=ReportExportOut)
def sign_report_export(export_id: int, payload: ReportExportSignRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).sign_export_for_user(
        user=user,
        export_id=export_id,
        signed_by=payload.signed_by,
        signature_hash=payload.signature_hash,
        signed_at=payload.signed_at,
    )

@router.get('/summary', response_model=ReportTypeSummaryListResponse)
def get_report_summary_by_type(
    farm_id: int | None = Query(default=None, ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ReportsService(db).summary_by_type_for_user(user=user, farm_id=farm_id)


@router.get('/overview', response_model=ReportOverviewOut)
def get_report_overview(farm_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportsService(db).overview_for_user(user=user, farm_id=farm_id)


@router.get('/overview.csv')
def export_report_overview_csv(farm_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    csv_data = ReportsService(db).overview_csv_for_user(user=user, farm_id=farm_id)
    headers = {'Content-Disposition': f'attachment; filename="report_overview_farm_{farm_id}.csv"'}
    return Response(content=csv_data, media_type='text/csv; charset=utf-8', headers=headers)


@router.get('/overview.json')
def export_report_overview_json(farm_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = ReportsService(db).overview_json_for_user(user=user, farm_id=farm_id)
    headers = {'Content-Disposition': f'attachment; filename="report_overview_farm_{farm_id}.json"'}
    return JSONResponse(content=payload, headers=headers)


@router.get('/overview.xlsx')
def export_report_overview_xlsx(farm_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    xlsx_data = ReportsService(db).overview_xlsx_for_user(user=user, farm_id=farm_id)
    headers = {'Content-Disposition': f'attachment; filename="report_overview_farm_{farm_id}.xlsx"'}
    return Response(content=xlsx_data, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)


@router.get('/overview.pdf')
def export_report_overview_pdf(farm_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pdf_data = ReportsService(db).overview_pdf_for_user(user=user, farm_id=farm_id)
    headers = {'Content-Disposition': f'attachment; filename="report_overview_farm_{farm_id}.pdf"'}
    return Response(content=pdf_data, media_type='application/pdf', headers=headers)
