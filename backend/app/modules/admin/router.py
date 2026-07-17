from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.modules.users.models import User
from app.modules.contacts.models import Contact
from app.modules.calls.models import Call
from app.modules.admin.schemas import AdminUserOut, PlatformStats


def list_all_users(db: Session, skip: int = 0, limit: int = 50) -> list[AdminUserOut]:
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return [
        AdminUserOut(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role_name=u.role.name,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]


def set_user_active_status(db: Session, target_user_id: int, is_active: bool, requesting_admin: User) -> User:
    if target_user_id == requesting_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot deactivate their own account.",
        )

    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def get_platform_stats(db: Session) -> PlatformStats:
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0  # noqa: E712
    total_contacts = db.query(func.count(Contact.id)).scalar() or 0
    total_calls = db.query(func.count(Call.id)).scalar() or 0

    return PlatformStats(
        total_users=total_users,
        active_users=active_users,
        total_contacts=total_contacts,
        total_calls=total_calls,
    )