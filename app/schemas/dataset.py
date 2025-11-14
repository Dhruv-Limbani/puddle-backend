# app/schemas/dataset.py
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class DatasetColumn(BaseModel):
    name: str
    description: Optional[str] = None
    data_type: Optional[str] = None
    sample_values: Optional[Any] = None


class DatasetColumnRead(DatasetColumn):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


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
    # At least one column is required when creating a dataset
    columns: List[DatasetColumn] = Field(..., min_length=1)
    embedding_input: Optional[str] = None
    embedding: Optional[List[float]] = None


class DatasetUpdate(BaseModel):
    title: Optional[str] = None
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
    visibility: Optional[str] = None
    status: Optional[str] = None
    # If provided, columns will replace existing columns entirely
    columns: Optional[List[DatasetColumn]] = None


class DatasetRead(DatasetCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
    columns: Optional[List[DatasetColumnRead]] = None

    model_config = {"from_attributes": True}
