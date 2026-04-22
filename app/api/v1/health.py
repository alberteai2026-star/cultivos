from datetime import datetime, timezone

from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import SessionLocal
from app.schemas.health import HealthOut, HealthReadinessOut

router = APIRouter()


def _database_is_ready() -> bool:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False
    finally:
        db.close()


@router.get('', response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.env,
        timestamp=datetime.now(timezone.utc),
    )


@router.get('/health', response_model=HealthOut, deprecated=True)
def health_legacy() -> HealthOut:
    return health()


@router.get('/ready', response_model=HealthReadinessOut)
def readiness(response: Response) -> HealthReadinessOut:
    if _database_is_ready():
        return HealthReadinessOut(status="ok", database="up", timestamp=datetime.now(timezone.utc))
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthReadinessOut(
        status="degraded",
        database="down",
        timestamp=datetime.now(timezone.utc),
    )
