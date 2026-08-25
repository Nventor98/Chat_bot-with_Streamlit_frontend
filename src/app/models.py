import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
