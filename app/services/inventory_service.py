from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory = InventoryRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_items_for_user(self, user: User):
        return self.inventory.list_items_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def list_movements_for_user(self, user: User):
        return self.inventory.list_movements_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_item_for_user(self, *, user: User, farm_id: int, name: str, unit: str, min_stock: float | None):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        item = self.inventory.create_item(farm_id=farm_id, name=name, unit=unit, min_stock=min_stock)
        self.audit.add(module='inventory', action='create_item', user_id=user.id, farm_id=farm_id, record_id=str(item.id))
        self.db.commit(); self.db.refresh(item)
        return item

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
