from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class InquiryBase(BaseModel):
    buyer_inquiry: Optional[Dict[str, Any]] = {}
    vendor_response: Optional[Dict[str, Any]] = {}
    status: Optional[str] = "draft"

class InquiryCreate(InquiryBase):
    buyer_id: UUID
    vendor_id: UUID
    dataset_id: UUID
    conversation_id: Optional[UUID] = None

class InquiryUpdate(BaseModel):
    buyer_inquiry: Optional[Dict[str, Any]] = None
    vendor_response: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class InquiryRead(InquiryBase):
    id: UUID
    buyer_id: UUID
    vendor_id: UUID
    dataset_id: UUID
    conversation_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

