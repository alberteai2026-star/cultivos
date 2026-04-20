from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.reports_repository import ReportsRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.reports import ReportOverviewOut


class ReportsService:
    def __init__(self, db: Session):
        self.db = db
        self.reports = ReportsRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_exports_for_user(self, user: User):
        return self.reports.list_exports_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_export_for_user(self, *, user: User, farm_id: int, report_type: str, format: str, period_label: str | None, file_url: str | None, status_value: str, generated_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        export = self.reports.create_export(farm_id=farm_id, report_type=report_type, format=format, period_label=period_label, file_url=file_url, status=status_value, generated_at=generated_at)
        self.audit.add(module='reports', action='create_export', user_id=user.id, farm_id=farm_id, record_id=str(export.id))
        self.db.commit(); self.db.refresh(export)
        return export

    def overview_for_user(self, *, user: User, farm_id: int) -> ReportOverviewOut:
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total_harvests, total_invoices, total_exports = self.reports.overview(farm_id)
        return ReportOverviewOut(farm_id=farm_id, total_harvests=total_harvests, total_invoices=total_invoices, total_exports=total_exports)

    def overview_csv_for_user(self, *, user: User, farm_id: int) -> str:
        overview = self.overview_for_user(user=user, farm_id=farm_id)
        rows = [
            'farm_id,total_harvests,total_invoices,total_exports',
            f'{overview.farm_id},{overview.total_harvests},{overview.total_invoices},{overview.total_exports}',
        ]
        return '\n'.join(rows) + '\n'
