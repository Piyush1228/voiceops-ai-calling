from datetime import datetime

from pydantic import BaseModel

from app.modules.calls.models import CallDirection, CallStatus


class CallCreate(BaseModel):
    contact_id: int
    direction: CallDirection


class CallOut(BaseModel):
    id: int
    contact_id: int
    direction: CallDirection
    status: CallStatus
    twilio_sid: str | None
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True