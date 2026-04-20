from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.machine import MachineCreateRequest, MachineOut
from app.services.machine_service import MachineService

router = APIRouter()


@router.get('/', response_model=list[MachineOut])
def list_machines(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MachineService(db).list_for_user(user)


@router.post('/', response_model=MachineOut, status_code=201)
def create_machine(payload: MachineCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MachineService(db).create_for_user(user=user, farm_id=payload.farm_id, name=payload.name, machine_type=payload.machine_type, plate_or_code=payload.plate_or_code)
