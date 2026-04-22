from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.input import (
    InputApplicationCreateRequest,
    InputApplicationListResponse,
    InputApplicationOut,
    InputApplicationUpdateRequest,
    InputProductCreateRequest,
    InputProductListResponse,
    InputProductOut,
    InputProductUpdateRequest,
)
from app.services.input_service import InputService

router = APIRouter()


@router.get('/products', response_model=InputProductListResponse)
def list_input_products(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.list_products(search=search, category=category, limit=limit, offset=offset)


@router.get('/products/{product_id}', response_model=InputProductOut)
def get_input_product(
    product_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.get_product(product_id=product_id)


@router.post('/products', response_model=InputProductOut, status_code=201)
def create_input_product(
    payload: InputProductCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.create_product(
        user=user,
        name=payload.name,
        category=payload.category,
        ica_register=payload.ica_register,
        withholding_days=payload.withholding_days,
    )


@router.patch('/products/{product_id}', response_model=InputProductOut)
def update_input_product(
    product_id: int,
    payload: InputProductUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.update_product(
        user=user,
        product_id=product_id,
        name=payload.name,
        category=payload.category,
        ica_register=payload.ica_register,
        withholding_days=payload.withholding_days,
    )


@router.get('/applications', response_model=InputApplicationListResponse)
def list_input_applications(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    input_product_id: int | None = Query(default=None, ge=1),
    applied_from: datetime | None = Query(default=None),
    applied_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.list_applications_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        input_product_id=input_product_id,
        applied_from=applied_from,
        applied_to=applied_to,
        limit=limit,
        offset=offset,
    )


@router.get('/applications/{application_id}', response_model=InputApplicationOut)
def get_input_application(
    application_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.get_application_for_user(user=user, application_id=application_id)


@router.post('/applications', response_model=InputApplicationOut, status_code=201)
def create_input_application(
    payload: InputApplicationCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.create_application_for_user(
        user=user,
        plot_id=payload.plot_id,
        input_product_id=payload.input_product_id,
        task_id=payload.task_id,
        applied_at=payload.applied_at,
        quantity=payload.quantity,
        unit=payload.unit,
    )


@router.patch('/applications/{application_id}', response_model=InputApplicationOut)
def update_input_application(
    application_id: int,
    payload: InputApplicationUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.update_application_for_user(
        user=user,
        application_id=application_id,
        applied_at=payload.applied_at,
        quantity=payload.quantity,
        unit=payload.unit,
    )
