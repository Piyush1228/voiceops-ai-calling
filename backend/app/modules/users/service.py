from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import verify_password, hash_password
from app.modules.auth import repository as auth_repository
from app.modules.users import repository
from app.modules.users.models import User
from app.modules.users.schemas import UserProfileUpdate, PasswordChange


def update_profile(db: Session, current_user: User, payload: UserProfileUpdate) -> User:
    if payload.email and payload.email != current_user.email:
        existing = auth_repository.get_user_by_email(db, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already in use by another account.",
            )

    return repository.update_user_profile(
        db=db,
        user=current_user,
        full_name=payload.full_name,
        email=payload.email,
    )


def change_password(db: Session, current_user: User, payload: PasswordChange) -> None:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect.",
        )

    new_hash = hash_password(payload.new_password)
    repository.update_user_password(db, current_user, new_hash)