from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.input_repository import InputRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class InputService:
    def __init__(self, db: Session):
        self.db = db
        self.inputs = InputRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_products(self):
        return self.inputs.list_products()

    def create_product(self, *, user: User, name: str, category: str, ica_register: str | None, withholding_days: int | None):
        product = self.inputs.create_product(
            name=name,
            category=category,
            ica_register=ica_register,
            withholding_days=withholding_days,
        )
        self.audit.add(
            module='inputs',
            action='create_product',
            user_id=user.id,
            record_id=str(product.id),
            metadata={'name': product.name},
        )
        self.db.commit()
        self.db.refresh(product)
        return product

    def list_applications_for_user(self, user: User):
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        return self.inputs.list_applications_by_farm_ids(farm_ids)

    def create_application_for_user(
        self,
        *,
        user: User,
        plot_id: int,
        input_product_id: int,
        task_id: int | None,
        applied_at,
        quantity: float,
        unit: str,
    ):
        plot = self.plots.get_by_id(plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lote no encontrado')

        if not self.relations.user_has_farm(user_id=user.id, farm_id=plot.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        product = self.inputs.get_product_by_id(input_product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Insumo no encontrado')

        application = self.inputs.create_application(
            farm_id=plot.farm_id,
            plot_id=plot_id,
            task_id=task_id,
            input_product_id=input_product_id,
            applied_at=applied_at,
            quantity=quantity,
            unit=unit,
        )

        self.audit.add(
            module='inputs',
            action='create_application',
            user_id=user.id,
            farm_id=plot.farm_id,
            record_id=str(application.id),
            metadata={'plot_id': plot.id, 'input_product_id': input_product_id},
        )

        self.db.commit()
        self.db.refresh(application)
        return application
