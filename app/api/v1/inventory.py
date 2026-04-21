from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.inventory import (
    InventoryItemCreateRequest,
    InventoryItemListResponse,
    InventoryItemOut,
    InventoryItemUpdateRequest,
    InventoryMovementCreateRequest,
    InventoryMovementListResponse,
    InventoryMovementOut,
    InventoryMovementUpdateRequest,
)
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get('/items', response_model=InventoryItemListResponse)
def list_inventory_items(
    farm_id: int | None = Query(default=None, ge=1),
    search: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InventoryService(db).list_items_for_user(user, farm_id=farm_id, search=search, limit=limit, offset=offset)


@router.post('/items', response_model=InventoryItemOut, status_code=201)
def create_inventory_item(payload: InventoryItemCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).create_item_for_user(user=user, farm_id=payload.farm_id, name=payload.name, unit=payload.unit, min_stock=payload.min_stock)


@router.get('/items/{item_id}', response_model=InventoryItemOut)
def get_inventory_item(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).get_item_for_user(user=user, item_id=item_id)


@router.patch('/items/{item_id}', response_model=InventoryItemOut)
def update_inventory_item(item_id: int, payload: InventoryItemUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).update_item_for_user(user=user, item_id=item_id, name=payload.name, unit=payload.unit, min_stock=payload.min_stock)


@router.get('/movements', response_model=InventoryMovementListResponse)
def list_inventory_movements(
    farm_id: int | None = Query(default=None, ge=1),
    item_id: int | None = Query(default=None, ge=1),
    movement_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InventoryService(db).list_movements_for_user(
        user,
        farm_id=farm_id,
        item_id=item_id,
        movement_type=movement_type,
        limit=limit,
        offset=offset,
    )


@router.post('/movements', response_model=InventoryMovementOut, status_code=201)
def create_inventory_movement(payload: InventoryMovementCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).create_movement_for_user(user=user, item_id=payload.item_id, movement_type=payload.movement_type, quantity=payload.quantity, reason=payload.reason)


@router.get('/movements/{movement_id}', response_model=InventoryMovementOut)
def get_inventory_movement(movement_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).get_movement_for_user(user=user, movement_id=movement_id)


@router.patch('/movements/{movement_id}', response_model=InventoryMovementOut)
def update_inventory_movement(movement_id: int, payload: InventoryMovementUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InventoryService(db).update_movement_for_user(user=user, movement_id=movement_id, reason=payload.reason)
