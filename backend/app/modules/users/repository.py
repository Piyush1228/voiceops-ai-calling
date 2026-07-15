from sqlalchemy.orm import Session

from app.modules.users.models import User


def update_user_profile(db: Session, user: User, full_name: str | None, email: str | None) -> User:
    if full_name is not None:
        user.full_name = full_name
    if email is not None:
        user.email = email
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user: User, new_password_hash: str) -> User:
    user.password_hash = new_password_hash
    db.commit()
    db.refresh(user)
    return user