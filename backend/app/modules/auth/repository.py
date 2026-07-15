from sqlalchemy.orm import Session

from app.modules.users.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password_hash: str, full_name: str, role_id: int) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role_id=role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user