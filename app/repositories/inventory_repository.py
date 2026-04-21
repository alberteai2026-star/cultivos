from sqlalchemy import func, select
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

    def list_items_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[InventoryItem]]:
        if not farm_ids:
            return 0, []
        q = select(InventoryItem).where(InventoryItem.farm_id.in_(farm_ids))
        count_q = select(func.count(InventoryItem.id)).where(InventoryItem.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(InventoryItem.farm_id == farm_id)
            count_q = count_q.where(InventoryItem.farm_id == farm_id)
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where(InventoryItem.name.ilike(pattern))
            count_q = count_q.where(InventoryItem.name.ilike(pattern))
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(InventoryItem.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def update_item_fields(self, item: InventoryItem, *, name: str | None, unit: str | None, min_stock: float | None) -> InventoryItem:
        if name is not None:
            item.name = name
        if unit is not None:
            item.unit = unit
        item.min_stock = min_stock
        self.db.flush()
        return item

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

    def list_movements_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        item_id: int | None = None,
        movement_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[InventoryMovement]]:
        if not farm_ids:
            return 0, []
        q = select(InventoryMovement).where(InventoryMovement.farm_id.in_(farm_ids))
        count_q = select(func.count(InventoryMovement.id)).where(InventoryMovement.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(InventoryMovement.farm_id == farm_id)
            count_q = count_q.where(InventoryMovement.farm_id == farm_id)
        if item_id is not None:
            q = q.where(InventoryMovement.item_id == item_id)
            count_q = count_q.where(InventoryMovement.item_id == item_id)
        if movement_type is not None:
            q = q.where(InventoryMovement.movement_type == movement_type)
            count_q = count_q.where(InventoryMovement.movement_type == movement_type)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(InventoryMovement.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_movement(self, movement_id: int) -> InventoryMovement | None:
        return self.db.get(InventoryMovement, movement_id)

    def update_movement_reason(self, movement: InventoryMovement, *, reason: str | None) -> InventoryMovement:
        movement.reason = reason
        self.db.flush()
        return movement
