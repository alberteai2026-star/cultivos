from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditLogOut(BaseModel):
    id: int
    user_id: int | None
    farm_id: int | None
    module: str
    action: str
    record_id: str | None
    metadata: dict[str, Any] | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    total: int
    items: list[AuditLogOut]


class AuditExportCreateRequest(BaseModel):
    farm_id: int | None = None
    format: str = Field(default='csv', max_length=20)
    module: str | None = Field(default=None, max_length=80)
    action: str | None = Field(default=None, max_length=50)


class AuditExportUpdateRequest(BaseModel):
    format: str | None = Field(default=None, max_length=20)
    file_url: str | None = None
    signature: str | None = Field(default=None, max_length=160)


class AuditExportStatusUpdateRequest(BaseModel):
    status: str = Field(pattern='^(solicitado|procesando|completado|fallido)$')
    error_message: str | None = None
    completed_at: datetime | None = None


class AuditExportOut(BaseModel):
    id: int
    user_id: int
    farm_id: int | None
    format: str
    filters: dict[str, Any] | None
    file_url: str | None
    signature: str | None
    status: str
    error_message: str | None
    completed_at: datetime | None
    created_at: datetime


class AuditExportListResponse(BaseModel):
    total: int
    items: list[AuditExportOut]
