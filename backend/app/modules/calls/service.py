from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.modules.calls import repository
from app.modules.calls.schemas import CallCreate
from app.modules.calls.models import CallDirection
from app.modules.calls.twilio_client import place_outbound_call
from app.modules.contacts import repository as contacts_repository
from app.modules.users.models import User


def create_call(db: Session, current_user: User, payload: CallCreate):
    contact = contacts_repository.get_contact_by_id(db, payload.contact_id, current_user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    call = repository.create_call(
        db=db,
        user_id=current_user.id,
        contact_id=contact.id,
        direction=payload.direction,
    )

    if payload.direction == CallDirection.OUTBOUND:
        twilio_sid = place_outbound_call(to_number=contact.phone_number, call_id=call.id)
        call.twilio_sid = twilio_sid
        db.commit()
        db.refresh(call)

    return call


def list_calls(db: Session, current_user: User, skip: int, limit: int):
    return repository.get_calls_for_user(db, current_user.id, skip, limit)


def get_call(db: Session, current_user: User, call_id: int):
    call = repository.get_call_by_id(db, call_id, current_user.id)
    if not call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found.")
    return call