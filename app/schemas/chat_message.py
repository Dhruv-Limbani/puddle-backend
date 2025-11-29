from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ChatMessageBase(BaseModel):
    role: str
    content: str
    tool_call: Optional[Any] = None

class ChatMessageCreate(ChatMessageBase):
    conversation_id: UUID

class ChatMessageRead(ChatMessageBase):
    id: int
    conversation_id: UUID
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
