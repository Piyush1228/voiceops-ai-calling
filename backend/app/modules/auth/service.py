from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password, create_access_token
from app.modules.auth import repository
from app.modules.auth.schemas import UserRegister, UserLogin

DEFAULT_ROLE_ID = 1  # "user" role, seeded separately


def register_user(db: Session, payload: UserRegister):
    existing = repository.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    password_hash = hash_password(payload.password)
    user = repository.create_user(
        db=db,
        email=payload.email,
        password_hash=password_hash,
        full_name=payload.full_name,
        role_id=DEFAULT_ROLE_ID,
    )
    return user


def authenticate_user(db: Session, payload: UserLogin) -> str:
    user = repository.get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    token = create_access_token(data={"sub": str(user.id)})
    return token