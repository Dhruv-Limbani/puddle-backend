import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
    BigInteger,
)
from sqlalchemy.orm import relationship
from app.core.db import Base

# Postgres-specific types (fallback for SQLite/local dev)
try:
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
except Exception:
    PG_UUID, JSONB = None, None

# pgvector integration (optional)
try:
    from pgvector.sqlalchemy import Vector as PGVector
except Exception:
    PGVector = None


# =============================
# Helpers
# =============================

def gen_uuid() -> str:
    return str(uuid.uuid4())


def uuid_column(primary_key: bool = False, fk: bool = False) -> Column:
    """Return a UUID column for Postgres or fallback to String(36)."""
    if PG_UUID is not None:
        return Column(PG_UUID(as_uuid=False), primary_key=primary_key, default=gen_uuid)
    return Column(String(36), primary_key=primary_key, default=gen_uuid)


# =============================
# USERS (Base Reference)
# =============================

class User(Base):
    __tablename__ = "users"

    id = uuid_column(primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(50), nullable=False)
    full_name = Column(String(255), nullable=True)
    profile_image_url = Column(Text, nullable=True)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    vendor_profile = relationship("Vendor", uselist=False, back_populates="user")
    buyer_profile = relationship("Buyer", uselist=False, back_populates="user")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


# =============================
# VENDORS
# =============================

class Vendor(Base):
    __tablename__ = "vendors"

    id = uuid_column(primary_key=True)
    if PG_UUID is not None:
        user_id = Column(PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    else:
        user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    industry_focus = Column(String(255))
    description = Column(Text)
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    website_url = Column(Text)
    logo_url = Column(Text)
    country = Column(String(100))
    region = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    organization_type = Column(String(100))
    founded_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="vendor_profile")
    datasets = relationship("Dataset", back_populates="vendor", cascade="all, delete-orphan")
    ai_agents = relationship("AIAgent", back_populates="vendor", cascade="all, delete-orphan")
    inquiries = relationship("Inquiry", back_populates="vendor", cascade="all, delete-orphan")


# =============================
# BUYERS
# =============================

class Buyer(Base):
    __tablename__ = "buyers"

    id = uuid_column(primary_key=True)
    if PG_UUID is not None:
        user_id = Column(PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    else:
        user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    organization = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    country = Column(String(100))
    region = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    organization_type = Column(String(100))
    job_title = Column(String(100))
    industry = Column(String(100))
    use_case_focus = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="buyer_profile")
    inquiries = relationship("Inquiry", back_populates="buyer", cascade="all, delete-orphan")


# =============================
# AI AGENTS
# =============================

class AIAgent(Base):
    __tablename__ = "ai_agents"

    id = uuid_column(primary_key=True)
    if PG_UUID is not None:
        vendor_id = Column(PG_UUID(as_uuid=False), ForeignKey("vendors.id", ondelete="CASCADE"))
    else:
        vendor_id = Column(String(36), ForeignKey("vendors.id", ondelete="CASCADE"))
    name = Column(String(255))
    description = Column(Text)
    model_used = Column(String(100), default="gemini-embedding-001")
    config = Column(JSONB if JSONB else JSON)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="ai_agents")


# =============================
# DATASETS
# =============================

class Dataset(Base):
    __tablename__ = "datasets"

    id = uuid_column(primary_key=True)
    if PG_UUID is not None:
        vendor_id = Column(PG_UUID(as_uuid=False), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    else:
        vendor_id = Column(String(36), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    status = Column(String(50), default="active")
    visibility = Column(String(50), default="public")
    description = Column(Text)
    domain = Column(String(100))
    dataset_type = Column(String(50))
    granularity = Column(String(100))
    pricing_model = Column(String(100))
    license = Column(String(255))
    topics = Column(JSONB if JSONB else JSON)
    entities = Column(JSONB if JSONB else JSON)
    temporal_coverage = Column(JSONB if JSONB else JSON)
    geographic_coverage = Column(JSONB if JSONB else JSON)
    embedding_input = Column(Text)
    embedding = Column(PGVector(1536) if PGVector else JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="datasets")
    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")
    inquiries = relationship("Inquiry", back_populates="dataset", cascade="all, delete-orphan")


# =============================
# DATASET COLUMNS
# =============================

class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    if PG_UUID is not None:
        dataset_id = Column(PG_UUID(as_uuid=False), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    else:
        dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    data_type = Column(String(100))
    sample_values = Column(JSONB if JSONB else JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="columns")


# =============================
# CONVERSATIONS
# =============================

class Conversation(Base):
    __tablename__ = "conversations"

    id = uuid_column(primary_key=True)
    if PG_UUID is not None:
        user_id = Column(PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    else:
        user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    inquiries = relationship("Inquiry", back_populates="conversation")


# =============================
# CHAT MESSAGES
# =============================

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    if PG_UUID is not None:
        conversation_id = Column(PG_UUID(as_uuid=False), ForeignKey("conversations.id", ondelete="CASCADE"))
    else:
        conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    tool_call = Column(JSONB if JSONB else JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


# =============================
# INQUIRIES
# =============================

class Inquiry(Base):
    __tablename__ = "inquiries"

    id = uuid_column(primary_key=True)

    # Foreign Keys
    if PG_UUID is not None:
        buyer_id = Column(PG_UUID(as_uuid=False), ForeignKey("buyers.id", ondelete="CASCADE"))
        vendor_id = Column(PG_UUID(as_uuid=False), ForeignKey("vendors.id", ondelete="CASCADE"))
        dataset_id = Column(PG_UUID(as_uuid=False), ForeignKey("datasets.id", ondelete="CASCADE"))
        conversation_id = Column(PG_UUID(as_uuid=False), ForeignKey("conversations.id", ondelete="SET NULL"))
    else:
        buyer_id = Column(String(36), ForeignKey("buyers.id", ondelete="CASCADE"))
        vendor_id = Column(String(36), ForeignKey("vendors.id", ondelete="CASCADE"))
        dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"))
        conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"))

    # JSON State
    buyer_inquiry = Column(JSONB if JSONB else JSON, default=dict)
    vendor_response = Column(JSONB if JSONB else JSON, default=dict)

    # Status
    status = Column(String(50), default="draft")
    # Allowed values: 'draft', 'submitted', 'pending_review', 'responded', 'accepted', 'rejected'

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    buyer = relationship("Buyer", back_populates="inquiries")
    vendor = relationship("Vendor", back_populates="inquiries")
    dataset = relationship("Dataset", back_populates="inquiries")
    conversation = relationship("Conversation", back_populates="inquiries")