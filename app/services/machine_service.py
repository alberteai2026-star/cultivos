from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class MachineService:
    def __init__(self, db: Session):
        self.db = db
        self.machines = MachineRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        return self.machines.list_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_for_user(self, *, user: User, farm_id: int, name: str, machine_type: str | None, plate_or_code: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        machine = self.machines.create(farm_id=farm_id, name=name, machine_type=machine_type, plate_or_code=plate_or_code)
        self.audit.add(module='machines', action='create', user_id=user.id, farm_id=farm_id, record_id=str(machine.id))
        self.db.commit(); self.db.refresh(machine)
        return machine
