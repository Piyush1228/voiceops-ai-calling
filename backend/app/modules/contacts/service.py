from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.modules.contacts import repository
from app.modules.contacts.schemas import ContactCreate, ContactUpdate
from app.modules.users.models import User


def create_contact(db: Session, current_user: User, payload: ContactCreate):
    return repository.create_contact(
        db=db,
        user_id=current_user.id,
        name=payload.name,
        phone_number=payload.phone_number,
        notes=payload.notes,
    )


def list_contacts(db: Session, current_user: User, skip: int, limit: int):
    return repository.get_contacts_for_user(db, current_user.id, skip, limit)


def get_contact(db: Session, current_user: User, contact_id: int):
    contact = repository.get_contact_by_id(db, contact_id, current_user.id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
    return contact


def update_contact(db: Session, current_user: User, contact_id: int, payload: ContactUpdate):
    contact = get_contact(db, current_user, contact_id)  # reuses 404 + ownership check
    return repository.update_contact(db, contact, payload.model_dump(exclude_unset=True))


def delete_contact(db: Session, current_user: User, contact_id: int):
    contact = get_contact(db, current_user, contact_id)
    repository.delete_contact(db, contact)