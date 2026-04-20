from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.phytosanitary import PhytosanitaryRecordCreateRequest, PhytosanitaryRecordOut
from app.services.phytosanitary_service import PhytosanitaryService

router = APIRouter()


@router.get('/', response_model=list[PhytosanitaryRecordOut])
def list_phytosanitary_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PhytosanitaryService(db).list_for_user(user)


@router.post('/', response_model=PhytosanitaryRecordOut, status_code=201)
def create_phytosanitary_record(payload: PhytosanitaryRecordCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PhytosanitaryService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, crop_cycle_id=payload.crop_cycle_id, detected_issue=payload.detected_issue, severity=payload.severity, action_taken=payload.action_taken, observed_at=payload.observed_at)
