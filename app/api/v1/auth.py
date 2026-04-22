from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPairResponse
from app.schemas.user import UserOut
from app.services.auth_service import AuthService

router = APIRouter()


@router.post('/register', response_model=UserOut, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        phone=payload.phone,
    )


@router.post('/login', response_model=TokenPairResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    tokens = service.login(email=payload.email, password=payload.password)
    return TokenPairResponse(**tokens)


@router.post('/refresh', response_model=TokenPairResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    tokens = service.refresh(refresh_token=payload.refresh_token)
    return TokenPairResponse(**tokens)


@router.get('/me', response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
