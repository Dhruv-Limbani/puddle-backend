from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class DatasetCreate(BaseModel):
    vendor_id: UUID
    title: str
    description: Optional[str] = None
    domain: Optional[str] = None
    dataset_type: Optional[str] = None
    granularity: Optional[str] = None
    pricing_model: Optional[str] = None
    license: Optional[str] = None
    topics: Optional[Any] = None
    entities: Optional[Any] = None
    temporal_coverage: Optional[Any] = None
    geographic_coverage: Optional[Any] = None
    visibility: Optional[str] = "public"
    status: Optional[str] = "active"
    columns: Optional[List[Dict[str, Any]]] = None  # for input only, mapped to dataset_columns
    embedding_input: Optional[str] = None
    embedding: Optional[List[float]] = None


class DatasetRead(DatasetCreate):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }
