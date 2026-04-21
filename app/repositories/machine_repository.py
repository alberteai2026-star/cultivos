from sqlalchemy import func, select
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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        status_value: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[Machine]]:
        if not farm_ids:
            return 0, []
        q = select(Machine).where(Machine.farm_id.in_(farm_ids))
        count_q = select(func.count(Machine.id)).where(Machine.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(Machine.farm_id == farm_id)
            count_q = count_q.where(Machine.farm_id == farm_id)
        if status_value is not None:
            q = q.where(Machine.status == status_value)
            count_q = count_q.where(Machine.status == status_value)
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where(Machine.name.ilike(pattern))
            count_q = count_q.where(Machine.name.ilike(pattern))
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(Machine.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, machine_id: int) -> Machine | None:
        return self.db.get(Machine, machine_id)

    def update_fields(
        self,
        machine: Machine,
        *,
        name: str | None,
        machine_type: str | None,
        plate_or_code: str | None,
    ) -> Machine:
        if name is not None:
            machine.name = name
        machine.machine_type = machine_type
        machine.plate_or_code = plate_or_code
        self.db.flush()
        return machine
