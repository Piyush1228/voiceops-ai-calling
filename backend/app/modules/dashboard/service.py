from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.calls.models import Call, CallStatus
from app.modules.contacts.models import Contact
from app.modules.users.models import User
from app.modules.dashboard.schemas import DashboardSummary, RecentCallOut


def get_summary(db: Session, current_user: User) -> DashboardSummary:
    total_contacts = (
        db.query(func.count(Contact.id))
        .filter(Contact.user_id == current_user.id)
        .scalar()
    )

    total_calls = (
        db.query(func.count(Call.id))
        .filter(Call.user_id == current_user.id)
        .scalar()
    )

    calls_completed = (
        db.query(func.count(Call.id))
        .filter(Call.user_id == current_user.id, Call.status == CallStatus.COMPLETED)
        .scalar()
    )

    calls_failed_or_missed = (
        db.query(func.count(Call.id))
        .filter(
            Call.user_id == current_user.id,
            Call.status.in_([CallStatus.FAILED, CallStatus.NO_ANSWER]),
        )
        .scalar()
    )

    total_seconds = (
        db.query(
            func.sum(
                func.extract("epoch", Call.ended_at) - func.extract("epoch", Call.started_at)
            )
        )
        .filter(
            Call.user_id == current_user.id,
            Call.started_at.isnot(None),
            Call.ended_at.isnot(None),
        )
        .scalar()
    )
    total_minutes = round((total_seconds or 0) / 60, 2)

    return DashboardSummary(
        total_contacts=total_contacts or 0,
        total_calls=total_calls or 0,
        calls_completed=calls_completed or 0,
        calls_failed_or_missed=calls_failed_or_missed or 0,
        total_call_minutes=total_minutes,
    )


def get_recent_calls(db: Session, current_user: User, limit: int = 10) -> list[RecentCallOut]:
    rows = (
        db.query(Call, Contact.name)
        .join(Contact, Call.contact_id == Contact.id)
        .filter(Call.user_id == current_user.id)
        .order_by(Call.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        RecentCallOut(
            id=call.id,
            contact_name=contact_name,
            direction=call.direction.value,
            status=call.status.value,
            created_at=call.created_at,
        )
        for call, contact_name in rows
    ]