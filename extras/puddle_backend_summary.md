# Puddle Backend API - Complete Frontend Integration Guide

## Project Overview

**Puddle** is an intelligent marketplace platform that connects dataset vendors and buyers. For the MVP, we focus exclusively on the dataset marketplace (not the insights/API part via MCP).

### Key Features
- User authentication with role-based access control (Admin, Vendor, Buyer)
- Dataset management with vector similarity search
- Vendor and buyer profile management
- AI agent configuration for vendors
- Chat functionality between users, vendors, and AI agents
- Dataset discovery and filtering

---

## Architecture Overview

### Technology Stack
- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector extension
- **Authentication**: JWT (OAuth2 Password Bearer)
- **API Versioning**: `/api/v1/`
- **Vector Search**: pgvector with cosine similarity

### Database Extensions
- `pgvector` - Vector similarity search
- `pg_trgm` - Trigram-based text search
- `uuid-ossp` - UUID generation

---

## Authentication & Authorization

### Authentication Flow

#### 1. User Registration
**Endpoint**: `POST /api/v1/auth/register`

**Query Parameters**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "buyer|vendor|admin",
  "full_name": "John Doe" // optional
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "buyer",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

#### 2. User Login
**Endpoint**: `POST /api/v1/auth/login`

**Request** (form-data):
```
username=user@example.com
password=password123
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "buyer",
    "is_active": true
  }
}
```

#### 3. Get Current User
**Endpoint**: `GET /api/v1/auth/me`

**Headers**: `Authorization: Bearer <JWT_TOKEN>`

**Response** (200):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "buyer",
  "full_name": "John Doe",
  "profile_image_url": null,
  "last_login": "2025-01-15T10:00:00Z",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

### Authorization Rules

**All authenticated endpoints require**:
- `Authorization: Bearer <JWT_TOKEN>` header
- JWT expires after 60 minutes
- Token payload contains `sub` (user email)

**Role-Based Access**:
- **Admin**: Full access to all resources
- **Vendor**: Can manage own datasets, agents, and vendor profile
- **Buyer**: Can view public datasets, manage own profile, create chats

---

## Core Entities & Endpoints

### 1. Users

Users are the base authentication entity. Every vendor or buyer has an associated user account.

**Key Fields**:
- `id` (UUID)
- `email` (unique)
- `role` (buyer|vendor|admin)
- `full_name`
- `profile_image_url`
- `is_active` (soft delete flag)

**Note**: User management is handled through auth endpoints. No separate CRUD for users in MVP.

---

### 2. Vendors

Vendors are data providers who list datasets on the marketplace.

#### Create Vendor Profile
**Endpoint**: `POST /api/v1/vendors/`

**Auth**: Vendor role required

