from datetime import datetime

from pydantic import BaseModel, Field


class ReportExportCreateRequest(BaseModel):
    farm_id: int
    report_type: str = Field(min_length=2, max_length=60)
    format: str = Field(default='pdf', max_length=20)
    period_label: str | None = Field(default=None, max_length=80)
    file_url: str | None = None
    status: str = Field(default='generado', max_length=30)
    generated_at: datetime


class ReportExportOut(BaseModel):
    id: int
    farm_id: int
    report_type: str
    format: str
    period_label: str | None
    file_url: str | None
    status: str
    generated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportOverviewOut(BaseModel):
    farm_id: int
    total_harvests: int
    total_invoices: int
    total_exports: int
