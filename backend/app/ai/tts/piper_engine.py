import io
import wave

from piper import PiperVoice

VOICE_MODEL_PATH = "app/ai/tts/voices/en_US-lessac-medium.onnx"
VOICE_CONFIG_PATH = "app/ai/tts/voices/en_US-lessac-medium.onnx.json"

_voice = PiperVoice.load(VOICE_MODEL_PATH, config_path=VOICE_CONFIG_PATH)


def synthesize_speech(text: str) -> tuple[bytes, int]:
    """
    Converts text into 16-bit PCM audio bytes using Piper.
    Returns (pcm_bytes, sample_rate).
    """
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        _voice.synthesize_wav(text, wav_file)

    buffer.seek(0)
    with wave.open(buffer, "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        pcm_bytes = wav_file.readframes(wav_file.getnframes())

    return pcm_bytes, sample_rate