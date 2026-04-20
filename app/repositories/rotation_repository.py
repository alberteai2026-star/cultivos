from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rotation_plan import RotationPlan


class RotationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, farm_id: int, plot_id: int, next_species: str, recommendation: str | None) -> RotationPlan:
        plan = RotationPlan(
            farm_id=farm_id,
            plot_id=plot_id,
            next_species=next_species,
            recommendation=recommendation,
            status='propuesto',
        )
        self.db.add(plan)
        self.db.flush()
        return plan

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[RotationPlan]:
        if not farm_ids:
            return []
        q = select(RotationPlan).where(RotationPlan.farm_id.in_(farm_ids)).order_by(RotationPlan.id.desc())
        return list(self.db.scalars(q).all())
