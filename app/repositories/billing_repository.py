from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.invoice import Invoice


class BillingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, *, farm_id: int, full_name: str, document_id: str | None, email: str | None, phone: str | None) -> Customer:
        customer = Customer(farm_id=farm_id, full_name=full_name, document_id=document_id, email=email, phone=phone)
        self.db.add(customer)
        self.db.flush()
        return customer

    def list_customers_by_farm_ids(self, farm_ids: list[int]) -> list[Customer]:
        if not farm_ids:
            return []
        q = select(Customer).where(Customer.farm_id.in_(farm_ids)).order_by(Customer.id.desc())
        return list(self.db.scalars(q).all())

    def get_customer(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def create_invoice(self, *, farm_id: int, customer_id: int, invoice_number: str, issue_date: datetime, due_date: datetime | None, total_amount: float, status: str, notes: str | None) -> Invoice:
        invoice = Invoice(
            farm_id=farm_id,
            customer_id=customer_id,
            invoice_number=invoice_number,
            issue_date=issue_date,
            due_date=due_date,
            total_amount=total_amount,
            status=status,
            notes=notes,
        )
        self.db.add(invoice)
        self.db.flush()
        return invoice

    def list_invoices_by_farm_ids(self, farm_ids: list[int]) -> list[Invoice]:
        if not farm_ids:
            return []
        q = select(Invoice).where(Invoice.farm_id.in_(farm_ids)).order_by(Invoice.issue_date.desc(), Invoice.id.desc())
        return list(self.db.scalars(q).all())
