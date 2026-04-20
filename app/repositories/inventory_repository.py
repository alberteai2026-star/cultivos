from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory_item import InventoryItem
from app.models.inventory_movement import InventoryMovement


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_item(self, *, farm_id: int, name: str, unit: str, min_stock: float | None) -> InventoryItem:
        item = InventoryItem(farm_id=farm_id, name=name, unit=unit, min_stock=min_stock, current_stock=0)
        self.db.add(item)
        self.db.flush()
        return item

    def get_item(self, item_id: int) -> InventoryItem | None:
        return self.db.get(InventoryItem, item_id)

    def list_items_by_farm_ids(self, farm_ids: list[int]) -> list[InventoryItem]:
        if not farm_ids:
            return []
        q = select(InventoryItem).where(InventoryItem.farm_id.in_(farm_ids)).order_by(InventoryItem.id.desc())
        return list(self.db.scalars(q).all())

    def create_movement(self, *, farm_id: int, item_id: int, movement_type: str, quantity: float, reason: str | None) -> InventoryMovement:
        movement = InventoryMovement(
            farm_id=farm_id,
            item_id=item_id,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason,
        )
        self.db.add(movement)
        self.db.flush()
        return movement

    def list_movements_by_farm_ids(self, farm_ids: list[int]) -> list[InventoryMovement]:
        if not farm_ids:
            return []
        q = select(InventoryMovement).where(InventoryMovement.farm_id.in_(farm_ids)).order_by(InventoryMovement.id.desc())
        return list(self.db.scalars(q).all())
