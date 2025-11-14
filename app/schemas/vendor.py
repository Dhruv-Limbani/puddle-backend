from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class VendorCreate(BaseModel):
    name: str
    industry_focus: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    organization_type: Optional[str] = None
    founded_year: Optional[int] = None
    user_id: Optional[UUID] = None


class VendorRead(VendorCreate):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }
