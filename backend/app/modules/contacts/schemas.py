from datetime import datetime

from pydantic import BaseModel, field_validator


class ContactCreate(BaseModel):
    name: str
    phone_number: str
    notes: str | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith("+"):
            raise ValueError("Phone number must be in E.164 format, e.g. +14155552671")
        return cleaned


class ContactUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    notes: str | None = None


class ContactOut(BaseModel):
    id: int
    name: str
    phone_number: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True