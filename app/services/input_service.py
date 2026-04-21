from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.input_repository import InputRepository
from app.repositories.plot_repository import PlotRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.input import InputApplicationListResponse, InputProductListResponse


class InputService:
    def __init__(self, db: Session):
        self.db = db
        self.inputs = InputRepository(db)
        self.plots = PlotRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_products(
        self,
        *,
        search: str | None = None,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> InputProductListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro offset debe ser mayor o igual a 0')
        total, items = self.inputs.list_products(search=search, category=category, limit=limit, offset=offset)
        return InputProductListResponse(total=total, items=items)

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

    def get_product(self, *, product_id: int):
        product = self.inputs.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Insumo no encontrado')
        return product

    def update_product(
        self,
        *,
        user: User,
        product_id: int,
        name: str | None,
        category: str | None,
        ica_register: str | None,
        withholding_days: int | None,
    ):
        product = self.inputs.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Insumo no encontrado')
        updated = self.inputs.update_product_fields(
            product,
            name=name,
            category=category,
            ica_register=ica_register,
            withholding_days=withholding_days,
        )
        self.audit.add(module='inputs', action='update_product', user_id=user.id, record_id=str(product.id), metadata={'name': updated.name})
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def list_applications_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        input_product_id: int | None = None,
        applied_from: datetime | None = None,
        applied_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> InputApplicationListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro offset debe ser mayor o igual a 0')
        if applied_from is not None and applied_to is not None and applied_from > applied_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Rango de fechas inválido')
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.inputs.list_applications_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            input_product_id=input_product_id,
            applied_from=applied_from,
            applied_to=applied_to,
            limit=limit,
            offset=offset,
        )
        return InputApplicationListResponse(total=total, items=items)

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

    def get_application_for_user(self, *, user: User, application_id: int):
        app = self.inputs.get_application_by_id(application_id)
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Aplicación no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=app.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return app

    def update_application_for_user(
        self,
        *,
        user: User,
        application_id: int,
        applied_at: datetime | None,
        quantity: float | None,
        unit: str | None,
    ):
        app = self.inputs.get_application_by_id(application_id)
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Aplicación no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=app.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        updated = self.inputs.update_application_fields(app, applied_at=applied_at, quantity=quantity, unit=unit)
        self.audit.add(
            module='inputs',
            action='update_application',
            user_id=user.id,
            farm_id=app.farm_id,
            record_id=str(app.id),
            metadata={'quantity': updated.quantity, 'unit': updated.unit},
        )
        self.db.commit()
        self.db.refresh(updated)
        return updated
