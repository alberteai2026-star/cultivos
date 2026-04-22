from datetime import datetime

from pydantic import BaseModel, Field


class MachineCreateRequest(BaseModel):
    farm_id: int
    name: str = Field(min_length=2, max_length=120)
    machine_type: str | None = Field(default=None, max_length=80)
    plate_or_code: str | None = Field(default=None, max_length=50)


class MachineUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    machine_type: str | None = Field(default=None, max_length=80)
    plate_or_code: str | None = Field(default=None, max_length=50)


class MachineStatusUpdateRequest(BaseModel):
    status: str


class MachineOut(BaseModel):
    id: int
    farm_id: int
    name: str | None = None
    machine_type: str | None = None
    plate_or_code: str | None = None
    status: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class MachineListResponse(BaseModel):
    total: int
    items: list[MachineOut]
