# Summary for app.crud.* files

## Overview

The CRUD files define all database interaction logic for the backend. Each file corresponds to one entity (User, Vendor, Buyer, Dataset, etc.) and includes functions to **create**, **read**, **update**, and **delete** records. These functions directly support the REST API routes that the frontend will call.

---

## app.crud.users.py

### Purpose

Handles all operations for user management.

### Key Operations

* **create_user(db, user_in):** Creates a new user record.
* **get_user(db, user_id):** Fetches a user by ID (only active users).
* **get_user_by_email(db, email):** Fetches a user by email (used during login).
* **list_users(limit, offset, include_inactive):** Returns a paginated list of users.
* **update_user(db, user_id, update_data):** Updates editable user fields (e.g., name, role).
* **delete_user(db, user_id):** Soft deletes user (sets `is_active=False`).

### Frontend Relevance

Used for signup, login, user listing in admin dashboards, and profile management. Only active users are exposed to frontend.

---

## app.crud.vendors.py

### Purpose

Handles vendor creation, updates, and soft deletion.

### Key Operations

* **create_vendor(db, vendor_in):** Registers a vendor.
* **get_vendor(db, vendor_id):** Fetches vendor by ID (only active vendors).
* **list_vendors(limit, offset, include_inactive):** Paginated list of vendors.
* **update_vendor(db, vendor_id, update_data):** Updates vendor profile (ignores `id`, `created_at`).
* **delete_vendor(db, vendor_id):** Soft delete via `is_active=False`, fallback to hard delete.

### Frontend Relevance

Used in vendor dashboards for profile updates, marketplace listings, and admin moderation UIs.

---

## app.crud.buyers.py

### Purpose

Manages buyer data and association with users.

### Key Operations

* **create_buyer(db, buyer_in, user_id):** Creates buyer profile (linked to user if provided).
* **get_buyer(db, buyer_id):** Fetches buyer by ID.
* **list_buyers(limit, offset):** Paginated list of buyers.
* **update_buyer(db, buyer_id, update_data):** Updates buyer info.
* **delete_buyer(db, buyer_id):** Hard deletes buyer.

### Frontend Relevance

Supports buyer profile pages, buyer list views, and related account management flows.

---

## app.crud.datasets.py

### Purpose

Handles dataset creation, embedding, updates, and deletion.

### Key Operations

* **create_dataset(db, dataset_in):** Creates dataset, builds embedding if missing.
* **get_dataset(db, dataset_id):** Retrieves dataset details.
* **list_datasets(limit, offset):** Lists datasets with pagination.
* **update_dataset(db, dataset_id, update_data):** Updates dataset; rebuilds embeddings if key fields changed.
* **delete_dataset(db, dataset_id):** Marks dataset inactive or deletes it.

### Frontend Relevance

Used for dataset upload forms, detail pages, editing UIs, and discovery marketplaces. The embedding system is abstracted from frontend.

---

## app.crud.dataset_columns.py

### Purpose

Handles creation and management of individual dataset columns.

### Key Operations

* **create_dataset_column(db, col_in):** Adds a column to a dataset.
* **list_dataset_columns(db, dataset_id):** Returns all columns for a dataset.
* **update_dataset_column(db, col_id, update_data):** Updates column metadata.
* **delete_dataset_column(db, col_id):** Deletes column entry.

### Frontend Relevance

Used when showing dataset schema previews or managing dataset metadata in the UI.

---

## app.crud.agents.py

### Purpose

CRUD logic for AI agents linked to vendors.

### Key Operations

* **create_agent(db, agent_in):** Registers a new AI agent.
* **get_agent(db, agent_id):** Fetches agent by ID.
* **list_agents(vendor_id, active, limit, offset):** Lists agents with filters.
* **update_agent(db, agent_id, update_data):** Updates agent configuration.
* **delete_agent(db, agent_id):** Deletes agent.

### Frontend Relevance

Enables agent management interfaces in vendor dashboards (create, edit, activate/deactivate agents).

---

## app.crud.chats.py

### Purpose

Manages chat sessions between users, vendors, and AI agents.

### Key Operations

* **create_chat(db, chat_in):** Starts a new chat.
* **list_chats(db, user_id, vendor_id, agent_id, chat_type):** Fetches relevant chat threads.
* **update_chat(db, chat_id, update_data):** Updates chat metadata.
* **delete_chat(db, chat_id):** Soft delete (sets `is_active=False`).

### Frontend Relevance

Used to fetch chat lists for dashboards, open existing sessions, and manage chat lifecycle.

---

## app.crud.chat_messages.py

### Purpose

Handles message-level operations within a chat.

### Key Operations

* **create_chat_message(db, message_in):** Sends or stores a chat message.
* **list_chat_messages(chat_id, sender_type, limit, offset):** Returns messages in a chat.
* **update_chat_message(db, message_id, update_data):** Updates message text or metadata.
* **delete_chat_message(db, message_id):** Deletes message.

### Frontend Relevance

Directly supports chat UIs for rendering messages, sending new ones, and displaying sender roles.

---

## General Frontend Guidelines

* Each CRUD function corresponds to an API route (`POST`, `GET`, `PUT/PATCH`, `DELETE`).
* Pagination (`limit`, `offset`) parameters should be supported in list views.
* UUIDs are used for IDs; treat them as strings.
* Soft deletes (using `is_active=False`) should be reflected in the frontend by hiding or marking records as inactive.
* Fields excluded from updates (`id`, `created_at`, `email`, etc.) should not be editable in frontend forms.
