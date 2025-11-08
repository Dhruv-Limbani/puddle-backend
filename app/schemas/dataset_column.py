from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class DatasetColumnCreate(BaseModel):
    dataset_id: UUID
    name: str
    description: Optional[str] = None
    data_type: Optional[str] = None
    sample_values: Optional[Any] = None


class DatasetColumnUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    sample_values: Optional[Any] = None


class DatasetColumnRead(DatasetColumnCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }
