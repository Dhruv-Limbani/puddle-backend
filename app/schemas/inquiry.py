from typing import Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class InquiryBase(BaseModel):
    buyer_inquiry: Optional[Dict[str, Any]] = Field(default_factory=dict)
    vendor_response: Optional[Dict[str, Any]] = Field(default_factory=dict)
    summary: Optional[str] = None
    status: Optional[Literal[
        "submitted",
        "responded",
        "accepted",
        "rejected",
    ]] = None

class InquiryCreate(InquiryBase):
    buyer_id: UUID
    vendor_id: UUID
    dataset_id: UUID
    conversation_id: Optional[UUID] = None

class InquiryUpdate(BaseModel):
    buyer_inquiry: Optional[Dict[str, Any]] = None
    vendor_response: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
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

class InquiryReadEnriched(InquiryRead):
    """Inquiry read model with resolved display fields for frontend convenience."""
    dataset_title: Optional[str] = None
    vendor_name: Optional[str] = None
    buyer_name: Optional[str] = None

