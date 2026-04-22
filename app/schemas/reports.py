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


class ReportExportUpdateRequest(BaseModel):
    report_type: str | None = Field(default=None, min_length=2, max_length=60)
    format: str | None = Field(default=None, max_length=20)
    period_label: str | None = Field(default=None, max_length=80)
    file_url: str | None = None
    generated_at: datetime | None = None


class ReportExportStatusUpdateRequest(BaseModel):
    status: str = Field(min_length=2, max_length=30)


class ReportExportSignRequest(BaseModel):
    signed_by: str = Field(min_length=2, max_length=120)
    signature_hash: str = Field(min_length=8, max_length=160)
    signed_at: datetime | None = None


class ReportExportOut(BaseModel):
    id: int
    farm_id: int
    report_type: str
    format: str
    period_label: str | None
    file_url: str | None
    status: str
    generated_at: datetime
    signed_by: str | None
    signature_hash: str | None
    signed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportExportListResponse(BaseModel):
    total: int
    items: list[ReportExportOut]


class ReportTemplateCreateRequest(BaseModel):
    farm_id: int
    template_name: str = Field(min_length=2, max_length=120)
    report_type: str = Field(min_length=2, max_length=60)
    format: str = Field(default='pdf', max_length=20)
    filters_json: str | None = None
    is_active: bool = True


class ReportTemplateUpdateRequest(BaseModel):
    template_name: str | None = Field(default=None, min_length=2, max_length=120)
    report_type: str | None = Field(default=None, min_length=2, max_length=60)
    format: str | None = Field(default=None, max_length=20)
    filters_json: str | None = None
    is_active: bool | None = None


class ReportTemplateOut(BaseModel):
    id: int
    farm_id: int
    template_name: str
    report_type: str
    format: str
    filters_json: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportTemplateListResponse(BaseModel):
    total: int
    items: list[ReportTemplateOut]


class ReportTemplateGenerateRequest(BaseModel):
    period_label: str | None = Field(default=None, max_length=80)
    generated_at: datetime | None = None


class ReportOverviewOut(BaseModel):
    farm_id: int
    total_harvests: int
    total_invoices: int
    total_exports: int


class ReportTypeSummaryOut(BaseModel):
    report_type: str
    total: int


class ReportTypeSummaryListResponse(BaseModel):
    total_types: int
    items: list[ReportTypeSummaryOut]
