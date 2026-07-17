from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.dashboard import service
from app.modules.dashboard.schemas import DashboardSummary, RecentCallOut
from app.modules.users.models import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_summary(db, current_user)


@router.get("/recent-calls", response_model=list[RecentCallOut])
def get_recent_calls(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_recent_calls(db, current_user, limit)