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

    def list_exports_by_farm_ids(self, farm_ids: list[int]) -> list[ReportExport]:
        if not farm_ids:
            return []
        q = select(ReportExport).where(ReportExport.farm_id.in_(farm_ids)).order_by(ReportExport.generated_at.desc(), ReportExport.id.desc())
        return list(self.db.scalars(q).all())

    def overview(self, farm_id: int) -> tuple[int, int, int]:
        harvests = self.db.execute(select(func.count(Harvest.id)).where(Harvest.farm_id == farm_id)).scalar_one()
        invoices = self.db.execute(select(func.count(Invoice.id)).where(Invoice.farm_id == farm_id)).scalar_one()
        exports = self.db.execute(select(func.count(ReportExport.id)).where(ReportExport.farm_id == farm_id)).scalar_one()
        return int(harvests), int(invoices), int(exports)
