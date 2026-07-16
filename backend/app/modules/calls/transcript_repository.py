from sqlalchemy.orm import Session

from app.modules.calls.transcript_models import Transcript, SpeakerType


def add_transcript_entry(db: Session, call_id: int, speaker: SpeakerType, text: str) -> Transcript:
    entry = Transcript(call_id=call_id, speaker=speaker, text=text)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_transcripts_for_call(db: Session, call_id: int) -> list[Transcript]:
    return (
        db.query(Transcript)
        .filter(Transcript.call_id == call_id)
        .order_by(Transcript.created_at.asc())
        .all()
    )