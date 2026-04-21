from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_farm_role import UserFarmRole


class UserFarmRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def assign_role(self, *, user_id: int, farm_id: int, role_id: int) -> UserFarmRole:
        relation = UserFarmRole(user_id=user_id, farm_id=farm_id, role_id=role_id)
        self.db.add(relation)
        self.db.flush()
        return relation

    def list_farm_ids_by_user(self, user_id: int) -> list[int]:
        rows = self.db.scalars(select(UserFarmRole.farm_id).where(UserFarmRole.user_id == user_id)).all()
        return [int(farm_id) for farm_id in rows]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        query = select(UserFarmRole.id).where(
            UserFarmRole.user_id == user_id,
            UserFarmRole.farm_id == farm_id,
        )
        return self.db.scalar(query) is not None


    def user_has_role_for_farm(self, *, user_id: int, farm_id: int, role_id: int) -> bool:
        query = select(UserFarmRole.id).where(
            UserFarmRole.user_id == user_id,
            UserFarmRole.farm_id == farm_id,
            UserFarmRole.role_id == role_id,
        )
        return self.db.scalar(query) is not None