**Request Body**:
```json
{
  "name": "Example Data Corp",
  "industry_focus": "Finance",
  "description": "Provider of high-quality financial datasets",
  "contact_email": "data@example.com",
  "contact_phone": "+1-555-0100",
  "website_url": "https://example.com",
  "logo_url": "https://example.com/logo.png",
  "country": "United States",
  "region": "California",
  "city": "San Francisco",
  "address": "123 Market St",
  "organization_type": "Private Company",
  "founded_year": 2020
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "Example Data Corp",
  "industry_focus": "Finance",
  "description": "Provider of high-quality financial datasets",
  "contact_email": "data@example.com",
  "contact_phone": "+1-555-0100",
  "website_url": "https://example.com",
  "logo_url": "https://example.com/logo.png",
  "country": "United States",
  "region": "California",
  "city": "San Francisco",
  "address": "123 Market St",
  "organization_type": "Private Company",
  "founded_year": 2020,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

#### List Vendors
**Endpoint**: `GET /api/v1/vendors/`

**Auth**: Any authenticated user

**Query Parameters**:
- `limit` (int, 1-1000, default: 100)
- `offset` (int, min: 0, default: 0)

**Response** (200): Array of VendorRead objects

#### Get Vendor by ID
**Endpoint**: `GET /api/v1/vendors/{vendor_id}`

**Auth**: Any authenticated user

**Response** (200): VendorRead object

#### Update Vendor
**Endpoint**: `PUT /api/v1/vendors/{vendor_id}`

**Auth**: Admin or vendor owner

**Request Body**: Partial vendor object (only fields to update)

**Response** (200): Updated VendorRead object

#### Delete Vendor
**Endpoint**: `DELETE /api/v1/vendors/{vendor_id}`

**Auth**: Admin or vendor owner

**Response** (200): Success message

---

### 3. Buyers

Buyers are data consumers who browse and purchase datasets.

#### Create Buyer Profile
**Endpoint**: `POST /api/v1/buyers/`

**Auth**: Buyer role required

**Request Body**:
```json
{
  "name": "John Doe",
  "organization": "Research Institute",
  "contact_email": "john@research.org",
  "contact_phone": "+1-555-0200",
  "country": "United States",
  "region": "Massachusetts",
  "city": "Boston",
  "address": "456 Academic Ave",
  "organization_type": "Non-profit",
  "job_title": "Data Scientist",
  "industry": "Research",
  "use_case_focus": "Climate analysis and modeling"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "John Doe",
  "organization": "Research Institute",
  "contact_email": "john@research.org",
  "contact_phone": "+1-555-0200",
  "country": "United States",
  "region": "Massachusetts",
  "city": "Boston",
  "address": "456 Academic Ave",
  "organization_type": "Non-profit",
  "job_title": "Data Scientist",
  "industry": "Research",
  "use_case_focus": "Climate analysis and modeling",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

#### List Buyers
**Endpoint**: `GET /api/v1/buyers/`

**Auth**: Admin, Vendor, or Buyer

**Query Parameters**:
- `limit` (int, 1-1000, default: 100)
- `offset` (int, min: 0, default: 0)

**Response** (200): Array of BuyerRead objects

#### Get Buyer by ID
**Endpoint**: `GET /api/v1/buyers/{buyer_id}`

**Auth**: Admin, Vendor, or buyer themselves

**Response** (200): BuyerRead object

#### Update Buyer
**Endpoint**: `PUT /api/v1/buyers/{buyer_id}`

**Auth**: Admin or buyer themselves

**Request Body**: Partial buyer object

**Response** (200): Updated BuyerRead object

#### Delete Buyer
**Endpoint**: `DELETE /api/v1/buyers/{buyer_id}`

**Auth**: Admin only

**Response** (200): Success message

---

### 4. Datasets

Datasets are the core product in the marketplace.

#### Create Dataset
**Endpoint**: `POST /api/v1/datasets/`

**Auth**: Vendor or Admin

**Request Body**:
```json
{
  "vendor_id": "uuid",
  "title": "Global E-commerce Transactions 2024",
  "description": "Comprehensive dataset of e-commerce transactions across 50 countries",
  "domain": "E-commerce",
  "dataset_type": "Transactional",
  "granularity": "Transaction-level",
  "pricing_model": "Subscription",
  "license": "Commercial Use Allowed",
  "topics": ["e-commerce", "retail", "consumer behavior"],
  "entities": ["transactions", "products", "customers"],
  "temporal_coverage": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "frequency": "Real-time"
  },
  "geographic_coverage": {
    "countries": ["US", "UK", "DE", "FR", "JP"],
    "regions": ["North America", "Europe", "Asia"]
  },
  "visibility": "public",
  "status": "active",
  "columns": [
    {
      "name": "transaction_id",
      "description": "Unique transaction identifier",
      "data_type": "UUID",
      "sample_values": ["a1b2c3d4-...", "e5f6g7h8-..."]
    },
    {
      "name": "amount",
      "description": "Transaction amount in USD",
      "data_type": "DECIMAL",
      "sample_values": [99.99, 149.50, 29.99]
    }
  ]
}
```

**Response** (201): DatasetRead object with auto-generated ID and timestamps

**Note**: 
- `embedding_input` is auto-generated from title + description + topics
- `embedding` is auto-generated using Gemini embeddings (1536 dimensions)
- Columns can be added inline or via separate endpoint

#### List Datasets
**Endpoint**: `GET /api/v1/datasets/`

**Auth**: Any authenticated user

**Query Parameters**:
- `limit` (int, 1-1000, default: 50)
- `offset` (int, min: 0, default: 0)
- `search` (string, optional): Text search in title/description
- `filters` (string, optional): JSON string of dynamic filters

**Filter Examples**:
```json
{
  "domain": "Finance",
  "status": "active",
  "pricing_model": "Subscription"
}
```

**Response** (200): Array of DatasetRead objects

**Visibility Rules**:
- Buyers see only `visibility: public` datasets
- Vendors see their own datasets (all visibility)
- Admins see all datasets

#### Get Dataset by ID
**Endpoint**: `GET /api/v1/datasets/{dataset_id}`

**Auth**: Any authenticated user (respects visibility rules)

**Response** (200): DatasetRead object

#### Update Dataset
**Endpoint**: `PUT /api/v1/datasets/{dataset_id}`

**Auth**: Dataset owner (vendor) or Admin

**Request Body**:
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "status": "inactive",
  "topics": ["updated", "topics"]
}
```

**Response** (200): Updated DatasetRead object

**Note**: Updating title, description, or topics triggers embedding regeneration

#### Delete Dataset
**Endpoint**: `DELETE /api/v1/datasets/{dataset_id}`

**Auth**: Dataset owner or Admin

**Response** (200): Success message

**Note**: Soft delete (sets `status: inactive`) or hard delete

#### Semantic Search (Vector Search)
**Endpoint**: `POST /api/v1/datasets/search/embedding`

**Auth**: Any authenticated user

**Request Body**:
```json
{
  "query": "financial data with quarterly reports",
  "top_k": 5
}
```

**Response** (200):
```json
{
  "results": [
    {
      "id": "uuid",
      "title": "Financial Markets Dataset",
      "description": "...",
      "similarity_score": 0.92,
      ...
    }
  ]
}
```

**How it works**:
1. Query is embedded using Gemini embeddings
2. Cosine similarity search against dataset embeddings
3. Returns top_k most similar datasets

---

### 5. Dataset Columns

Dataset columns define the schema/structure of datasets.

#### Create Column
**Endpoint**: `POST /api/v1/dataset-columns/`

**Auth**: Dataset owner or Admin

**Request Body**:
```json
{
  "dataset_id": "uuid",
  "name": "customer_age",
  "description": "Age of customer in years",
  "data_type": "INTEGER",
  "sample_values": [25, 34, 42, 56]
}
```

**Response** (201): DatasetColumnRead object

#### List Columns for Dataset
**Endpoint**: `GET /api/v1/dataset-columns/dataset/{dataset_id}`

**Auth**: Any authenticated user (respects dataset visibility)

**Response** (200): Array of DatasetColumnRead objects

#### Get Column by ID
**Endpoint**: `GET /api/v1/dataset-columns/{col_id}`

**Auth**: Any authenticated user

**Response** (200): DatasetColumnRead object

#### Update Column
**Endpoint**: `PUT /api/v1/dataset-columns/{col_id}`

**Auth**: Dataset owner or Admin

**Request Body**: Partial column object

**Response** (200): Updated DatasetColumnRead object

#### Delete Column
**Endpoint**: `DELETE /api/v1/dataset-columns/{col_id}`

**Auth**: Dataset owner or Admin

**Response** (204): No content

---

### 6. AI Agents

AI agents are vendor-specific assistants configured to handle buyer inquiries.

#### Create Agent
**Endpoint**: `POST /api/v1/agents/`

**Auth**: Admin or Vendor

**Request Body**:
```json
{
  "vendor_id": "uuid",
  "name": "Finance Data Assistant",
  "description": "AI agent for financial dataset inquiries",
  "model_used": "gemini-embedding-001",
  "config": {
    "max_tokens": 1000,
    "temperature": 0.7,
    "escalation_threshold": 0.5
  },
  "active": true
}
```

**Response** (201): AgentRead object

#### List Agents
**Endpoint**: `GET /api/v1/agents/`

**Auth**: Any authenticated user

**Query Parameters**:
- `vendor_id` (uuid, optional): Filter by vendor
- `active` (boolean, optional): Filter by active status
- `limit` (int, 1-1000, default: 100)
- `offset` (int, min: 0, default: 0)

**Response** (200): Array of AgentRead objects

**Access Rules**:
- Admin: sees all agents
- Vendor: sees only own agents
- Buyer: sees all active agents (marketplace discovery)

#### Get Agent by ID
**Endpoint**: `GET /api/v1/agents/{agent_id}`

**Auth**: Any authenticated user

**Response** (200): AgentRead object

#### Update Agent
**Endpoint**: `PUT /api/v1/agents/{agent_id}`

**Auth**: Admin or agent owner (vendor)

**Request Body**: Partial agent object

**Response** (200): Updated AgentRead object

#### Delete Agent
**Endpoint**: `DELETE /api/v1/agents/{agent_id}`

**Auth**: Admin or agent owner

**Response** (200): Success message

---

### 7. Chats

Chats represent conversation sessions between users, vendors, and AI agents.

#### Chat Types
- **discovery**: Buyer exploring datasets (may involve AI agents)
- **vendor**: Direct buyer-vendor communication

#### Create Chat
**Endpoint**: `POST /api/v1/chats/`

**Auth**: Any authenticated user

**Request Body**:
```json
{
  "user_id": "uuid",
  "vendor_id": "uuid",  // optional, null for discovery chats
  "agent_id": "uuid",   // optional
  "chat_type": "vendor",
  "title": "Inquiry about Financial Dataset",
  "is_active": true
}
```

**Response** (201): ChatRead object

**RBAC**:
- Users can create chats as themselves
- Vendors can create chats under their vendor_id

#### List Chats
**Endpoint**: `GET /api/v1/chats/`

**Auth**: Any authenticated user

**Query Parameters**:
- `user_id` (uuid, optional)
- `vendor_id` (uuid, optional)
- `agent_id` (uuid, optional)
- `chat_type` (string, optional)
- `limit` (int, default: 100)
- `offset` (int, default: 0)
- `include_inactive` (boolean, default: false)

**Response** (200): Array of ChatRead objects

**Access Rules**:
- Admin: sees all chats
- Vendor: sees only chats with their vendor_id
- User/Buyer: sees only chats with their user_id

#### Get Chat by ID
**Endpoint**: `GET /api/v1/chats/{chat_id}`

**Auth**: Chat participant or Admin

**Response** (200): ChatRead object

#### Update Chat
**Endpoint**: `PUT /api/v1/chats/{chat_id}`

**Auth**: Chat owner or Admin

**Request Body**: Partial chat object

**Response** (200): Updated ChatRead object

#### Delete Chat
**Endpoint**: `DELETE /api/v1/chats/{chat_id}`

**Auth**: Chat owner or Admin

**Response** (204): No content

**Note**: Soft delete (sets `is_active: false`)

---

### 8. Chat Messages

Individual messages within chat sessions.

#### Create Message
**Endpoint**: `POST /api/v1/chat-messages/`

**Auth**: Any authenticated user (must be chat participant)

**Request Body**:
```json
{
  "chat_id": "uuid",
  "sender_type": "user",  // user|agent|system
  "message": "Can you provide sample data for this dataset?",
  "message_metadata": {
    "model": "gemini-pro",
    "tokens_used": 150
  }
}
```

**Response** (201): ChatMessageRead object

**Note**: Current user is automatically set as sender

#### List Messages
**Endpoint**: `GET /api/v1/chat-messages/`

**Auth**: Any authenticated user

**Query Parameters**:
- `chat_id` (uuid, optional): Filter by chat
- `sender_type` (string, optional): Filter by sender type
- `limit` (int, 1-500, default: 100)
- `offset` (int, min: 0, default: 0)
- `include_metadata` (boolean, default: true)

**Response** (200): Array of ChatMessageRead objects (sorted by created_at DESC)

#### List Messages by Chat
**Endpoint**: `GET /api/v1/chat-messages/by-chat/{chat_id}`

**Auth**: Chat participant or Admin

**Query Parameters**:
- `limit` (int, 1-200, default: 50)
- `offset` (int, min: 0, default: 0)
- `include_metadata` (boolean, default: true)

**Response** (200): Array of ChatMessageRead objects

#### Get Message by ID
**Endpoint**: `GET /api/v1/chat-messages/{message_id}`

**Auth**: Chat participant

**Response** (200): ChatMessageRead object

#### Update Message
**Endpoint**: `PATCH /api/v1/chat-messages/{message_id}`

**Auth**: Message sender only

**Request Body**:
```json
{
  "message": "Updated message text",
  "message_metadata": { "edited": true }
}
```

**Response** (200): Updated ChatMessageRead object

#### Delete Message
**Endpoint**: `DELETE /api/v1/chat-messages/{message_id}`

**Auth**: Message sender or Admin

**Response** (204): No content

---

## Data Models Summary

### User
```typescript
{
  id: string (uuid)
  email: string
  role: 'buyer' | 'vendor' | 'admin'
  full_name?: string
  profile_image_url?: string
  last_login?: datetime
  is_active: boolean
  created_at: datetime
  updated_at: datetime
}
```

### Vendor
```typescript
{
  id: string (uuid)
  user_id: string (uuid)
  name: string
  industry_focus?: string
  description?: string
  contact_email?: string
  contact_phone?: string
  website_url?: string
  logo_url?: string
  country?: string
  region?: string
  city?: string
  address?: string
  organization_type?: string
  founded_year?: number
  created_at: datetime
  updated_at: datetime
}
```

### Buyer
```typescript
{
  id: string (uuid)
  user_id: string (uuid)
  name: string
  organization?: string
  contact_email?: string
  contact_phone?: string
  country?: string
  region?: string
  city?: string
  address?: string
  organization_type?: string
  job_title?: string
  industry?: string
  use_case_focus?: string
  created_at: datetime
  updated_at: datetime
}
```

### Dataset
```typescript
{
  id: string (uuid)
  vendor_id: string (uuid)
  title: string
  description?: string
  domain?: string
  dataset_type?: string
  granularity?: string
  pricing_model?: string
  license?: string
  topics?: array
  entities?: array
  temporal_coverage?: object
  geographic_coverage?: object
  visibility: 'public' | 'private'
  status: 'active' | 'inactive' | 'draft'
  columns?: array
  embedding_input?: string
  embedding?: number[] (1536 dimensions)
  created_at: datetime
  updated_at: datetime
}
```

### DatasetColumn
```typescript
{
  id: number (bigserial)
  dataset_id: string (uuid)
  name: string
  description?: string
  data_type?: string
  sample_values?: any
  created_at: datetime
}
```

### AIAgent
```typescript
{
  id: string (uuid)
  vendor_id: string (uuid)
  name?: string
  description?: string
  model_used: string (default: 'gemini-embedding-001')
  config?: object
  active: boolean
  created_at: datetime
  updated_at: datetime
}
```

### Chat
```typescript
{
  id: string (uuid)
  user_id: string (uuid)
  vendor_id?: string (uuid)
  agent_id?: string (uuid)
  chat_type: 'discovery' | 'vendor'
  title?: string
  is_active: boolean
  created_at: datetime
  updated_at: datetime
}
```

### ChatMessage
```typescript
{
  id: number (bigserial)
  chat_id: string (uuid)
  sender_type: 'user' | 'agent' | 'system'
  message: string
  message_metadata?: object
  created_at: datetime
}
```

---

## Error Handling

### Standard HTTP Status Codes

- **200 OK**: Successful GET/PUT/PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error

### Error Response Format

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Common Error Scenarios

1. **Expired JWT**: Return 401, redirect to login
2. **Insufficient permissions**: Return 403, show error message
3. **Resource not found**: Return 404, show not found page
4. **Validation errors**: Return 422, highlight form fields

---

## Frontend Implementation Guidelines

### 1. Authentication State Management

```typescript
// Store JWT and user info
interface AuthState {
  token: string | null
  user: UserRead | null
  isAuthenticated: boolean
}

