from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.machine import Machine


class MachineRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, farm_id: int, name: str, machine_type: str | None, plate_or_code: str | None) -> Machine:
        machine = Machine(
            farm_id=farm_id,
            name=name,
            machine_type=machine_type,
            plate_or_code=plate_or_code,
            status='disponible',
        )
        self.db.add(machine)
        self.db.flush()
        return machine

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[Machine]:
        if not farm_ids:
            return []
        q = select(Machine).where(Machine.farm_id.in_(farm_ids)).order_by(Machine.id.desc())
        return list(self.db.scalars(q).all())
