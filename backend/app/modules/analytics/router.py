from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.analytics import service
from app.modules.analytics.schemas import CallVolumePoint, StatusBreakdown, DirectionBreakdown
from app.modules.users.models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/call-volume", response_model=list[CallVolumePoint])
def call_volume(
    days: int = Query(14, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_call_volume_by_day(db, current_user, days)


@router.get("/status-breakdown", response_model=list[StatusBreakdown])
def status_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_status_breakdown(db, current_user)


@router.get("/direction-breakdown", response_model=list[DirectionBreakdown])
def direction_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_direction_breakdown(db, current_user)