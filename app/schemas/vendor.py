from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class VendorCreate(BaseModel):
    name: str
    industry_focus: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    website_url: Optional[str] = None
    country: Optional[str] = None
    organization_type: Optional[str] = None
    founded_year: Optional[int] = None


class VendorRead(VendorCreate):
    id: str
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }
