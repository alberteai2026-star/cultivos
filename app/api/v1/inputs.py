from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.input import (
    InputApplicationCreateRequest,
    InputApplicationOut,
    InputProductCreateRequest,
    InputProductOut,
)
from app.services.input_service import InputService

router = APIRouter()


@router.get('/products', response_model=list[InputProductOut])
def list_input_products(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.list_products()


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


@router.get('/applications', response_model=list[InputApplicationOut])
def list_input_applications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InputService(db)
    return service.list_applications_for_user(user)


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
