from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, hash_password, verify_password
from app.db.session import get_db
from app.models.entities import Role, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair
from app.services.audit import write_audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email.lower()).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=Role.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    write_audit(db, "user.register", user.id, {"email": user.email})
    return TokenPair(
        access_token=create_token(str(user.id), "access", settings.access_token_expire_minutes),
        refresh_token=create_token(str(user.id), "refresh", settings.refresh_token_expire_minutes),
    )


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")
    write_audit(db, "user.login", user.id)
    return TokenPair(
        access_token=create_token(str(user.id), "access", settings.access_token_expire_minutes),
        refresh_token=create_token(str(user.id), "refresh", settings.refresh_token_expire_minutes),
    )
