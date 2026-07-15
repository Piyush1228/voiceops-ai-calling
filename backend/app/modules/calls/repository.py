from sqlalchemy.orm import Session

from app.modules.calls.models import Call, CallStatus, CallDirection


def create_call(db: Session, user_id: int, contact_id: int, direction: CallDirection) -> Call:
    call = Call(user_id=user_id, contact_id=contact_id, direction=direction, status=CallStatus.QUEUED)
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


def get_calls_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> list[Call]:
    return (
        db.query(Call)
        .filter(Call.user_id == user_id)
        .order_by(Call.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_call_by_id(db: Session, call_id: int, user_id: int) -> Call | None:
    return db.query(Call).filter(Call.id == call_id, Call.user_id == user_id).first()


def update_call_status(db: Session, call: Call, status: CallStatus) -> Call:
    call.status = status
    db.commit()
    db.refresh(call)
    return call