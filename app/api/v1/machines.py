from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.machine import MachineCreateRequest, MachineListResponse, MachineOut, MachineStatusUpdateRequest, MachineUpdateRequest
from app.services.machine_service import MachineService

router = APIRouter()


@router.get('/', response_model=MachineListResponse)
def list_machines(
    farm_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    search: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MachineService(db).list_for_user(
        user,
        farm_id=farm_id,
        status_value=status_value,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.post('/', response_model=MachineOut, status_code=201)
def create_machine(payload: MachineCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MachineService(db).create_for_user(user=user, farm_id=payload.farm_id, name=payload.name, machine_type=payload.machine_type, plate_or_code=payload.plate_or_code)


@router.get('/{machine_id}', response_model=MachineOut)
def get_machine(machine_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MachineService(db).get_for_user(user=user, machine_id=machine_id)


@router.patch('/{machine_id}', response_model=MachineOut)
def update_machine(machine_id: int, payload: MachineUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MachineService(db).update_for_user(
        user=user,
        machine_id=machine_id,
        name=payload.name,
        machine_type=payload.machine_type,
        plate_or_code=payload.plate_or_code,
    )


@router.patch('/{machine_id}/status', response_model=MachineOut)
def update_machine_status(machine_id: int, payload: MachineStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MachineService(db).update_status_for_user(user=user, machine_id=machine_id, status_value=payload.status)