// Include token in all API requests
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

### 2. Role-Based UI Rendering

```typescript
// Show/hide features based on user role
if (user.role === 'vendor') {
  // Show: Dataset upload, Agent management, Vendor dashboard
}
if (user.role === 'buyer') {
  // Show: Dataset discovery, Chat with vendors
}
if (user.role === 'admin') {
  // Show: All admin panels
}
```

### 3. Pagination Pattern

```typescript
// For list endpoints
const fetchDatasets = async (page: number, pageSize: number) => {
  const offset = page * pageSize
  const response = await fetch(
    `/api/v1/datasets/?limit=${pageSize}&offset=${offset}`,
    { headers: authHeaders }
  )
  return response.json()
}
```

### 4. Search and Filtering

```typescript
// Text search
const searchDatasets = async (query: string) => {
  const response = await fetch(
    `/api/v1/datasets/?search=${encodeURIComponent(query)}`,
    { headers: authHeaders }
  )
  return response.json()
}

// Dynamic filters
const filterDatasets = async (filters: object) => {
  const filterString = JSON.stringify(filters)
  const response = await fetch(
    `/api/v1/datasets/?filters=${encodeURIComponent(filterString)}`,
    { headers: authHeaders }
  )
  return response.json()
}

// Semantic search
const semanticSearch = async (query: string) => {
  const response = await fetch('/api/v1/datasets/search/embedding', {
    method: 'POST',
    headers: authHeaders,
    body: JSON.stringify({ query, top_k: 5 })
  })
  return response.json()
}
```

