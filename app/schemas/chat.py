from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ChatCreate(BaseModel):
    user_id: UUID
    vendor_id: Optional[UUID] = None  # NULL for discovery chats
    agent_id: Optional[UUID] = None   # optional vendor agent
    chat_type: str  # 'discovery' or 'vendor'
    title: Optional[str] = None
    is_active: Optional[bool] = True


class ChatRead(ChatCreate):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
