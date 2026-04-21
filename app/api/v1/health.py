from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthOut

router = APIRouter()


@router.get('/health', response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.env,
        timestamp=datetime.now(timezone.utc),
    )