### 5. Real-time Chat Updates

Consider implementing:
- WebSocket connection for live chat messages
- Polling mechanism (e.g., fetch new messages every 5 seconds)
- Optimistic UI updates for sent messages

### 6. Form Validation

Match backend validation rules:
- Email format validation
- Required fields enforcement
- UUID format for IDs
- Enum validation for role, status, visibility, etc.

### 7. Soft Deletes Handling

- Filter out `is_active: false` entities in list views
- Show "inactive" badge for soft-deleted items if needed
- Provide "restore" option for admins

---

## API Base URL

**Development**: `http://localhost:8000/api/v1`
**Production**: `https://your-domain.com/api/v1`

---

## Environment Variables (Backend)

The frontend engineer should know these exist but doesn't need access:

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT signing
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `JWT_EXPIRATION_MINUTES`: Token expiration time (default: 60)
- `OPENAI_API_KEY`: For future AI features
- `GEMINI_API_KEY`: For embedding generation

---

## Key Implementation Notes

### 1. UUID Handling
- All entity IDs are UUIDs (strings)
- Always treat as strings in frontend
- Use string comparison, not numeric

### 2. Timestamps
- All timestamps are ISO 8601 format
- Parse with `new Date()` in JavaScript
- Display with local timezone consideration

### 3. JSONB Fields
- `config`, `topics`, `entities`, `temporal_coverage`, `geographic_coverage`, `sample_values`, `message_metadata`
- These are flexible JSON objects
- Frontend can read/write any structure

### 4. Embeddings
- `embedding` field is a 1536-dimension float array
- Frontend doesn't need to handle this directly
- Used only for semantic search backend logic

### 5. Async Operations
- All database operations are async
- API responses are non-blocking
- Use async/await or promises in frontend

### 6. Pagination Defaults
- Most list endpoints: `limit=100, offset=0`
- Chat messages: `limit=50, offset=0`
- Adjust based on UI/UX needs

### 7. Cascade Deletes
- Deleting a user → deletes vendor/buyer profile
- Deleting a vendor → deletes datasets, agents, chats
- Deleting a dataset → deletes columns
- Deleting a chat → deletes messages

---

