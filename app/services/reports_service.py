import csv
import io
import zipfile
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.reports_repository import ReportsRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.reports import (
    ReportExportListResponse,
    ReportOverviewOut,
    ReportTemplateListResponse,
    ReportTypeSummaryListResponse,
    ReportTypeSummaryOut,
)


class ReportsService:
    def __init__(self, db: Session):
        self.db = db
        self.reports = ReportsRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_exports_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        report_type: str | None = None,
        status_value: str | None = None,
        generated_from: datetime | None = None,
        generated_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ReportExportListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro offset debe ser mayor o igual a 0')
        if generated_from is not None and generated_to is not None and generated_from > generated_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Rango de fechas inválido')
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        total, exports = self.reports.list_exports_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            report_type=report_type,
            status=status_value,
            generated_from=generated_from,
            generated_to=generated_to,
            limit=limit,
            offset=offset,
        )
        return ReportExportListResponse(total=total, items=exports)

    def create_export_for_user(self, *, user: User, farm_id: int, report_type: str, format: str, period_label: str | None, file_url: str | None, status_value: str, generated_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        export = self.reports.create_export(farm_id=farm_id, report_type=report_type, format=format, period_label=period_label, file_url=file_url, status=status_value, generated_at=generated_at)
        self.audit.add(module='reports', action='create_export', user_id=user.id, farm_id=farm_id, record_id=str(export.id))
        self.db.commit()
        self.db.refresh(export)
        return export

    def list_templates_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        report_type: str | None = None,
        is_active: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ReportTemplateListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro offset debe ser mayor o igual a 0')

        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        total, items = self.reports.list_templates_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            report_type=report_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        return ReportTemplateListResponse(total=total, items=items)

    def create_template_for_user(
        self,
        *,
        user: User,
        farm_id: int,
        template_name: str,
        report_type: str,
        format: str,
        filters_json: str | None,
        is_active: bool = True,
    ):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        template = self.reports.create_template(
            farm_id=farm_id,
            template_name=template_name,
            report_type=report_type,
            format=format,
            filters_json=filters_json,
            is_active=is_active,
        )
        self.audit.add(module='reports', action='create_template', user_id=user.id, farm_id=farm_id, record_id=str(template.id))
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_template_for_user(self, *, user: User, template_id: int):
        template = self.reports.get_template_by_id(template_id)
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Plantilla no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=template.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return template

    def update_template_for_user(
        self,
        *,
        user: User,
        template_id: int,
        template_name: str | None,
        report_type: str | None,
        format: str | None,
        filters_json: str | None,
        is_active: bool | None,
    ):
        template = self.get_template_for_user(user=user, template_id=template_id)
        updated = self.reports.update_template_fields(
            template,
            template_name=template_name,
            report_type=report_type,
            format=format,
            filters_json=filters_json,
            is_active=is_active,
        )
        self.audit.add(module='reports', action='update_template', user_id=user.id, farm_id=template.farm_id, record_id=str(template.id))
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def generate_export_from_template_for_user(
        self,
        *,
        user: User,
        template_id: int,
        period_label: str | None = None,
        generated_at: datetime | None = None,
    ):
        template = self.get_template_for_user(user=user, template_id=template_id)
        if not template.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='La plantilla está inactiva')

        export = self.reports.create_export(
            farm_id=template.farm_id,
            report_type=template.report_type,
            format=template.format,
            period_label=period_label,
            file_url=None,
            status='generado',
            generated_at=generated_at or datetime.utcnow(),
        )
        self.audit.add(
            module='reports',
            action='generate_export_from_template',
            user_id=user.id,
            farm_id=template.farm_id,
            record_id=f'{template.id}:{export.id}',
        )
        self.db.commit()
        self.db.refresh(export)
        return export

    def get_export_for_user(self, *, user: User, export_id: int):
        export = self.reports.get_export_by_id(export_id)
        if not export:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Exportación no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=export.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return export

    def update_export_for_user(
        self,
        *,
        user: User,
        export_id: int,
        report_type: str | None,
        format: str | None,
        period_label: str | None,
        file_url: str | None,
        generated_at: datetime | None,
    ):
        export = self.get_export_for_user(user=user, export_id=export_id)
        updated = self.reports.update_export_fields(
            export,
            report_type=report_type,
            format=format,
            period_label=period_label,
            file_url=file_url,
            generated_at=generated_at,
        )
        self.audit.add(module='reports', action='update_export', user_id=user.id, farm_id=export.farm_id, record_id=str(export.id))
        self.db.commit()
        self.db.refresh(updated)
        return updated


    def sign_export_for_user(self, *, user: User, export_id: int, signed_by: str, signature_hash: str, signed_at: datetime | None = None):
        export = self.get_export_for_user(user=user, export_id=export_id)
        signed = self.reports.sign_export(
            export,
            signed_by=signed_by,
            signature_hash=signature_hash,
            signed_at=signed_at or datetime.utcnow(),
        )
        self.audit.add(module='reports', action='sign_export', user_id=user.id, farm_id=export.farm_id, record_id=str(export.id))
        self.db.commit()
        self.db.refresh(signed)
        return signed

    def update_export_status_for_user(self, *, user: User, export_id: int, status_value: str):
        export = self.get_export_for_user(user=user, export_id=export_id)
        export.status = status_value
        self.audit.add(module='reports', action='update_export_status', user_id=user.id, farm_id=export.farm_id, record_id=str(export.id))
        self.db.commit()
        self.db.refresh(export)
        return export

    def summary_by_type_for_user(self, *, user: User, farm_id: int | None = None) -> ReportTypeSummaryListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        rows = self.reports.summary_by_report_type(farm_ids=farm_ids, farm_id=farm_id)
        items = [ReportTypeSummaryOut(report_type=report_type, total=total) for report_type, total in rows]
        return ReportTypeSummaryListResponse(total_types=len(items), items=items)

    def overview_for_user(self, *, user: User, farm_id: int) -> ReportOverviewOut:
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total_harvests, total_invoices, total_exports = self.reports.overview(farm_id)
        return ReportOverviewOut(farm_id=farm_id, total_harvests=total_harvests, total_invoices=total_invoices, total_exports=total_exports)

    def overview_csv_for_user(self, *, user: User, farm_id: int) -> str:
        overview = self.overview_for_user(user=user, farm_id=farm_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['farm_id', 'total_harvests', 'total_invoices', 'total_exports'])
        writer.writerow([overview.farm_id, overview.total_harvests, overview.total_invoices, overview.total_exports])
        return output.getvalue()

    def overview_json_for_user(self, *, user: User, farm_id: int) -> dict:
        overview = self.overview_for_user(user=user, farm_id=farm_id)
        return overview.model_dump()


    def overview_pdf_for_user(self, *, user: User, farm_id: int) -> bytes:
        overview = self.overview_for_user(user=user, farm_id=farm_id)
        lines = [
            'Reporte General de Finca',
            f'Finca: {overview.farm_id}',
            f'Total Cosechas: {overview.total_harvests}',
            f'Total Facturas: {overview.total_invoices}',
            f'Total Exportaciones: {overview.total_exports}',
            f'Generado: {datetime.utcnow().isoformat()}Z',
        ]
        return self._build_simple_pdf(lines)

    def overview_xlsx_for_user(self, *, user: User, farm_id: int) -> bytes:
        overview = self.overview_for_user(user=user, farm_id=farm_id)
        rows = [
            ['farm_id', 'total_harvests', 'total_invoices', 'total_exports'],
            [str(overview.farm_id), str(overview.total_harvests), str(overview.total_invoices), str(overview.total_exports)],
        ]
        return self._build_simple_xlsx(rows)

    @staticmethod
    def _build_simple_pdf(lines: list[str]) -> bytes:
        escaped = [line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)') for line in lines]
        stream_lines = ['BT', '/F1 12 Tf', '50 780 Td']
        for idx, line in enumerate(escaped):
            if idx == 0:
                stream_lines.append(f'({line}) Tj')
            else:
                stream_lines.append('0 -18 Td')
                stream_lines.append(f'({line}) Tj')
        stream_lines.append('ET')
        stream = '\n'.join(stream_lines).encode('latin-1', errors='replace')

        objects = [
            b'1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n',
            b'2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n',
            b'3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n',
            b'4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n',
            f'5 0 obj << /Length {len(stream)} >> stream\n'.encode('latin-1') + stream + b'\nendstream endobj\n',
        ]

        buffer = io.BytesIO()
        buffer.write(b'%PDF-1.4\n')
        offsets = [0]
        for obj in objects:
            offsets.append(buffer.tell())
            buffer.write(obj)

        xref_start = buffer.tell()
        buffer.write(f'xref\n0 {len(offsets)}\n'.encode('latin-1'))
        buffer.write(b'0000000000 65535 f \n')
        for offset in offsets[1:]:
            buffer.write(f'{offset:010d} 00000 n \n'.encode('latin-1'))

        buffer.write(
            f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF'.encode('latin-1')
        )
        return buffer.getvalue()

    @staticmethod
    def _build_simple_xlsx(rows: list[list[str]]) -> bytes:
        def col_name(idx: int) -> str:
            name = ''
            idx += 1
            while idx > 0:
                idx, rem = divmod(idx - 1, 26)
                name = chr(65 + rem) + name
            return name

        sheet_rows = []
        for r_idx, row in enumerate(rows, start=1):
            cells = []
            for c_idx, value in enumerate(row):
                ref = f'{col_name(c_idx)}{r_idx}'
                safe = (value or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{safe}</t></is></c>')
            sheet_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')

        sheet_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<sheetData>{"".join(sheet_rows)}</sheetData>'
            '</worksheet>'
        )

        workbook_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Overview" sheetId="1" r:id="rId1"/></sheets></workbook>'
        )

        rels_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'
        )

        workbook_rels_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>'
        )

        content_types_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>'
        )

        output = io.BytesIO()
        with zipfile.ZipFile(output, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', content_types_xml)
            zf.writestr('_rels/.rels', rels_xml)
            zf.writestr('xl/workbook.xml', workbook_xml)
            zf.writestr('xl/_rels/workbook.xml.rels', workbook_rels_xml)
            zf.writestr('xl/worksheets/sheet1.xml', sheet_xml)
        return output.getvalue()
