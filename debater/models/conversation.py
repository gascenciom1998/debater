from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    USER = "user"
    BOT = "bot"


class Message(BaseModel):
    role: Role
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Conversation(BaseModel):
    conversation_id: str
    topic: str
    bot_position: str
    first_message: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DebateRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class DebateResponse(BaseModel):
    conversation_id: str
    messages: List[Message]