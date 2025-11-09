# Summary for app.schemas.* files

## Overview

These schema files define **Pydantic models** used for request validation and response serialization in the FastAPI backend. They determine what data shapes are expected from the frontend and what responses the frontend will receive. Each file corresponds to one domain entity (e.g., user, vendor, buyer, dataset, etc.) from the models.

---

## app.schemas.user.py

### Purpose

Handles validation and serialization for user-related API endpoints.

### Key Schemas

* **UserCreate:** Used when registering new users.

  * Fields: `email`, `password_hash`, `role` ('buyer', 'vendor', or 'admin'), optional profile details.
* **UserRead:** Response schema returned to frontend.

  * Includes metadata like `id`, `created_at`, `updated_at`, `last_login`.

### Frontend Relevance

Used during signup, login, and displaying user profile information. `role` determines dashboard type and permissions.

---

## app.schemas.vendor.py

### Purpose

Defines how vendor data is created and displayed.

### Key Schemas

* **VendorCreate:** Used for creating a new vendor profile after signup.
* **VendorRead:** Returns vendor info along with timestamps.

### Frontend Relevance

Displayed in vendor dashboards, profile forms, and dataset creation UIs. The frontend should handle optional fields gracefully.

---

## app.schemas.buyer.py

### Purpose

Handles buyer profile information.

### Key Schemas

* **BuyerCreate:** Defines structure for creating buyer profiles.
* **BuyerRead:** Response schema for displaying buyer details.

### Frontend Relevance

Displayed in buyer dashboards and data request forms. Similar to `VendorRead` but oriented toward dataset consumption.

---

## app.schemas.dataset.py

### Purpose

Defines dataset structure for vendor uploads and buyer discovery.

### Key Schemas

* **DatasetCreate:** Used for dataset creation by vendors.

  * Includes `vendor_id`, `title`, `description`, and metadata such as `topics`, `entities`, `domain`, etc.
  * Optional `columns` field allows including dataset column metadata inline.
* **DatasetRead:** Response schema sent to frontend.

  * Adds `id`, `created_at`, and `updated_at`.

### Frontend Relevance

Used for vendor dataset upload forms, dataset detail pages, and buyer-facing discovery or marketplace UIs.

---

## app.schemas.dataset_column.py

### Purpose

Defines schema for dataset column metadata.

### Key Schemas

* **DatasetColumnCreate:** Used to create columns under a dataset.
* **DatasetColumnUpdate:** Used for editing existing column metadata.
* **DatasetColumnRead:** Used in dataset detail pages or previews.

### Frontend Relevance

The frontend can render these columns as part of a schema preview when browsing or viewing dataset details.

---

## app.schemas.agent.py

### Purpose

Defines AI Agent structure for vendors.

### Key Schemas

* **AgentCreate:** Used when vendors create or configure AI agents.
* **AgentRead:** Returns full agent details, including `id`, `created_at`, and `updated_at`.

### Frontend Relevance

Supports AI management UI for vendors (e.g., listing and editing agents, monitoring status, and linking agents to chats).

---

## app.schemas.chat.py

### Purpose

Defines structure for chat sessions between users, vendors, and AI agents.

### Key Schemas

* **ChatCreate:** Used when a new chat session is initiated.
* **ChatRead:** Sent back when fetching chat histories or active sessions.

### Frontend Relevance

Drives chat interfaces, including both buyer-vendor messaging and AI chat components.

---

## app.schemas.chat_message.py

### Purpose

Defines structure for messages exchanged in chat sessions.

### Key Schemas

* **ChatMessageCreate:** Used for sending new messages.
* **ChatMessageRead:** Response schema for displaying chat histories.

### Frontend Relevance

Used by chat UIs for rendering message lists and sending new messages. `sender_type` helps distinguish between user, vendor, or AI responses.

---

## General Frontend Guidelines

* All schemas use **UUIDs** for entity IDs; treat them as strings in frontend code.
* All response schemas have `model_config = { 'from_attributes': True }`, enabling ORM-to-JSON conversion automatically.
* Optional fields mean the frontend can omit them during create/update calls.
* Consistent naming (`Create`, `Read`, `Update`) maps 1:1 with HTTP methods:

  * `Create` → POST
  * `Read` → GET
  * `Update` → PUT/PATCH
