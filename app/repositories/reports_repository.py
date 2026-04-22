from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.harvest import Harvest
from app.models.invoice import Invoice
from app.models.report_export import ReportExport
from app.models.report_template import ReportTemplate


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

    def create_template(
        self,
        *,
        farm_id: int,
        template_name: str,
        report_type: str,
        format: str,
        filters_json: str | None,
        is_active: bool,
    ) -> ReportTemplate:
        template = ReportTemplate(
            farm_id=farm_id,
            template_name=template_name,
            report_type=report_type,
            format=format,
            filters_json=filters_json,
            is_active=is_active,
        )
        self.db.add(template)
        self.db.flush()
        return template

    def list_templates_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        report_type: str | None = None,
        is_active: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[ReportTemplate]]:
        if not farm_ids:
            return 0, []

        q = select(ReportTemplate).where(ReportTemplate.farm_id.in_(farm_ids))
        count_q = select(func.count(ReportTemplate.id)).where(ReportTemplate.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(ReportTemplate.farm_id == farm_id)
            count_q = count_q.where(ReportTemplate.farm_id == farm_id)
        if report_type is not None:
            q = q.where(ReportTemplate.report_type == report_type)
            count_q = count_q.where(ReportTemplate.report_type == report_type)
        if is_active is not None:
            q = q.where(ReportTemplate.is_active == is_active)
            count_q = count_q.where(ReportTemplate.is_active == is_active)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(ReportTemplate.updated_at.desc(), ReportTemplate.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_template_by_id(self, template_id: int) -> ReportTemplate | None:
        return self.db.get(ReportTemplate, template_id)

    def update_template_fields(
        self,
        template: ReportTemplate,
        *,
        template_name: str | None = None,
        report_type: str | None = None,
        format: str | None = None,
        filters_json: str | None = None,
        is_active: bool | None = None,
    ) -> ReportTemplate:
        if template_name is not None:
            template.template_name = template_name
        if report_type is not None:
            template.report_type = report_type
        if format is not None:
            template.format = format
        if filters_json is not None:
            template.filters_json = filters_json
        if is_active is not None:
            template.is_active = is_active
        self.db.add(template)
        return template

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
