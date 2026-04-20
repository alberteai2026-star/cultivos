from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.billing_repository import BillingRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class BillingService:
    def __init__(self, db: Session):
        self.db = db
        self.billing = BillingRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_customers_for_user(self, user: User):
        return self.billing.list_customers_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_customer_for_user(self, *, user: User, farm_id: int, full_name: str, document_id: str | None, email: str | None, phone: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        customer = self.billing.create_customer(farm_id=farm_id, full_name=full_name, document_id=document_id, email=email, phone=phone)
        self.audit.add(module='billing', action='create_customer', user_id=user.id, farm_id=farm_id, record_id=str(customer.id))
        self.db.commit(); self.db.refresh(customer)
        return customer

    def list_invoices_for_user(self, user: User):
        return self.billing.list_invoices_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_invoice_for_user(self, *, user: User, farm_id: int, customer_id: int, invoice_number: str, issue_date: datetime, due_date: datetime | None, total_amount: float, status_value: str, notes: str | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        customer = self.billing.get_customer(customer_id)
        if customer is None or customer.farm_id != farm_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cliente no encontrado para la finca')
        invoice = self.billing.create_invoice(farm_id=farm_id, customer_id=customer_id, invoice_number=invoice_number, issue_date=issue_date, due_date=due_date, total_amount=total_amount, status=status_value, notes=notes)
        self.audit.add(module='billing', action='create_invoice', user_id=user.id, farm_id=farm_id, record_id=str(invoice.id))
        self.db.commit(); self.db.refresh(invoice)
        return invoice
