from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.modules.admin import service
from app.modules.admin.schemas import AdminUserOut, UserStatusUpdate, PlatformStats
from app.modules.users.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return service.list_all_users(db, skip, limit)


@router.patch("/users/{user_id}/status", response_model=AdminUserOut)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    updated_user = service.set_user_active_status(db, user_id, payload.is_active, admin)
    return AdminUserOut(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role_name=updated_user.role.name,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
    )


@router.get("/stats", response_model=PlatformStats)
def platform_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return service.get_platform_stats(db)