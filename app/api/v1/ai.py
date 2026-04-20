from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import AIInsightCreateRequest, AIInsightOut
from app.services.ai_service import AIService

router = APIRouter()


@router.get('/insights', response_model=list[AIInsightOut])
def list_ai_insights(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AIService(db).list_for_user(user)


@router.post('/insights', response_model=AIInsightOut, status_code=201)
def create_ai_insight(payload: AIInsightCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AIService(db).create_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, crop_cycle_id=payload.crop_cycle_id, insight_type=payload.insight_type, title=payload.title, recommendation=payload.recommendation, predicted_value=payload.predicted_value, confidence=payload.confidence, priority=payload.priority, generated_at=payload.generated_at)