## Quick Start Checklist for Frontend Engineer

- [ ] Set up authentication flow (register, login, token storage)
- [ ] Implement JWT token management (storage, refresh, expiration)
- [ ] Create role-based routing/navigation
- [ ] Build user profile pages (vendor/buyer)
- [ ] Implement dataset listing with pagination
- [ ] Add dataset search (text + semantic)
- [ ] Create dataset detail view with columns
- [ ] Build vendor/buyer onboarding forms
- [ ] Implement chat interface
- [ ] Add AI agent management (vendor-only)
- [ ] Handle error states (401, 403, 404, 422)
- [ ] Implement loading states for async operations
- [ ] Add form validation matching backend rules
- [ ] Test RBAC (role-based access control)

---

## Testing Endpoints

Use tools like:
- **Postman/Insomnia**: For manual API testing
- **curl**: For quick command-line tests
- **OpenAPI/Swagger**: Available at `/docs` (FastAPI auto-generated)

Example curl command:
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"

# Get datasets (with token)
curl -X GET "http://localhost:8000/api/v1/datasets/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Support & Documentation

- **OpenAPI Spec**: Available at `/docs` or `/redoc`
- **Backend Repository**: [Link to repo]
- **API Versioning**: All endpoints under `/api/v1/`
- **Contact**: [Backend team contact]

---

**Last Updated**: January 2025  
**API Version**: 1.0.0  
**Backend Framework**: FastAPI (Python)

---

## Advanced Features & Implementation Details

### Vector Similarity Search

The backend uses pgvector for semantic search capabilities. Here's how it works:

**Embedding Generation**:
- Automatically triggered when creating/updating datasets
- Uses Gemini embedding model (1536 dimensions)
- Input: `title + description + topics` (concatenated)
- Stored in `embedding` field

**Search Process**:
1. User query is embedded using the same model
2. Cosine similarity calculated against all dataset embeddings
3. Results ranked by similarity score (0-1, higher = more similar)
4. Returns top_k results with metadata

**Frontend Usage**:
```typescript
// Semantic search for datasets
const semanticSearch = async (userQuery: string, topResults: number = 5) => {
  const response = await fetch('/api/v1/datasets/search/embedding', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: userQuery,
      top_k: topResults
    })
  })
  
  const data = await response.json()
  // data.results contains ranked datasets with similarity scores
  return data.results
}
```

**Use Cases**:
- "Find datasets about climate change"
- "Show me financial data from 2023"
- "Datasets related to consumer behavior in Europe"

---

## Complete API Endpoint Reference

### Authentication Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/v1/auth/register` | No | Register new user |
| POST | `/api/v1/auth/login` | No | Login and get JWT |
| GET | `/api/v1/auth/me` | Yes | Get current user |

### User Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/v1/auth/me` | Yes | Current user profile |

*Note: Full user CRUD not exposed in MVP. Users managed through auth endpoints.*

### Vendor Endpoints

| Method | Endpoint | Auth Required | Roles | Description |
|--------|----------|---------------|-------|-------------|
| POST | `/api/v1/vendors/` | Yes | Vendor | Create vendor profile |
| GET | `/api/v1/vendors/` | Yes | All | List all vendors |
| GET | `/api/v1/vendors/{vendor_id}` | Yes | All | Get vendor by ID |
| PUT | `/api/v1/vendors/{vendor_id}` | Yes | Admin, Owner | Update vendor |
| DELETE | `/api/v1/vendors/{vendor_id}` | Yes | Admin, Owner | Delete vendor |

### Buyer Endpoints

| Method | Endpoint | Auth Required | Roles | Description |
|--------|----------|---------------|-------|-------------|
| POST | `/api/v1/buyers/` | Yes | Buyer | Create buyer profile |
| GET | `/api/v1/buyers/` | Yes | All | List all buyers |
| GET | `/api/v1/buyers/{buyer_id}` | Yes | Admin, Vendor, Owner | Get buyer by ID |
| PUT | `/api/v1/buyers/{buyer_id}` | Yes | Admin, Owner | Update buyer |
| DELETE | `/api/v1/buyers/{buyer_id}` | Yes | Admin | Delete buyer |

### Dataset Endpoints

| Method | Endpoint | Auth Required | Roles | Description |
|--------|----------|---------------|-------|-------------|
| POST | `/api/v1/datasets/` | Yes | Vendor, Admin | Create dataset |
| GET | `/api/v1/datasets/` | Yes | All | List datasets (filtered by visibility) |
| GET | `/api/v1/datasets/{dataset_id}` | Yes | All | Get dataset by ID |
| PUT | `/api/v1/datasets/{dataset_id}` | Yes | Admin, Owner | Update dataset |
| DELETE | `/api/v1/datasets/{dataset_id}` | Yes | Admin, Owner | Delete dataset |
| POST | `/api/v1/datasets/search/embedding` | Yes | All | Semantic search |

### Dataset Column Endpoints

| Method | Endpoint | Auth Required | Roles | Description |
|--------|----------|---------------|-------|-------------|
| POST | `/api/v1/dataset-columns/` | Yes | Admin, Owner | Create column |
| GET | `/api/v1/dataset-columns/dataset/{dataset_id}` | Yes | All | List columns for dataset |
| GET | `/api/v1/dataset-columns/{col_id}` | Yes | All | Get column by ID |
| PUT | `/api/v1/dataset-columns/{col_id}` | Yes | Admin, Owner | Update column |
| DELETE | `/api/v1/dataset-columns/{col_id}` | Yes | Admin, Owner | Delete column |

### AI Agent Endpoints

| Method | Endpoint | Auth Required | Roles | Description |
|--------|----------|---------------|-------|-------------|
| POST | `/api/v1/agents/` | Yes | Admin, Vendor | Create agent |
| GET | `/api/v1/agents/` | Yes | All | List agents (RBAC filtered) |
| GET | `/api/v1/agents/{agent_id}` | Yes | All | Get agent by ID |
| PUT | `/api/v1/agents/{agent_id}` | Yes | Admin, Owner | Update agent |
| DELETE | `/api/v1/agents/{agent_id}` | Yes | Admin, Owner | Delete agent |

