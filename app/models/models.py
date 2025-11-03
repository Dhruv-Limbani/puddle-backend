import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean, JSON, BigInteger
from sqlalchemy.orm import relationship

from app.core.db import Base

# Try to import Postgres-specific types where available. If not available
# fall back to generic SQLAlchemy types so local dev (SQLite) still works.
try:
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
except Exception:
    PG_UUID = None
    JSONB = None

try:
    # pgvector SQLAlchemy type (optional)
    from pgvector.sqlalchemy import Vector as PGVector
except Exception:
    PGVector = None


def gen_uuid() -> str:
    return str(uuid.uuid4())


def uuid_column(primary_key: bool = False):
    """Return a Column configured as UUID for Postgres or String fallback."""
    if PG_UUID is not None:
        return Column(PG_UUID(as_uuid=False), primary_key=primary_key, default=gen_uuid)
    return Column(String(36), primary_key=primary_key, default=gen_uuid)


class Vendor(Base):
    __tablename__ = "vendors"

    id = uuid_column(primary_key=True)
    name = Column(String(255), nullable=False)
    industry_focus = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    website_url = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    organization_type = Column(String(100), nullable=True)
    founded_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    datasets = relationship("Dataset", back_populates="vendor", cascade="all, delete-orphan")
    ai_agents = relationship("AIAgent", back_populates="vendor", cascade="all, delete-orphan")


class Buyer(Base):
    __tablename__ = "buyers"

    id = uuid_column(primary_key=True)
    name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    organization_type = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    use_case_focus = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AIAgent(Base):
    __tablename__ = "ai_agents"

    id = uuid_column(primary_key=True)
    vendor_id = Column(String(36), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    model_used = Column(String(100), default="gemini-embedding-001")
    config = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="ai_agents")


class Dataset(Base):
    __tablename__ = "datasets"

    id = uuid_column(primary_key=True)
    vendor_id = Column(String(36), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    status = Column(String(50), default="active")
    visibility = Column(String(50), default="public")
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)
    dataset_type = Column(String(50), nullable=True)
    granularity = Column(String(100), nullable=True)
    pricing_model = Column(String(100), nullable=True)
    license = Column(String(255), nullable=True)
    # Use JSONB on Postgres if available for better indexing; otherwise JSON
    topics = Column(JSONB if JSONB is not None else JSON, nullable=True)
    entities = Column(JSONB if JSONB is not None else JSON, nullable=True)
    temporal_coverage = Column(JSONB if JSONB is not None else JSON, nullable=True)
    geographic_coverage = Column(JSONB if JSONB is not None else JSON, nullable=True)
    embedding_input = Column(Text, nullable=True)
    # If pgvector is available use a Vector column; otherwise fall back to JSON list
    if PGVector is not None:
        embedding = Column(PGVector(1536), nullable=True)
    else:
        embedding = Column(JSON, nullable=True)  # store list[float] safely across DBs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="datasets")
    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")


class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    # BIGSERIAL primary key on Postgres -> BigInteger with autoincrement
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    # Use Postgres UUID type for FK when available, otherwise use string(36)
    if PG_UUID is not None:
        dataset_id = Column(PG_UUID(as_uuid=False), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    else:
        dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    data_type = Column(String(100), nullable=True)
    sample_values = Column(JSONB if JSONB is not None else JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="columns")
