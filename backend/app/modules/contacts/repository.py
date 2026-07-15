from sqlalchemy.orm import Session

from app.modules.contacts.models import Contact


def create_contact(db: Session, user_id: int, name: str, phone_number: str, notes: str | None) -> Contact:
    contact = Contact(user_id=user_id, name=name, phone_number=phone_number, notes=notes)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def get_contacts_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> list[Contact]:
    return (
        db.query(Contact)
        .filter(Contact.user_id == user_id)
        .order_by(Contact.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_contact_by_id(db: Session, contact_id: int, user_id: int) -> Contact | None:
    return (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.user_id == user_id)
        .first()
    )


def update_contact(db: Session, contact: Contact, updates: dict) -> Contact:
    for field, value in updates.items():
        if value is not None:
            setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact: Contact) -> None:
    db.delete(contact)
    db.commit()