from datetime import datetime

from pydantic import BaseModel, Field


class AuditLogOut(BaseModel):
    id: int
    user_id: int | None
    farm_id: int | None
    module: str
    action: str
    record_id: str | None
    metadata_json: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditExportCreateRequest(BaseModel):
    farm_id: int | None = None
    format: str = Field(default='csv', max_length=20)
    module: str | None = Field(default=None, max_length=80)
    action: str | None = Field(default=None, max_length=50)


class AuditExportOut(BaseModel):
    id: int
    user_id: int
    farm_id: int | None
    format: str
    filters_json: str | None
    file_url: str | None
    signature: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
