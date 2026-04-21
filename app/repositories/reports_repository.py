from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.harvest import Harvest
from app.models.invoice import Invoice
from app.models.report_export import ReportExport


class ReportsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_export(self, *, farm_id: int, report_type: str, format: str, period_label: str | None, file_url: str | None, status: str, generated_at: datetime) -> ReportExport:
        export = ReportExport(
            farm_id=farm_id,
            report_type=report_type,
            format=format,
            period_label=period_label,
            file_url=file_url,
            status=status,
            generated_at=generated_at,
        )
        self.db.add(export)
        self.db.flush()
        return export

    def list_exports_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        report_type: str | None = None,
        status: str | None = None,
        generated_from: datetime | None = None,
        generated_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[ReportExport]]:
        if not farm_ids:
            return 0, []

        q = select(ReportExport).where(ReportExport.farm_id.in_(farm_ids))
        count_q = select(func.count(ReportExport.id)).where(ReportExport.farm_id.in_(farm_ids))

        if farm_id is not None:
            q = q.where(ReportExport.farm_id == farm_id)
            count_q = count_q.where(ReportExport.farm_id == farm_id)
        if report_type is not None:
            q = q.where(ReportExport.report_type == report_type)
            count_q = count_q.where(ReportExport.report_type == report_type)
        if status is not None:
            q = q.where(ReportExport.status == status)
            count_q = count_q.where(ReportExport.status == status)
        if generated_from is not None:
            q = q.where(ReportExport.generated_at >= generated_from)
            count_q = count_q.where(ReportExport.generated_at >= generated_from)
        if generated_to is not None:
            q = q.where(ReportExport.generated_at <= generated_to)
            count_q = count_q.where(ReportExport.generated_at <= generated_to)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(ReportExport.generated_at.desc(), ReportExport.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def summary_by_report_type(self, *, farm_ids: list[int], farm_id: int | None = None) -> list[tuple[str, int]]:
        if not farm_ids:
            return []
        q = (
            select(ReportExport.report_type, func.count(ReportExport.id))
            .where(ReportExport.farm_id.in_(farm_ids))
            .group_by(ReportExport.report_type)
            .order_by(func.count(ReportExport.id).desc(), ReportExport.report_type.asc())
        )
        if farm_id is not None:
            q = q.where(ReportExport.farm_id == farm_id)
        return [(str(row[0]), int(row[1])) for row in self.db.execute(q).all()]

    def get_export_by_id(self, export_id: int) -> ReportExport | None:
        return self.db.get(ReportExport, export_id)

    def update_export_fields(
        self,
        export: ReportExport,
        *,
        report_type: str | None = None,
        format: str | None = None,
        period_label: str | None = None,
        file_url: str | None = None,
        generated_at: datetime | None = None,
    ) -> ReportExport:
        if report_type is not None:
            export.report_type = report_type
        if format is not None:
            export.format = format
        if period_label is not None:
            export.period_label = period_label
        if file_url is not None:
            export.file_url = file_url
        if generated_at is not None:
            export.generated_at = generated_at
        self.db.add(export)
        return export


    def sign_export(
        self,
        export: ReportExport,
        *,
        signed_by: str,
        signature_hash: str,
        signed_at: datetime,
    ) -> ReportExport:
        export.signed_by = signed_by
        export.signature_hash = signature_hash
        export.signed_at = signed_at
        export.status = 'firmado'
        self.db.add(export)
        return export

    def overview(self, farm_id: int) -> tuple[int, int, int]:
        harvests = self.db.execute(select(func.count(Harvest.id)).where(Harvest.farm_id == farm_id)).scalar_one()
        invoices = self.db.execute(select(func.count(Invoice.id)).where(Invoice.farm_id == farm_id)).scalar_one()
        exports = self.db.execute(select(func.count(ReportExport.id)).where(ReportExport.farm_id == farm_id)).scalar_one()
        return int(harvests), int(invoices), int(exports)
