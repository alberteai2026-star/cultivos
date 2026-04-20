from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.input_application import InputApplication
from app.models.input_product import InputProduct


class InputRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_product(
        self,
        *,
        name: str,
        category: str,
        ica_register: str | None,
        withholding_days: int | None,
    ) -> InputProduct:
        product = InputProduct(
            name=name,
            category=category,
            ica_register=ica_register,
            withholding_days=withholding_days,
        )
        self.db.add(product)
        self.db.flush()
        return product

    def list_products(self) -> list[InputProduct]:
        return list(self.db.scalars(select(InputProduct).order_by(InputProduct.id.desc())).all())

    def get_product_by_id(self, product_id: int) -> InputProduct | None:
        return self.db.get(InputProduct, product_id)

    def create_application(
        self,
        *,
        farm_id: int,
        plot_id: int,
        task_id: int | None,
        input_product_id: int,
        applied_at,
        quantity: float,
        unit: str,
    ) -> InputApplication:
        app = InputApplication(
            farm_id=farm_id,
            plot_id=plot_id,
            task_id=task_id,
            input_product_id=input_product_id,
            applied_at=applied_at,
            quantity=quantity,
            unit=unit,
        )
        self.db.add(app)
        self.db.flush()
        return app

    def list_applications_by_farm_ids(self, farm_ids: list[int]) -> list[InputApplication]:
        if not farm_ids:
            return []
        query = select(InputApplication).where(InputApplication.farm_id.in_(farm_ids)).order_by(InputApplication.id.desc())
        return list(self.db.scalars(query).all())
