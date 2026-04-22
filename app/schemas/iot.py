from datetime import datetime

from pydantic import BaseModel, Field


class IoTDeviceCreateRequest(BaseModel):
    farm_id: int
    plot_id: int | None = None
    name: str = Field(min_length=2, max_length=120)
    device_type: str = Field(min_length=2, max_length=60)
    status: str = Field(default='active', max_length=30)


class IoTDeviceOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    name: str
    device_type: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IoTDeviceListResponse(BaseModel):
    total: int
    items: list[IoTDeviceOut]


class IoTReadingCreateRequest(BaseModel):
    device_id: int
    metric: str = Field(min_length=2, max_length=60)
    value: float
    unit: str | None = Field(default=None, max_length=20)
    recorded_at: datetime


class IoTReadingOut(BaseModel):
    id: int
    device_id: int
    metric: str
    value: float
    unit: str | None
    recorded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class IoTReadingListResponse(BaseModel):
    total: int
    items: list[IoTReadingOut]


class IoTMetricSummaryOut(BaseModel):
    metric: str
    count: int
    min_value: float
    max_value: float
    avg_value: float


class IoTMetricSummaryListResponse(BaseModel):
    total_metrics: int
    items: list[IoTMetricSummaryOut]


class IoTRuleCreateRequest(BaseModel):
    farm_id: int
    device_id: int | None = None
    metric: str = Field(min_length=2, max_length=60)
    operator: str = Field(min_length=1, max_length=5)
    threshold_value: float
    severity: str = Field(default='medium', min_length=2, max_length=20)
    status: str = Field(default='active', min_length=2, max_length=20)


class IoTRuleOut(BaseModel):
    id: int
    farm_id: int
    device_id: int | None
    metric: str
    operator: str
    threshold_value: float
    severity: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IoTRuleListResponse(BaseModel):
    total: int
    items: list[IoTRuleOut]


class IoTRuleAlertOut(BaseModel):
    rule_id: int
    farm_id: int
    device_id: int | None
    metric: str
    operator: str
    threshold_value: float
    current_value: float
    severity: str
    triggered_at: datetime


class IoTRuleAlertListResponse(BaseModel):
    total: int
    items: list[IoTRuleAlertOut]


class IoTValveCommandCreateRequest(BaseModel):
    farm_id: int
    device_id: int
    action: str = Field(min_length=2, max_length=20)
    source: str = Field(default='manual', min_length=2, max_length=20)


class IoTValveCommandOut(BaseModel):
    id: int
    farm_id: int
    device_id: int
    action: str
    status: str
    source: str
    requested_at: datetime
    executed_at: datetime | None

    model_config = {"from_attributes": True}


class IoTValveCommandListResponse(BaseModel):
    total: int
    items: list[IoTValveCommandOut]
