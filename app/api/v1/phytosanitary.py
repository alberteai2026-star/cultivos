from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.phytosanitary import (
    PhytosanitaryRecordCreateRequest,
    PhytosanitaryRecordListResponse,
    PhytosanitaryRecordOut,
    PhytosanitaryRecordUpdateRequest,
)
from app.services.phytosanitary_service import PhytosanitaryService

router = APIRouter()


@router.get('/', response_model=PhytosanitaryRecordListResponse)
def list_phytosanitary_records(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    severity: str | None = None,
    issue_search: str | None = Query(default=None, alias='search'),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PhytosanitaryService(db).list_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        severity=severity,
        issue_search=issue_search,
        limit=limit,
        offset=offset,
    )


@router.post('/', response_model=PhytosanitaryRecordOut, status_code=201)
def create_phytosanitary_record(payload: PhytosanitaryRecordCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PhytosanitaryService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, crop_cycle_id=payload.crop_cycle_id, detected_issue=payload.detected_issue, severity=payload.severity, action_taken=payload.action_taken, observed_at=payload.observed_at)


@router.get('/{record_id}', response_model=PhytosanitaryRecordOut)
def get_phytosanitary_record(record_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PhytosanitaryService(db).get_for_user(user=user, record_id=record_id)


@router.patch('/{record_id}', response_model=PhytosanitaryRecordOut)
def update_phytosanitary_record(record_id: int, payload: PhytosanitaryRecordUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PhytosanitaryService(db).update_for_user(
        user=user,
        record_id=record_id,
        detected_issue=payload.detected_issue,
        severity=payload.severity,
        action_taken=payload.action_taken,
        observed_at=payload.observed_at,
    )
