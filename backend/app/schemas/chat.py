from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    content: str
    role: str = "user"


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    ai_provider: Optional[str] = "gemini"


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    ai_provider: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    ai_provider: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    ai_provider: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    conversation_id: int
    message: MessageResponse
    response: MessageResponse
