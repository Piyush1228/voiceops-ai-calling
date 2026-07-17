import audioop


def pcm16_to_mulaw(pcm_bytes: bytes, source_rate: int) -> bytes:
    """
    Converts 16-bit PCM audio (Piper's output) at any sample rate
    into 8kHz mulaw bytes - the format Twilio requires to play
    audio back into a live call.
    """
    resampled, _ = audioop.ratecv(pcm_bytes, 2, 1, source_rate, 8000, None)
    mulaw_bytes = audioop.lin2ulaw(resampled, 2)
    return mulaw_bytes