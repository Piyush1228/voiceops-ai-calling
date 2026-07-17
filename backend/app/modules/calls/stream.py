import base64
import json
import asyncio

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.ai.stt.audio_utils import mulaw_to_pcm_float32
from app.ai.stt.whisper_engine import transcribe_audio
from app.ai.llm.ollama_engine import generate_response
from app.ai.llm.conversation_memory import ConversationMemory
from app.ai.tts.piper_engine import synthesize_speech
from app.ai.tts.audio_utils import pcm16_to_mulaw
from app.database import SessionLocal
from app.modules.calls.models import Call
from app.modules.calls.transcript_repository import add_transcript_entry
from app.modules.calls.transcript_models import SpeakerType

router = APIRouter()

BUFFER_SECONDS = 3
SAMPLE_RATE = 16000
BUFFER_SIZE_SAMPLES = BUFFER_SECONDS * SAMPLE_RATE
OUTBOUND_CHUNK_SIZE = 320  # 20ms of 8kHz mulaw audio per Twilio message


@router.websocket("/ws/twilio/stream")
async def twilio_media_stream(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = np.array([], dtype=np.float32)
    memory = ConversationMemory()
    call_id: int | None = None
    stream_sid: str | None = None
    is_ai_speaking = False  # simple turn-taking guard to prevent self-transcription

    try:
        while True:
            raw_message = await websocket.receive_text()
            message = json.loads(raw_message)
            event = message.get("event")

            if event == "start":
                twilio_call_sid = message["start"]["callSid"]
                stream_sid = message["start"]["streamSid"]
                call_id = _lookup_call_id(twilio_call_sid)
                print("Media stream started for call_id:", call_id)

            elif event == "media":
                # While the AI is speaking, ignore incoming audio entirely.
                # This prevents the AI's own voice (leaking into the mic)
                # from being transcribed as if the caller said it.
                if is_ai_speaking:
                    continue

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

                        is_ai_speaking = True
                        await _speak_to_caller(websocket, stream_sid, ai_reply)
                        await asyncio.sleep(0.8)  # let Twilio finish actually playing the audio
                        is_ai_speaking = False

            elif event == "stop":
                print("Media stream stopped.")
                break

    except WebSocketDisconnect:
        print("WebSocket disconnected.")


async def _speak_to_caller(websocket: WebSocket, stream_sid: str, text: str):
    """
    Synthesizes speech from text and streams it back to Twilio
    in small chunks, formatted exactly as Twilio's Media Streams protocol expects.
    Stops immediately and quietly if the call has already ended.
    """
    pcm_bytes, source_rate = synthesize_speech(text)
    mulaw_bytes = pcm16_to_mulaw(pcm_bytes, source_rate)

    for i in range(0, len(mulaw_bytes), OUTBOUND_CHUNK_SIZE):
        if websocket.client_state != WebSocketState.CONNECTED:
            print("Call ended mid-response; stopping playback.")
            return

        chunk = mulaw_bytes[i:i + OUTBOUND_CHUNK_SIZE]
        payload_b64 = base64.b64encode(chunk).decode("utf-8")

        message = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {"payload": payload_b64},
        }
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            print("Call ended mid-response; stopping playback.")
            return


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