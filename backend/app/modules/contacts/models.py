from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User")