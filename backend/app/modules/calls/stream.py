import base64
import json

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ai.stt.audio_utils import mulaw_to_pcm_float32
from app.ai.stt.whisper_engine import transcribe_audio

router = APIRouter()

# How much audio to buffer before running transcription (in seconds).
# Smaller = more responsive but less accurate; larger = opposite.
BUFFER_SECONDS = 3
SAMPLE_RATE = 16000
BUFFER_SIZE_SAMPLES = BUFFER_SECONDS * SAMPLE_RATE


@router.websocket("/ws/twilio/stream")
async def twilio_media_stream(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = np.array([], dtype=np.float32)

    try:
        while True:
            raw_message = await websocket.receive_text()
            message = json.loads(raw_message)
            event = message.get("event")

            if event == "start":
                print("Media stream started:", message["start"]["callSid"])

            elif event == "media":
                payload_b64 = message["media"]["payload"]
                mulaw_bytes = base64.b64decode(payload_b64)
                pcm_chunk = mulaw_to_pcm_float32(mulaw_bytes)
                audio_buffer = np.concatenate([audio_buffer, pcm_chunk])

                if len(audio_buffer) >= BUFFER_SIZE_SAMPLES:
                    text = transcribe_audio(audio_buffer)
                    if text:
                        print("Caller said:", text)
                    audio_buffer = np.array([], dtype=np.float32)

            elif event == "stop":
                print("Media stream stopped.")
                break

    except WebSocketDisconnect:
        print("WebSocket disconnected.")