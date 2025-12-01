from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator


class ToolCallItem(BaseModel):
    name: str
    arguments: Dict[str, Any]
    result: Optional[str] = None
    result_json: Optional[Any] = None  # Structured data when tool returns JSON


class ToolCallPayload(BaseModel):
    calls: List[ToolCallItem]
    trace_id: Optional[str] = None

class ChatMessageBase(BaseModel):
    role: str
    content: str
    tool_call: Optional[Union[ToolCallPayload, Dict[str, Any]]] = None
    
    @field_validator('tool_call', mode='before')
    @classmethod
    def validate_tool_call(cls, v):
        if v is None:
            return v
        if isinstance(v, dict):
            # Handle old format: convert to new format with calls array
            if 'calls' not in v:
                # Old format detected, wrap in calls array
                return {'calls': [v], 'trace_id': None}
        return v

class ChatMessageCreate(ChatMessageBase):
    conversation_id: UUID

class ChatMessageRead(ChatMessageBase):
    id: int
    conversation_id: UUID
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
