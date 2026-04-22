from datetime import datetime

from pydantic import BaseModel


class HealthOut(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime


class HealthReadinessOut(BaseModel):
    status: str
    database: str
    timestamp: datetime
