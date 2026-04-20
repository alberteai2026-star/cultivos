from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.inventory import (
    InventoryItemCreateRequest,
    InventoryItemOut,
    InventoryMovementCreateRequest,
    InventoryMovementOut,
)
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get('/items', response_model=list[InventoryItemOut])
def list_inventory_items(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).list_items_for_user(user)


@router.post('/items', response_model=InventoryItemOut, status_code=201)
def create_inventory_item(payload: InventoryItemCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).create_item_for_user(user=user, farm_id=payload.farm_id, name=payload.name, unit=payload.unit, min_stock=payload.min_stock)


@router.get('/movements', response_model=list[InventoryMovementOut])
def list_inventory_movements(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).list_movements_for_user(user)


@router.post('/movements', response_model=InventoryMovementOut, status_code=201)
def create_inventory_movement(payload: InventoryMovementCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).create_movement_for_user(user=user, item_id=payload.item_id, movement_type=payload.movement_type, quantity=payload.quantity, reason=payload.reason)
