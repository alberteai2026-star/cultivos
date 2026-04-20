from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.plot import Plot


class PlotRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        farm_id: int,
        code: str,
        name: str,
        area_ha: float | None,
        soil_type: str | None,
        status: str,
    ) -> Plot:
        plot = Plot(
            farm_id=farm_id,
            code=code,
            name=name,
            area_ha=area_ha,
            soil_type=soil_type,
            status=status,
        )
        self.db.add(plot)
        self.db.flush()
        return plot

    def list_by_farm_ids(self, farm_ids: list[int]) -> list[Plot]:
        if not farm_ids:
            return []
        query = select(Plot).where(Plot.farm_id.in_(farm_ids)).order_by(Plot.id.desc())
        return list(self.db.scalars(query).all())

    def get_by_id(self, plot_id: int) -> Plot | None:
        return self.db.get(Plot, plot_id)
