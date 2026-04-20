from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.audit = AuditRepository(db)

    def register(self, *, full_name: str, email: str, password: str, phone: str | None) -> User:
        existing = self.users.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado",
            )

        user = self.users.create(
            full_name=full_name,
            email=email,
            password_hash=get_password_hash(password),
            phone=phone,
        )
        self.audit.add(
            module="auth",
            action="register",
            user_id=user.id,
            record_id=str(user.id),
            metadata={"email": user.email},
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, *, email: str, password: str) -> str:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo",
            )

        token = create_access_token(subject=str(user.id))
        self.audit.add(
            module="auth",
            action="login",
            user_id=user.id,
            record_id=str(user.id),
            metadata={"email": user.email},
        )
        self.db.commit()
        return token