### Chat Endpoints

| Method | Endpoint | Auth Required | Roles | Description |
|--------|----------|---------------|-------|-------------|
| POST | `/api/v1/chats/` | Yes | All | Create chat |
| GET | `/api/v1/chats/` | Yes | All | List chats (RBAC filtered) |
| GET | `/api/v1/chats/{chat_id}` | Yes | Participant, Admin | Get chat by ID |
| PUT | `/api/v1/chats/{chat_id}` | Yes | Owner, Admin | Update chat |
| DELETE | `/api/v1/chats/{chat_id}` | Yes | Owner, Admin | Delete chat (soft) |

### Chat Message Endpoints

| Method | Endpoint | Auth Required | Roles | Description |
|--------|----------|---------------|-------|-------------|
| POST | `/api/v1/chat-messages/` | Yes | Participant | Create message |
| GET | `/api/v1/chat-messages/` | Yes | All | List messages (filtered) |
| GET | `/api/v1/chat-messages/{message_id}` | Yes | Participant | Get message by ID |
| GET | `/api/v1/chat-messages/by-chat/{chat_id}` | Yes | Participant, Admin | List messages by chat |
| PATCH | `/api/v1/chat-messages/{message_id}` | Yes | Sender | Update message |
| DELETE | `/api/v1/chat-messages/{message_id}` | Yes | Sender, Admin | Delete message |

---

## Database Relationships & Constraints

### Entity Relationships Diagram

```
users (1) ←→ (1) vendors
users (1) ←→ (1) buyers
vendors (1) → (many) datasets
vendors (1) → (many) ai_agents
datasets (1) → (many) dataset_columns
users (1) → (many) chats
vendors (0-1) → (many) chats
ai_agents (0-1) → (many) chats
chats (1) → (many) chat_messages
```

### Cascade Behaviors

**ON DELETE CASCADE**:
- `users.id` → `vendors.user_id`: Deleting user deletes vendor profile
- `users.id` → `buyers.user_id`: Deleting user deletes buyer profile
- `vendors.id` → `datasets.vendor_id`: Deleting vendor deletes all datasets
- `vendors.id` → `ai_agents.vendor_id`: Deleting vendor deletes all agents
- `datasets.id` → `dataset_columns.dataset_id`: Deleting dataset deletes columns
- `users.id` → `chats.user_id`: Deleting user deletes their chats
- `chats.id` → `chat_messages.chat_id`: Deleting chat deletes all messages

**ON DELETE SET NULL**:
- `vendors.id` → `chats.vendor_id`: Deleting vendor nullifies vendor_id in chats
- `ai_agents.id` → `chats.agent_id`: Deleting agent nullifies agent_id in chats

### Unique Constraints

- `users.email`: Must be unique
- `users.id` ↔ `vendors.user_id`: One-to-one relationship
- `users.id` ↔ `buyers.user_id`: One-to-one relationship

### Check Constraints

- `users.role` ∈ `['buyer', 'vendor', 'admin']`
- `datasets.status` ∈ `['active', 'inactive', 'draft']`
- `datasets.visibility` ∈ `['public', 'private']`
- `chats.chat_type` ∈ `['discovery', 'vendor']`
- `chat_messages.sender_type` ∈ `['user', 'agent', 'system']`

---

## Frontend-Backend Integration Patterns

### 1. Profile Management Flow

**New User Registration → Profile Creation**

```typescript
// Step 1: Register user
const registerUser = async (email: string, password: string, role: string) => {
  const response = await fetch('/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, role, full_name: 'John Doe' })
  })
  return response.json() // Returns UserRead
}

// Step 2: Login to get token
const loginUser = async (email: string, password: string) => {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)
  
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  })
  
  const data = await response.json()
  // Store token and user info
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('user', JSON.stringify(data.user))
  return data
}

// Step 3: Create vendor/buyer profile
const createVendorProfile = async (vendorData: VendorCreate, token: string) => {
  const response = await fetch('/api/v1/vendors/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(vendorData)
  })
  return response.json()
}
```

### 2. Dataset Management Flow

**Vendor uploads dataset with columns**

```typescript
// Step 1: Create dataset
const createDataset = async (datasetData: DatasetCreate, token: string) => {
  // Include columns inline if desired
  const payload = {
    vendor_id: currentVendorId,
    title: 'My Dataset',
    description: 'Dataset description',
    domain: 'Finance',
    visibility: 'public',
    status: 'active',
    columns: [
      {
        name: 'customer_id',
        description: 'Unique customer identifier',
        data_type: 'UUID',
        sample_values: ['a1b2c3...', 'd4e5f6...']
      },
      {
        name: 'revenue',
        description: 'Monthly revenue in USD',
        data_type: 'DECIMAL',
        sample_values: [10000, 25000, 15000]
      }
    ]
  }
  
  const response = await fetch('/api/v1/datasets/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  
  return response.json() // Returns DatasetRead with auto-generated embedding
}

// Alternative: Create dataset first, then add columns separately
const addColumnToDataset = async (datasetId: string, columnData: any, token: string) => {
  const response = await fetch('/api/v1/dataset-columns/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      dataset_id: datasetId,
      ...columnData
    })
  })
  return response.json()
}
```

### 3. Dataset Discovery Flow

**Buyer searches and filters datasets**

```typescript
// Text search
const searchDatasets = async (searchQuery: string, token: string) => {
  const response = await fetch(
    `/api/v1/datasets/?search=${encodeURIComponent(searchQuery)}&limit=20`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  )
  return response.json()
}

// Apply filters
const filterDatasets = async (filters: any, token: string) => {
  const filterString = JSON.stringify(filters)
  const response = await fetch(
    `/api/v1/datasets/?filters=${encodeURIComponent(filterString)}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  )
  return response.json()
}

