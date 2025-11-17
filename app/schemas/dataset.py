# app/schemas/dataset.py
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# --- COLUMN SCHEMAS ---

class DatasetColumnBase(BaseModel):
    name: str
    description: Optional[str] = None
    data_type: Optional[str] = None
    sample_values: Optional[Any] = None

class DatasetColumn(DatasetColumnBase):
    # This is for creating/updating columns.
    # If 'id' is present, it's an update. If not, it's a create.
    id: Optional[int] = None 

class DatasetColumnRead(DatasetColumnBase):
    id: int
    created_at: datetime
    dataset_id: UUID # Added for clarity

    model_config = {"from_attributes": True}


# --- DATASET SCHEMAS ---

# ** BUG FIX: Create a Base schema for common fields **
class DatasetBase(BaseModel):
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
    embedding_input: Optional[str] = None
    embedding: Optional[List[float]] = None


class DatasetCreate(DatasetBase):
    vendor_id: UUID
    # At least one column is required when creating a dataset
    columns: List[DatasetColumn] = Field(..., min_length=1)


class DatasetUpdate(BaseModel):
    # All fields are optional for updates
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
    # Use DatasetColumn, which can include 'id' for updates
    columns: Optional[List[DatasetColumn]] = None


# ** BUG FIX: DatasetRead should inherit from Base, not Create **
# This ensures 'columns' is defined correctly for output
class DatasetRead(DatasetBase):
    id: UUID
    vendor_id: UUID
    created_at: datetime
    updated_at: datetime
    # Use DatasetColumnRead and provide a default empty list
    columns: List[DatasetColumnRead] = []

    model_config = {"from_attributes": True}