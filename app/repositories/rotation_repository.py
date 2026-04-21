from sqlalchemy import func, select
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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[RotationPlan]]:
        if not farm_ids:
            return 0, []
        q = select(RotationPlan).where(RotationPlan.farm_id.in_(farm_ids))
        count_q = select(func.count(RotationPlan.id)).where(RotationPlan.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(RotationPlan.farm_id == farm_id)
            count_q = count_q.where(RotationPlan.farm_id == farm_id)
        if plot_id is not None:
            q = q.where(RotationPlan.plot_id == plot_id)
            count_q = count_q.where(RotationPlan.plot_id == plot_id)
        if status_value is not None:
            q = q.where(RotationPlan.status == status_value)
            count_q = count_q.where(RotationPlan.status == status_value)
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where(RotationPlan.next_species.ilike(pattern))
            count_q = count_q.where(RotationPlan.next_species.ilike(pattern))
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(RotationPlan.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, plan_id: int) -> RotationPlan | None:
        return self.db.get(RotationPlan, plan_id)

    def update_fields(self, plan: RotationPlan, *, next_species: str | None, recommendation: str | None) -> RotationPlan:
        if next_species is not None:
            plan.next_species = next_species
        plan.recommendation = recommendation
        self.db.flush()
        return plan
