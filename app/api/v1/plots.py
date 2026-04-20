from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.plot import PlotCreateRequest, PlotOut
from app.services.plot_service import PlotService

router = APIRouter()


@router.get('/', response_model=list[PlotOut])
def list_plots(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PlotService(db)
    return service.list_for_user(user)


@router.post('/', response_model=PlotOut, status_code=201)
def create_plot(
    payload: PlotCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PlotService(db)
    return service.create_for_user(
        user=user,
        farm_id=payload.farm_id,
        code=payload.code,
        name=payload.name,
        area_ha=payload.area_ha,
        soil_type=payload.soil_type,
        status_value=payload.status,
    )
