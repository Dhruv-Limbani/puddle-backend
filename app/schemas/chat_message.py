from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ChatMessageCreate(BaseModel):
    chat_id: UUID
    sender_type: str  # 'user', 'agent', 'system'
    message: str
    message_metadata: Optional[Any] = None  # JSONB


class ChatMessageRead(ChatMessageCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
