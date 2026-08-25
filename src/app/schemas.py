from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    created_at: datetime


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    messages: List[MessageOut] = []