// Semantic search (AI-powered)
const semanticSearchDatasets = async (query: string, token: string) => {
  const response = await fetch('/api/v1/datasets/search/embedding', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query, top_k: 10 })
  })
  return response.json()
}

// Get dataset details
const getDatasetDetails = async (datasetId: string, token: string) => {
  const response = await fetch(`/api/v1/datasets/${datasetId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  return response.json()
}

// Get dataset columns (schema)
const getDatasetColumns = async (datasetId: string, token: string) => {
  const response = await fetch(`/api/v1/dataset-columns/dataset/${datasetId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  return response.json()
}
```

### 4. Chat Flow

**Buyer initiates chat with vendor**

```typescript
// Create chat session
const createChat = async (vendorId: string, userId: string, token: string) => {
  const response = await fetch('/api/v1/chats/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      vendor_id: vendorId,
      chat_type: 'vendor',
      title: 'Inquiry about dataset',
      is_active: true
    })
  })
  return response.json() // Returns ChatRead with chat_id
}

// Send message
const sendMessage = async (chatId: string, message: string, token: string) => {
  const response = await fetch('/api/v1/chat-messages/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      chat_id: chatId,
      sender_type: 'user',
      message: message
    })
  })
  return response.json()
}

// Fetch chat messages
const getChatMessages = async (chatId: string, token: string, limit: number = 50) => {
  const response = await fetch(
    `/api/v1/chat-messages/by-chat/${chatId}?limit=${limit}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  )
  return response.json() // Returns array of ChatMessageRead (newest first)
}

// Polling for new messages (simple approach)
const pollForNewMessages = async (chatId: string, token: string, lastMessageId: number) => {
  const messages = await getChatMessages(chatId, token, 10)
  return messages.filter((msg: any) => msg.id > lastMessageId)
}
```

### 5. AI Agent Management (Vendor Only)

```typescript
// Create AI agent
const createAgent = async (vendorId: string, agentData: any, token: string) => {
  const response = await fetch('/api/v1/agents/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      vendor_id: vendorId,
      name: 'Dataset Assistant',
      description: 'Helps buyers understand our datasets',
      model_used: 'gemini-embedding-001',
      active: true,
      config: {
        max_response_length: 500,
        temperature: 0.7
      }
    })
  })
  return response.json()
}

// List vendor's agents
const getVendorAgents = async (vendorId: string, token: string) => {
  const response = await fetch(
    `/api/v1/agents/?vendor_id=${vendorId}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  )
  return response.json()
}

// Update agent configuration
const updateAgent = async (agentId: string, updates: any, token: string) => {
  const response = await fetch(`/api/v1/agents/${agentId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  })
  return response.json()
}

// Deactivate agent
const deactivateAgent = async (agentId: string, token: string) => {
  const response = await fetch(`/api/v1/agents/${agentId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ active: false })
  })
  return response.json()
}
```

---

## Common Frontend Components Needed

### 1. Authentication Components
- **LoginForm**: Email + password form
- **RegisterForm**: Email + password + role selection + full name
- **AuthGuard**: HOC/Route guard checking JWT validity
- **RoleGuard**: HOC checking user role for protected routes

### 2. Profile Components
- **VendorProfileForm**: Create/edit vendor profile
- **BuyerProfileForm**: Create/edit buyer profile
- **UserProfileView**: Display user info with edit button

### 3. Dataset Components
- **DatasetList**: Grid/list view with pagination
- **DatasetCard**: Summary card with title, description, vendor
- **DatasetDetail**: Full dataset view with columns, metadata
- **DatasetForm**: Create/edit dataset (vendor only)
- **DatasetSearch**: Search bar with text + semantic options
- **DatasetFilters**: Filter panel (domain, type, pricing, etc.)
- **ColumnSchemaTable**: Display dataset columns in table format

### 4. Chat Components
- **ChatList**: List of chat sessions
- **ChatWindow**: Main chat interface with message history
- **MessageBubble**: Individual message component
- **ChatInput**: Text input with send button
- **ChatHeader**: Display chat participants and title

### 5. AI Agent Components (Vendor Only)
- **AgentList**: List vendor's agents
- **AgentCard**: Agent summary card
- **AgentForm**: Create/edit agent configuration
- **AgentStatusToggle**: Activate/deactivate agent

### 6. Admin Components
- **UserManagementTable**: CRUD for all users
- **VendorManagementTable**: View/edit all vendors
- **DatasetModerationPanel**: Approve/reject datasets
- **SystemAnalytics**: Dashboard with metrics

---

## Security Considerations

### 1. Token Management
```typescript
// Store token securely
// Option 1: localStorage (simple but XSS vulnerable)
localStorage.setItem('token', accessToken)

// Option 2: httpOnly cookie (more secure, requires backend support)
// Backend sets cookie on login response

// Option 3: Memory + refresh token pattern (most secure)
let tokenInMemory: string | null = null

// Check token expiration
const isTokenExpired = (token: string): boolean => {
  const payload = JSON.parse(atob(token.split('.')[1]))
  return payload.exp * 1000 < Date.now()
}

// Refresh token before expiration
const refreshTokenIfNeeded = async () => {
  if (tokenInMemory && isTokenExpired(tokenInMemory)) {
    // Redirect to login or call refresh endpoint
  }
}
```

### 2. Input Sanitization
- Always sanitize user input before sending to backend
- Use libraries like DOMPurify for rich text
- Validate email format, UUID format, etc.

### 3. RBAC Enforcement
```typescript
// Client-side role checking (for UI only, not security)
const canUserAccessResource = (user: UserRead, resource: string): boolean => {
  const permissions = {
    admin: ['*'], // All permissions
    vendor: ['datasets:create', 'datasets:update', 'agents:manage'],
    buyer: ['datasets:view', 'chats:create']
  }
  return permissions[user.role].includes(resource) || permissions[user.role].includes('*')
}

