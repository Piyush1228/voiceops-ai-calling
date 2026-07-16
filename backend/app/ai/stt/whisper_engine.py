import numpy as np
from faster_whisper import WhisperModel

# "base" balances speed and accuracy for CPU inference.
# Options: tiny, base, small, medium, large-v3 (bigger = more accurate, slower)
_model = WhisperModel("base", device="cpu", compute_type="int8")


def transcribe_audio(pcm_audio: np.ndarray) -> str:
    """
    Takes 16kHz mono PCM float32 audio and returns transcribed text.
    """
    segments, _ = _model.transcribe(pcm_audio, language="en", beam_size=5)
    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip()