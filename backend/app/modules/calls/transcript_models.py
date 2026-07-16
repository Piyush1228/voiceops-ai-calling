import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from app.database import Base


class SpeakerType(str, enum.Enum):
    CALLER = "caller"
    AI = "ai"


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False, index=True)

    speaker = Column(Enum(SpeakerType), nullable=False)
    text = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    call = relationship("Call")