// Hide/show UI elements
{user.role === 'vendor' && <CreateDatasetButton />}
{user.role === 'admin' && <AdminPanel />}
```

**Important**: Client-side checks are for UX only. Backend always enforces actual permissions.

### 4. API Error Handling
```typescript
const handleApiError = async (response: Response) => {
  if (response.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('token')
    window.location.href = '/login'
  } else if (response.status === 403) {
    // Insufficient permissions
    alert('You do not have permission to perform this action')
  } else if (response.status === 404) {
    // Resource not found
    alert('Resource not found')
  } else if (response.status === 422) {
    // Validation error
    const error = await response.json()
    return error.detail // Display validation errors
  }
}
```

---

## Performance Optimization Tips

### 1. Pagination
- Always use pagination for lists
- Default page size: 50-100 items
- Implement infinite scroll or "Load More" button

### 2. Caching
- Cache frequently accessed data (vendor profiles, dataset metadata)
- Use SWR or React Query for automatic caching
- Invalidate cache on mutations

### 3. Debouncing Search
```typescript
import { debounce } from 'lodash'

const debouncedSearch = debounce(async (query: string) => {
  const results = await searchDatasets(query, token)
  setSearchResults(results)
}, 300) // Wait 300ms after user stops typing
```

### 4. Lazy Loading
- Load chat messages on demand
- Implement virtual scrolling for large lists
- Use code splitting for heavy components

### 5. Optimistic UI Updates
```typescript
// Add message immediately to UI, then confirm with backend
const sendMessageOptimistic = async (message: string) => {
  const tempMessage = {
    id: Date.now(), // Temporary ID
    message,
    sender_type: 'user',
    created_at: new Date().toISOString()
  }
  
  // Add to UI immediately
  setMessages(prev => [tempMessage, ...prev])
  
  try {
    // Send to backend
    const confirmed = await sendMessage(chatId, message, token)
    // Replace temp message with confirmed one
    setMessages(prev => prev.map(m => m.id === tempMessage.id ? confirmed : m))
  } catch (error) {
    // Remove temp message on error
    setMessages(prev => prev.filter(m => m.id !== tempMessage.id))
    alert('Failed to send message')
  }
}
```

---

## Testing Strategy

### 1. Unit Tests
- Test individual components in isolation
- Mock API calls
- Test form validation logic

### 2. Integration Tests
- Test authentication flow end-to-end
- Test dataset creation → listing → detail flow
- Test chat message sending/receiving

### 3. E2E Tests
- Use Playwright or Cypress
- Test critical user journeys:
  - User registration → profile creation → dataset upload
  - Dataset search → view details → initiate chat
  - Admin user management

### 4. API Testing
- Use Postman/Insomnia collections
- Test all CRUD operations
- Verify RBAC enforcement
- Test error scenarios (401, 403, 404, 422)

---

## Deployment Considerations

### Environment Variables (Frontend)
```bash
VITE_API_BASE_URL=https://api.puddle.com/api/v1
VITE_WS_URL=wss://api.puddle.com/ws  # For future WebSocket support
```

### CORS Configuration
Backend must allow frontend origin:
```python
# Already configured in backend
allow_origins = ["http://localhost:3000", "https://puddle.com"]
```

### Build Optimization
- Minify and compress JavaScript/CSS
- Use CDN for static assets
- Implement lazy loading for routes
- Enable gzip/brotli compression

---

## Future Enhancements (Post-MVP)

### 1. Real-time Features
- WebSocket integration for live chat updates
- Real-time dataset upload progress
- Live notifications for new messages

### 2. Advanced Search
- Faceted search with multiple filters
- Saved search queries
- Search history

### 3. Dataset Previews
- Sample data download
- Data quality metrics
- Schema visualization

### 4. Payment Integration
- Dataset purchase flow
- Subscription management
- Invoice generation

### 5. Analytics Dashboard
- Dataset view analytics
- User engagement metrics
- Revenue tracking (vendor)

### 6. Vendor API Integration (MCP)
- Connect vendor APIs via Model Context Protocol
- Pay-per-use insights
- Cross-domain analysis

---

## Troubleshooting Common Issues

### Issue 1: JWT Token Expired
**Symptom**: 401 errors after some time
**Solution**: Implement token refresh logic or redirect to login

### Issue 2: CORS Errors
**Symptom**: Network errors in browser console
**Solution**: Verify backend CORS configuration includes your frontend URL

### Issue 3: Pagination Not Working
**Symptom**: Always seeing same results
**Solution**: Check that `offset` is being calculated correctly: `page * pageSize`

### Issue 4: Embeddings Not Generated
**Symptom**: Semantic search returns no results
**Solution**: Ensure `GEMINI_API_KEY` is configured in backend environment

### Issue 5: Soft Deleted Items Showing
**Symptom**: Inactive vendors/buyers/chats appearing in lists
**Solution**: Add `include_inactive=false` parameter or filter on frontend

---

## Contact & Support

**Backend Team Lead**: [Name]
**Frontend Team Lead**: [Name]
**Project Manager**: [Name]

**Slack Channel**: #puddle-dev
**Documentation**: [Wiki Link]
**Issue Tracker**: [Jira/GitHub Issues Link]

**Office Hours**: Tuesdays 2-3 PM EST

---

## Glossary

- **Vendor**: Data provider who lists datasets
- **Buyer**: Data consumer who searches and purchases datasets
- **Dataset**: Collection of structured data with metadata
- **Agent**: AI assistant configured by vendors
- **Discovery Chat**: Exploratory conversation with AI agents
- **Vendor Chat**: Direct communication between buyer and vendor
- **Embedding**: Vector representation of dataset for semantic search
- **RBAC**: Role-Based Access Control
- **Soft Delete**: Marking record as inactive instead of removing from database
- **UUID**: Universally Unique Identifier (128-bit)
- **JWT**: JSON Web Token (for authentication)
- **JSONB**: PostgreSQL's JSON binary storage format
- **Vector Search**: Similarity search using embeddings
- **Cosine Similarity**: Measure of similarity between two vectors

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**API Version**: 1.0.0  
**Backend Framework**: FastAPI (Python 3.10+)  
**Database**: PostgreSQL 14+ with pgvector extension