from datetime import datetime

from sqlalchemy import func, select
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

    def list_products(
        self,
        *,
        search: str | None = None,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[InputProduct]]:
        q = select(InputProduct)
        count_q = select(func.count(InputProduct.id))
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where(InputProduct.name.ilike(pattern))
            count_q = count_q.where(InputProduct.name.ilike(pattern))
        if category:
            q = q.where(InputProduct.category == category)
            count_q = count_q.where(InputProduct.category == category)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(InputProduct.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_product_by_id(self, product_id: int) -> InputProduct | None:
        return self.db.get(InputProduct, product_id)

    def update_product_fields(
        self,
        product: InputProduct,
        *,
        name: str | None,
        category: str | None,
        ica_register: str | None,
        withholding_days: int | None,
    ) -> InputProduct:
        if name is not None:
            product.name = name
        if category is not None:
            product.category = category
        product.ica_register = ica_register
        product.withholding_days = withholding_days
        self.db.flush()
        return product

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

    def list_applications_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        input_product_id: int | None = None,
        applied_from: datetime | None = None,
        applied_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[InputApplication]]:
        if not farm_ids:
            return 0, []
        query = select(InputApplication).where(InputApplication.farm_id.in_(farm_ids))
        count_query = select(func.count(InputApplication.id)).where(InputApplication.farm_id.in_(farm_ids))
        if farm_id is not None:
            query = query.where(InputApplication.farm_id == farm_id)
            count_query = count_query.where(InputApplication.farm_id == farm_id)
        if plot_id is not None:
            query = query.where(InputApplication.plot_id == plot_id)
            count_query = count_query.where(InputApplication.plot_id == plot_id)
        if input_product_id is not None:
            query = query.where(InputApplication.input_product_id == input_product_id)
            count_query = count_query.where(InputApplication.input_product_id == input_product_id)
        if applied_from is not None:
            query = query.where(InputApplication.applied_at >= applied_from)
            count_query = count_query.where(InputApplication.applied_at >= applied_from)
        if applied_to is not None:
            query = query.where(InputApplication.applied_at <= applied_to)
            count_query = count_query.where(InputApplication.applied_at <= applied_to)
        total = int(self.db.scalar(count_query) or 0)
        query = query.order_by(InputApplication.applied_at.desc(), InputApplication.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(query).all())

    def get_application_by_id(self, application_id: int) -> InputApplication | None:
        return self.db.get(InputApplication, application_id)

    def update_application_fields(
        self,
        app: InputApplication,
        *,
        applied_at: datetime | None,
        quantity: float | None,
        unit: str | None,
    ) -> InputApplication:
        if applied_at is not None:
            app.applied_at = applied_at
        if quantity is not None:
            app.quantity = quantity
        if unit is not None:
            app.unit = unit
        self.db.flush()
        return app
