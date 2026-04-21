from datetime import datetime

from pydantic import BaseModel


class HealthOut(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime
