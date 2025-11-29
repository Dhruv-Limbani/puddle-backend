from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    user_id: UUID

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class ConversationRead(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

