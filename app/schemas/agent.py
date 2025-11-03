from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class AgentCreate(BaseModel):
    vendor_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    model_used: Optional[str] = "gemini-embedding-001"
    config: Optional[dict] = None
    active: Optional[bool] = True


class AgentRead(AgentCreate):
    id: str
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }
