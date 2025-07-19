from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class Role(str, Enum):
    USER = "user"
    BOT = "bot"


class Message(BaseModel):
    role: Role
    message: str


class Conversation(BaseModel):
    conversation_id: str
    topic: str
    bot_position: str
    first_message: str
    messages: List[Message] = []


class DebateRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class DebateResponse(BaseModel):
    conversation_id: str
    message: List[Message]  # Challenge requires "message" not "messages"