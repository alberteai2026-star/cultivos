from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(*, subject: str, expires_minutes: int, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "typ": token_type,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire_delta = expires_minutes or settings.access_token_expire_minutes
    return _create_token(subject=subject, expires_minutes=expire_delta, token_type=ACCESS_TOKEN_TYPE)


def create_refresh_token(subject: str, expires_minutes: int | None = None) -> str:
    expire_delta = expires_minutes or settings.refresh_token_expire_minutes
    return _create_token(subject=subject, expires_minutes=expire_delta, token_type=REFRESH_TOKEN_TYPE)


def decode_access_token(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    token_type = payload.get("typ")
    if token_type not in (None, ACCESS_TOKEN_TYPE):
        raise ValueError("Tipo de token inválido para acceso")
    return payload


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Token inválido") from exc
