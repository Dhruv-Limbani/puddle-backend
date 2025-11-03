from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class BuyerCreate(BaseModel):
    name: str
    organization: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    country: Optional[str] = None
    organization_type: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    use_case_focus: Optional[str] = None


class BuyerRead(BuyerCreate):
    id: str
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }
