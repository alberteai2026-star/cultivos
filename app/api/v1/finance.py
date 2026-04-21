from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.finance import FinanceEntryCreateRequest, FinanceEntryOut, FinanceSummaryOut
from app.services.finance_service import FinanceService

router = APIRouter()


@router.get('/entries', response_model=list[FinanceEntryOut])
def list_finance_entries(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return FinanceService(db).list_for_user(user)


@router.post('/entries', response_model=FinanceEntryOut, status_code=201)
def create_finance_entry(payload: FinanceEntryCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return FinanceService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, crop_cycle_id=payload.crop_cycle_id, entry_type=payload.entry_type, category=payload.category, amount=payload.amount, description=payload.description, happened_at=payload.happened_at)


@router.get('/summary', response_model=FinanceSummaryOut)
def get_finance_summary(
    farm_id: int,
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return FinanceService(db).summary_for_user(user=user, farm_id=farm_id, date_from=date_from, date_to=date_to)
