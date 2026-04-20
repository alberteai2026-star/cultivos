from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
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


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    token = service.login(email=payload.email, password=payload.password)
    return TokenResponse(access_token=token)
