from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    role: str  # 'buyer', 'vendor', or 'admin'
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: Optional[bool] = True


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    last_login: Optional[datetime] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
