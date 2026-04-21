from sqlalchemy import func, select
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

    def list_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        search: str | None = None,
        status_value: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[Plot]]:
        if not farm_ids:
            return 0, []

        q = select(Plot).where(Plot.farm_id.in_(farm_ids))
        count_q = select(func.count(Plot.id)).where(Plot.farm_id.in_(farm_ids))

        if farm_id is not None:
            q = q.where(Plot.farm_id == farm_id)
            count_q = count_q.where(Plot.farm_id == farm_id)
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where((Plot.name.ilike(pattern)) | (Plot.code.ilike(pattern)))
            count_q = count_q.where((Plot.name.ilike(pattern)) | (Plot.code.ilike(pattern)))
        if status_value is not None:
            q = q.where(Plot.status == status_value)
            count_q = count_q.where(Plot.status == status_value)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(Plot.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_by_id(self, plot_id: int) -> Plot | None:
        return self.db.get(Plot, plot_id)

    def get_by_code_in_farm(self, *, farm_id: int, code: str) -> Plot | None:
        query = select(Plot).where(Plot.farm_id == farm_id, Plot.code == code)
        return self.db.scalar(query)

    def update(
        self,
        plot: Plot,
        *,
        code: str | None,
        name: str | None,
        area_ha: float | None,
        soil_type: str | None,
        status: str | None,
    ) -> Plot:
        if code is not None:
            plot.code = code
        if name is not None:
            plot.name = name
        plot.area_ha = area_ha
        plot.soil_type = soil_type
        if status is not None:
            plot.status = status
        self.db.flush()
        return plot
