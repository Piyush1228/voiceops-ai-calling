import base64
import json

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ai.stt.audio_utils import mulaw_to_pcm_float32
from app.ai.stt.whisper_engine import transcribe_audio
from app.ai.llm.ollama_engine import generate_response
from app.ai.llm.conversation_memory import ConversationMemory
from app.database import SessionLocal
from app.modules.calls.models import Call
from app.modules.calls.transcript_repository import add_transcript_entry
from app.modules.calls.transcript_models import SpeakerType

router = APIRouter()

BUFFER_SECONDS = 3
SAMPLE_RATE = 16000
BUFFER_SIZE_SAMPLES = BUFFER_SECONDS * SAMPLE_RATE


@router.websocket("/ws/twilio/stream")
async def twilio_media_stream(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = np.array([], dtype=np.float32)
    memory = ConversationMemory()
    call_id: int | None = None

    try:
        while True:
            raw_message = await websocket.receive_text()
            message = json.loads(raw_message)
            event = message.get("event")

            if event == "start":
                twilio_call_sid = message["start"]["callSid"]
                call_id = _lookup_call_id(twilio_call_sid)
                print("Media stream started for call_id:", call_id)

            elif event == "media":
                payload_b64 = message["media"]["payload"]
                mulaw_bytes = base64.b64decode(payload_b64)
                pcm_chunk = mulaw_to_pcm_float32(mulaw_bytes)
                audio_buffer = np.concatenate([audio_buffer, pcm_chunk])

                if len(audio_buffer) >= BUFFER_SIZE_SAMPLES:
                    text = transcribe_audio(audio_buffer)
                    audio_buffer = np.array([], dtype=np.float32)

                    if text:
                        print("Caller said:", text)
                        memory.add_user_message(text)
                        _save_transcript(call_id, SpeakerType.CALLER, text)

                        ai_reply = generate_response(memory.get_messages())
                        print("AI would say:", ai_reply)
                        memory.add_ai_message(ai_reply)
                        _save_transcript(call_id, SpeakerType.AI, ai_reply)

            elif event == "stop":
                print("Media stream stopped.")
                break

    except WebSocketDisconnect:
        print("WebSocket disconnected.")


def _lookup_call_id(twilio_call_sid: str) -> int | None:
    db = SessionLocal()
    try:
        call = db.query(Call).filter(Call.twilio_sid == twilio_call_sid).first()
        return call.id if call else None
    finally:
        db.close()


def _save_transcript(call_id: int | None, speaker: SpeakerType, text: str):
    if call_id is None:
        return
    db = SessionLocal()
    try:
        add_transcript_entry(db, call_id, speaker, text)
    finally:
        db.close()