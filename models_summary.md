# Summary for app.models.models.py

## Overview

Defines all SQLAlchemy ORM models representing core entities in the system. Each table has an associated Python class with relationships. Frontend engineers will interact with these entities indirectly through REST API routes. The relationships define data dependencies that inform how frontend components (like dashboards or forms) should structure data.

---

## Core Entities

### User

* **Fields:** id, email, password_hash, role, full_name, profile_image_url, last_login, is_active, created_at, updated_at.
* **Relationships:**

  * One-to-one with `Vendor` (vendor_profile)
  * One-to-one with `Buyer` (buyer_profile)
  * One-to-many with `Chat` (user’s chat history)
* **Frontend relevance:** Used for authentication, profile display, and access control (role-based).

### Vendor

* **Fields:** id, user_id, name, industry_focus, description, contact_email, contact_phone, website_url, logo_url, country, region, city, address, organization_type, founded_year.
* **Relationships:**

  * Belongs to `User`
  * Has many `Datasets`, `AIAgents`, and `Chats`
* **Frontend relevance:** Represents data provider profile; vendor dashboard will display/manage datasets, AI agents, and chat inquiries.

### Buyer

* **Fields:** id, user_id, name, organization, contact_email, contact_phone, country, region, city, address, organization_type, job_title, industry, use_case_focus.
* **Relationships:**

  * Belongs to `User`
* **Frontend relevance:** Represents data consumer profile; buyer dashboard will show accessible datasets and AI agent chats.

### AIAgent

* **Fields:** id, vendor_id, name, description, model_used, config, active, created_at, updated_at.
* **Relationships:**

  * Belongs to `Vendor`
  * Has many `Chats`
* **Frontend relevance:** Used in AI management dashboard. Each vendor can configure and monitor multiple AI agents.

### Dataset

* **Fields:** id, vendor_id, title, status, visibility, description, domain, dataset_type, granularity, pricing_model, license, topics, entities, temporal_coverage, geographic_coverage, embedding_input, embedding.
* **Relationships:**

  * Belongs to `Vendor`
  * Has many `DatasetColumn`
* **Frontend relevance:** Used for dataset listing, search, and detail views. Important for vendor upload and buyer discovery.

### DatasetColumn

* **Fields:** id, dataset_id, name, description, data_type, sample_values, created_at.
* **Relationships:**

  * Belongs to `Dataset`
* **Frontend relevance:** Defines dataset schema details. Will be displayed in dataset details view or data preview sections.

### Chat

* **Fields:** id, user_id, vendor_id, agent_id, chat_type, title, is_active, created_at, updated_at.
* **Relationships:**

  * Belongs to `User`, `Vendor`, `AIAgent`
  * Has many `ChatMessage`
* **Frontend relevance:** Represents a conversation session. Used in buyer-vendor communication or AI chat UIs.

### ChatMessage

* **Fields:** id, chat_id, sender_type, message, message_metadata, created_at.
* **Relationships:**

  * Belongs to `Chat`
* **Frontend relevance:** Represents individual messages in chat threads.

---

## General Frontend Considerations

* Every entity includes `created_at` and `updated_at` timestamps (useful for activity logs or sorting).
* UUIDs are used as primary keys; frontend should treat them as strings.
* Relationships inform UI nesting: vendors own datasets, datasets contain columns, chats contain messages.
* Role-based distinctions (User.role) control which components are visible (vendor dashboard vs. buyer dashboard).
