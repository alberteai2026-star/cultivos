from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.inventory import InventoryItemListResponse, InventoryMovementListResponse


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory = InventoryRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_items_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> InventoryItemListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.inventory.list_items_by_farm_ids(farm_ids, farm_id=farm_id, search=search, limit=limit, offset=offset)
        return InventoryItemListResponse(total=total, items=items)

    def list_movements_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        item_id: int | None = None,
        movement_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> InventoryMovementListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.inventory.list_movements_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            item_id=item_id,
            movement_type=movement_type,
            limit=limit,
            offset=offset,
        )
        return InventoryMovementListResponse(total=total, items=items)

    def create_item_for_user(self, *, user: User, farm_id: int, name: str, unit: str, min_stock: float | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        item = self.inventory.create_item(farm_id=farm_id, name=name, unit=unit, min_stock=min_stock)
        self.audit.add(module='inventory', action='create_item', user_id=user.id, farm_id=farm_id, record_id=str(item.id))
        self.db.commit(); self.db.refresh(item)
        return item

    def get_item_for_user(self, *, user: User, item_id: int):
        item = self.inventory.get_item(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=item.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return item

    def update_item_for_user(self, *, user: User, item_id: int, name: str | None, unit: str | None, min_stock: float | None):
        item = self.get_item_for_user(user=user, item_id=item_id)
        updated = self.inventory.update_item_fields(item, name=name, unit=unit, min_stock=min_stock)
        self.audit.add(module='inventory', action='update_item', user_id=user.id, farm_id=item.farm_id, record_id=str(item.id))
        self.db.commit(); self.db.refresh(updated)
        return updated

    def create_movement_for_user(self, *, user: User, item_id: int, movement_type: str, quantity: float, reason: str | None):
        item = self.inventory.get_item(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=item.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        if movement_type == 'entrada':
            item.current_stock += quantity
        elif movement_type == 'salida':
            item.current_stock -= quantity
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Tipo de movimiento inválido')

        move = self.inventory.create_movement(farm_id=item.farm_id, item_id=item.id, movement_type=movement_type, quantity=quantity, reason=reason)
        self.audit.add(module='inventory', action='movement', user_id=user.id, farm_id=item.farm_id, record_id=str(move.id), metadata={'type': movement_type, 'qty': quantity})
        self.db.commit(); self.db.refresh(move)
        return move

    def get_movement_for_user(self, *, user: User, movement_id: int):
        move = self.inventory.get_movement(movement_id)
        if not move:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movimiento no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=move.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return move

    def update_movement_for_user(self, *, user: User, movement_id: int, reason: str | None):
        move = self.get_movement_for_user(user=user, movement_id=movement_id)
        updated = self.inventory.update_movement_reason(move, reason=reason)
        self.audit.add(module='inventory', action='update_movement', user_id=user.id, farm_id=move.farm_id, record_id=str(move.id))
        self.db.commit(); self.db.refresh(updated)
        return updated
