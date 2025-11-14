-- 1 Lowest-level dependent tables
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chats CASCADE;

-- 2 Entities depending on users
DROP TABLE IF EXISTS dataset_columns CASCADE;
DROP TABLE IF EXISTS datasets CASCADE;
DROP TABLE IF EXISTS ai_agents CASCADE;
DROP TABLE IF EXISTS buyers CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;

-- 3 Root table (referenced by others)
DROP TABLE IF EXISTS users CASCADE;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================
-- 1. USERS (for Authentication)
-- =============================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) CHECK (role IN ('buyer', 'vendor', 'admin')) NOT NULL,
    full_name VARCHAR(255),
    profile_image_url TEXT,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);


-- =============================
-- 2. Vendors
-- =============================
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    industry_focus VARCHAR(255),
    description TEXT,
    contact_email VARCHAR(255),
	contact_phone VARCHAR(50),
    website_url TEXT,
	logo_url TEXT,
    country VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(100),
    address TEXT,
    organization_type VARCHAR(100),   
    founded_year INT,                 
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);


-- =============================
-- 3. Buyers
-- =============================
CREATE TABLE buyers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    contact_email VARCHAR(255),
	contact_phone VARCHAR(50),
    country VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(100),
    address TEXT,
    organization_type VARCHAR(100),   
    job_title VARCHAR(100),           
    industry VARCHAR(100),
	use_case_focus TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- 4. AI AGENT CONFIGURATION
-- =============================
CREATE TABLE ai_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    name VARCHAR(255),
    description TEXT,
    model_used VARCHAR(100) DEFAULT 'gemini-embedding-001',
    config JSONB, -- Custom parameters, policies, escalation rules
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_ai_agents_vendor_id ON ai_agents(vendor_id);

-- =============================
-- 5. DATASETS
-- =============================
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
	status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'draft')),
	visibility VARCHAR(50) DEFAULT 'public' CHECK (visibility IN ('public', 'private')),
    description TEXT,
    domain VARCHAR(100),
    dataset_type VARCHAR(50),
    granularity VARCHAR(100),
    pricing_model VARCHAR(100),
    license VARCHAR(255),
    topics JSONB,
    entities JSONB,              
    temporal_coverage JSONB,     
    geographic_coverage JSONB,
    embedding_input TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- 6. DATASET COLUMNS
-- =============================
CREATE TABLE dataset_columns (
    id BIGSERIAL PRIMARY KEY,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    data_type VARCHAR(100),
    sample_values JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector search
CREATE INDEX datasets_embedding_ivfflat_idx 
ON datasets USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Filters
CREATE INDEX idx_datasets_visibility ON datasets(visibility);
CREATE INDEX idx_datasets_vendor_id ON datasets(vendor_id);
CREATE INDEX idx_datasets_domain ON datasets(domain);

-- Text search
CREATE INDEX idx_datasets_title_trgm 
ON datasets USING gin (title gin_trgm_ops);

-- Optimized buyer search
CREATE INDEX idx_datasets_public_title_trgm 
ON datasets USING gin (title gin_trgm_ops) 
WHERE visibility = 'public';

-- Dataset columns lookup
CREATE INDEX idx_dataset_columns_dataset_id 
ON dataset_columns(dataset_id);


-- =============================
-- 7. CHATS
-- =============================
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,       -- who started the chat
    vendor_id UUID REFERENCES vendors(id) ON DELETE SET NULL,  -- NULL for discovery chats
    agent_id UUID REFERENCES ai_agents(id) ON DELETE SET NULL, -- optional vendor agent
    chat_type VARCHAR(50) NOT NULL CHECK (chat_type IN ('discovery', 'vendor')),
    title VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_chats_vendor_id ON chats(vendor_id);
CREATE INDEX idx_chats_chat_type ON chats(chat_type);

-- =============================
-- 8. CHAT MESSAGES
-- =============================
CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    sender_type VARCHAR(50) NOT NULL CHECK (sender_type IN ('user', 'agent', 'system')),
    message TEXT NOT NULL,
    message_metadata JSONB,  -- e.g. model name, token usage, retrieval context
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_chat_id ON chat_messages(chat_id);
CREATE INDEX idx_chat_messages_sender_type ON chat_messages(sender_type);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at DESC);



CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_vendors_updated_at
BEFORE UPDATE ON vendors
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_buyers_updated_at
BEFORE UPDATE ON buyers
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_agents_updated_at
BEFORE UPDATE ON ai_agents
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at
BEFORE UPDATE ON datasets
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
