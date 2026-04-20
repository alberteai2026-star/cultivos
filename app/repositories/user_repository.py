from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def create(self, *, full_name: str, email: str, password_hash: str, phone: str | None) -> User:
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()
        return user
