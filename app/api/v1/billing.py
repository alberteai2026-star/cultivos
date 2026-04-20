from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.billing import CustomerCreateRequest, CustomerOut, InvoiceCreateRequest, InvoiceOut
from app.services.billing_service import BillingService

router = APIRouter()


@router.get('/customers', response_model=list[CustomerOut])
def list_customers(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return BillingService(db).list_customers_for_user(user)


@router.post('/customers', response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return BillingService(db).create_customer_for_user(user=user, farm_id=payload.farm_id, full_name=payload.full_name, document_id=payload.document_id, email=payload.email, phone=payload.phone)


@router.get('/invoices', response_model=list[InvoiceOut])
def list_invoices(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return BillingService(db).list_invoices_for_user(user)


@router.post('/invoices', response_model=InvoiceOut, status_code=201)
def create_invoice(payload: InvoiceCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return BillingService(db).create_invoice_for_user(user=user, farm_id=payload.farm_id, customer_id=payload.customer_id, invoice_number=payload.invoice_number, issue_date=payload.issue_date, due_date=payload.due_date, total_amount=payload.total_amount, status_value=payload.status, notes=payload.notes)
