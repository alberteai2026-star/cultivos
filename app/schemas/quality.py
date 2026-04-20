from datetime import datetime

from pydantic import BaseModel, Field


class QualityTestCreateRequest(BaseModel):
    farm_id: int
    plot_id: int | None = None
    harvest_id: int | None = None
    test_type: str = Field(min_length=2, max_length=80)
    result_value: str = Field(min_length=1, max_length=120)
    status: str = Field(default='ok', max_length=30)
    tested_at: datetime


class QualityTestOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    harvest_id: int | None
    test_type: str
    result_value: str
    status: str
    tested_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class CertificationCreateRequest(BaseModel):
    farm_id: int
    name: str = Field(min_length=2, max_length=120)
    issuer: str | None = Field(default=None, max_length=120)
    valid_until: datetime | None = None


class CertificationOut(BaseModel):
    id: int
    farm_id: int
    name: str
    issuer: str | None
    valid_until: datetime | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
