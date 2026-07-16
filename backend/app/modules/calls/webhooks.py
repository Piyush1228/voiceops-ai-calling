from datetime import datetime

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.twiml.voice_response import VoiceResponse, Connect

from app.config import settings
from app.database import get_db
from app.modules.calls.models import Call, CallStatus

router = APIRouter(prefix="/webhooks/twilio", tags=["Twilio Webhooks"])

# Maps Twilio's own status strings to our internal enum
TWILIO_STATUS_MAP = {
    "queued": CallStatus.QUEUED,
    "initiated": CallStatus.QUEUED,
    "ringing": CallStatus.RINGING,
    "in-progress": CallStatus.IN_PROGRESS,
    "completed": CallStatus.COMPLETED,
    "busy": CallStatus.NO_ANSWER,
    "no-answer": CallStatus.NO_ANSWER,
    "failed": CallStatus.FAILED,
    "canceled": CallStatus.FAILED,
}


@router.post("/voice")
async def handle_voice(request: Request):
    """
    Twilio hits this the moment a call connects.
    We open a live Media Stream so we can transcribe the
    caller's speech in real time instead of just speaking a static line.
    """
    response = VoiceResponse()
    ws_url = settings.public_base_url.replace("https://", "wss://").replace("http://", "ws://")

    connect = Connect()
    connect.stream(url=f"{ws_url}/ws/twilio/stream")
    response.append(connect)

    return Response(content=str(response), media_type="application/xml")


@router.post("/status")
async def handle_status(
    request: Request,
    call_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Twilio hits this repeatedly as call state changes.
    We update our own Call row to reflect the real-world status.
    """
    form = await request.form()
    twilio_status = form.get("CallStatus")
    twilio_sid = form.get("CallSid")

    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        return Response(status_code=200)  # acknowledge anyway; nothing to update

    if twilio_sid and not call.twilio_sid:
        call.twilio_sid = twilio_sid

    mapped_status = TWILIO_STATUS_MAP.get(twilio_status)
    if mapped_status:
        call.status = mapped_status

    if mapped_status == CallStatus.IN_PROGRESS and not call.started_at:
        call.started_at = datetime.utcnow()
    if mapped_status in (CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.NO_ANSWER):
        call.ended_at = datetime.utcnow()

    db.commit()
    return Response(status_code=200)