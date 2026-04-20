from datetime import datetime

from pydantic import BaseModel, Field


class MachineCreateRequest(BaseModel):
    farm_id: int
    name: str = Field(min_length=2, max_length=120)
    machine_type: str | None = Field(default=None, max_length=80)
    plate_or_code: str | None = Field(default=None, max_length=50)


class MachineOut(BaseModel):
    id: int
    farm_id: int
    name: str
    machine_type: str | None
    plate_or_code: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
