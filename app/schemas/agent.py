from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AgentCreate(BaseModel):
    vendor_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    model_used: Optional[str] = "gemini-embedding-001"
    config: Optional[dict] = None
    active: Optional[bool] = True


class AgentRead(AgentCreate):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }
