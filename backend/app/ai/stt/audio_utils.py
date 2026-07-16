import audioop
import numpy as np


def mulaw_to_pcm_float32(mulaw_bytes: bytes) -> np.ndarray:
    """
    Converts 8kHz mulaw audio (Twilio's format) into
    16kHz mono float32 PCM (Whisper's expected format).
    """
    # Step 1: mulaw -> 16-bit linear PCMimport audioop
import numpy as np


def mulaw_to_pcm_float32(mulaw_bytes: bytes) -> np.ndarray:
    """
    Converts 8kHz mulaw audio (Twilio's format) into
    16kHz mono float32 PCM (Whisper's expected format).
    """
    # Step 1: mulaw -> 16-bit linear PCM
    pcm16 = audioop.ulaw2lin(mulaw_bytes, 2)

    # Step 2: upsample 8kHz -> 16kHz (Whisper expects 16kHz)
    pcm16_resampled, _ = audioop.ratecv(pcm16, 2, 1, 8000, 16000, None)

    # Step 3: convert 16-bit int PCM -> float32 in range [-1, 1]
    audio_array = np.frombuffer(pcm16_resampled, dtype=np.int16).astype(np.float32) / 32768.0
    return audio_array
    pcm16 = audioop.ulaw2lin(mulaw_bytes, 2)

    # Step 2: upsample 8kHz -> 16kHz (Whisper expects 16kHz)
    pcm16_resampled, _ = audioop.ratecv(pcm16, 2, 1, 8000, 16000, None)

    # Step 3: convert 16-bit int PCM -> float32 in range [-1, 1]
    audio_array = np.frombuffer(pcm16_resampled, dtype=np.int16).astype(np.float32) / 32768.0
    return audio_array