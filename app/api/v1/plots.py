from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.plot import PlotCreateRequest, PlotListResponse, PlotOut, PlotUpdateRequest
from app.services.plot_service import PlotService

router = APIRouter()


@router.get('/', response_model=PlotListResponse)
def list_plots(
    farm_id: int | None = Query(default=None, ge=1),
    search: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias='status'),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PlotService(db)
    return service.list_for_user(
        user,
        farm_id=farm_id,
        search=search,
        status_value=status_value,
        limit=limit,
        offset=offset,
    )


@router.get('/{plot_id}', response_model=PlotOut)
def get_plot(
    plot_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PlotService(db)
    return service.get_for_user(user=user, plot_id=plot_id)


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


@router.patch('/{plot_id}', response_model=PlotOut)
def update_plot(
    plot_id: int,
    payload: PlotUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PlotService(db)
    return service.update_for_user(
        user=user,
        plot_id=plot_id,
        code=payload.code,
        name=payload.name,
        area_ha=payload.area_ha,
        soil_type=payload.soil_type,
        status_value=payload.status,
    )
