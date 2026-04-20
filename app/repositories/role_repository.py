from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str) -> Role | None:
        return self.db.scalar(select(Role).where(Role.code == code))
