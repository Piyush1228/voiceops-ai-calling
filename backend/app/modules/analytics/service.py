from datetime import datetime, timedelta

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.modules.calls.models import Call, CallStatus
from app.modules.users.models import User
from app.modules.analytics.schemas import CallVolumePoint, StatusBreakdown, DirectionBreakdown


def get_call_volume_by_day(db: Session, current_user: User, days: int = 14) -> list[CallVolumePoint]:
    since = datetime.utcnow() - timedelta(days=days)

    day_column = func.date(Call.created_at)

    rows = (
        db.query(
            day_column.label("day"),
            func.count(Call.id).label("total_calls"),
            func.sum(
                case((Call.status == CallStatus.COMPLETED, 1), else_=0)
            ).label("completed_calls"),
        )
        .filter(Call.user_id == current_user.id, Call.created_at >= since)
        .group_by(day_column)
        .order_by(day_column.asc())
        .all()
    )

    return [
        CallVolumePoint(
            day=row.day,
            total_calls=row.total_calls,
            completed_calls=row.completed_calls or 0,
        )
        for row in rows
    ]


def get_status_breakdown(db: Session, current_user: User) -> list[StatusBreakdown]:
    rows = (
        db.query(Call.status, func.count(Call.id).label("count"))
        .filter(Call.user_id == current_user.id)
        .group_by(Call.status)
        .all()
    )
    return [StatusBreakdown(status=status.value, count=count) for status, count in rows]


def get_direction_breakdown(db: Session, current_user: User) -> list[DirectionBreakdown]:
    rows = (
        db.query(Call.direction, func.count(Call.id).label("count"))
        .filter(Call.user_id == current_user.id)
        .group_by(Call.direction)
        .all()
    )
    return [DirectionBreakdown(direction=direction.value, count=count) for direction, count in rows]