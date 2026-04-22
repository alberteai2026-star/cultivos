from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.machine import MachineListResponse


class MachineService:
    def __init__(self, db: Session):
        self.db = db
        self.machines = MachineRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        status_value: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> MachineListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.machines.list_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            status_value=status_value,
            search=search,
            limit=limit,
            offset=offset,
        )
        return MachineListResponse(total=total, items=items)

    def create_for_user(self, *, user: User, farm_id: int, name: str, machine_type: str | None, plate_or_code: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        machine = self.machines.create(farm_id=farm_id, name=name, machine_type=machine_type, plate_or_code=plate_or_code)
        self.audit.add(module='machines', action='create', user_id=user.id, farm_id=farm_id, record_id=str(machine.id))
        self.db.commit(); self.db.refresh(machine)
        return machine

    def get_for_user(self, *, user: User, machine_id: int):
        machine = self.machines.get_by_id(machine_id)
        if not machine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Máquina no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=machine.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return machine

    def update_for_user(
        self,
        *,
        user: User,
        machine_id: int,
        name: str | None,
        machine_type: str | None,
        plate_or_code: str | None,
    ):
        machine = self.get_for_user(user=user, machine_id=machine_id)
        updated = self.machines.update_fields(machine, name=name, machine_type=machine_type, plate_or_code=plate_or_code)
        self.audit.add(module='machines', action='update', user_id=user.id, farm_id=machine.farm_id, record_id=str(machine.id))
        self.db.commit(); self.db.refresh(updated)
        return updated

    def update_status_for_user(self, *, user: User, machine_id: int, status_value: str):
        machine = self.get_for_user(user=user, machine_id=machine_id)
        machine.status = status_value
        self.audit.add(module='machines', action='update_status', user_id=user.id, farm_id=machine.farm_id, record_id=str(machine.id))
        self.db.commit(); self.db.refresh(machine)
        return machine
