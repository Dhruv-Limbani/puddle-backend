# Summary for app.api.v1.routes.* (Unified)

This document summarizes all route files in `app.api.v1.routes`, covering authentication, users, vendors, buyers, datasets, dataset columns, agents, chats, and chat messages. Each section includes endpoints, parameters, response models, role-based access, and frontend implications.

---

## auth.py

**Prefix:** `/auth`

### Endpoints

1. `POST /auth/register` – Register a new user.
2. `POST /auth/login` – Authenticate and return JWT.
3. `GET /auth/me` – Get current user details.

**Frontend relevance:** Used in signup/login forms, storing JWT, maintaining session context.

---

## users.py

**Prefix:** `/users`
**Roles:** `admin`, `vendor`, `buyer`

### Endpoints

* `GET /users/me` – Display current user profile.
* `GET /users/` – Admin dashboard user list (with optional role filter).
* `GET /users/{user_id}` – View user profile.
* `PUT /users/{user_id}` – Edit profile.
* `DELETE /users/{user_id}` – Admin soft-delete user.

**Frontend relevance:** Profile pages, admin user management.

---

## vendors.py

**Prefix:** `/vendors`

### Endpoints

* `POST /vendors/` – Create vendor profile (onboarding).
* `GET /vendors/` – List vendors (paginated).
* `GET /vendors/{vendor_id}` – View vendor profile.
* `PUT /vendors/{vendor_id}` – Edit vendor profile.
* `DELETE /vendors/{vendor_id}` – Delete vendor.

**Frontend relevance:** Vendor onboarding, profile pages, marketplace listings.

---

## buyers.py

**Prefix:** `/buyers`

### Endpoints

* `POST /buyers/` – Create buyer profile.
* `GET /buyers/` – List buyers.
* `GET /buyers/{buyer_id}` – View buyer profile.
* `PUT /buyers/{buyer_id}` – Edit buyer profile.
* `DELETE /buyers/{buyer_id}` – Admin deletes buyer.

**Frontend relevance:** Buyer onboarding, profile pages, discovery listings.

---

## datasets.py

**Prefix:** `/datasets`
**Roles:** Vendor (create/update/delete), Buyer (view public), Admin (full access)

### Endpoints

1. `POST /datasets/` – Create dataset (Vendor/Admin only).
2. `GET /datasets/` – List datasets with filters/search.
3. `GET /datasets/{dataset_id}` – Get dataset details.
4. `PUT /datasets/{dataset_id}` – Update dataset (owner only).
5. `DELETE /datasets/{dataset_id}` – Delete dataset (owner only).
6. `POST /datasets/search/embedding` – Semantic search by embeddings.

**Frontend relevance:** Dataset marketplace, detail pages, semantic search.

---

## dataset_columns.py

**Prefix:** `/dataset-columns`
**Roles:** Vendor (owner), Admin (full), Buyer (read-only public)

### Endpoints

1. `POST /dataset-columns/` – Create column (owner/Admin).
2. `GET /dataset-columns/dataset/{dataset_id}` – List columns.
3. `GET /dataset-columns/{col_id}` – Get column details.
4. `PUT /dataset-columns/{col_id}` – Update column.
5. `DELETE /dataset-columns/{col_id}` – Delete column.

**Frontend relevance:** Column management UI for vendors, read-only display for buyers.

---

## agents.py

**Prefix:** `/agents`
**Roles:** Admin, Vendor (own agents), Buyer (view)

### Endpoints

1. `POST /agents/` – Create AI agent (Admin/Vendor).
2. `GET /agents/` – List agents (RBAC enforced).
3. `GET /agents/{agent_id}` – Get specific agent.
4. `PUT /agents/{agent_id}` – Update agent (Admin/own Vendor).
5. `DELETE /agents/{agent_id}` – Delete agent (Admin/own Vendor).

**Frontend relevance:** Agent management dashboard, marketplace discovery.

---

## chats.py

**Prefix:** `/chats`
**Roles:** Admin, Vendor, User/Buyer

### Helper

* `verify_chat_access` – Enforces RBAC for chat retrieval, updates, and deletion.

### Endpoints

1. `POST /chats/` – Create chat (self only for users/vendors).
2. `GET /chats/{chat_id}` – Retrieve chat.
3. `GET /chats/` – List chats with filters.
4. `PUT /chats/{chat_id}` – Update chat (owner/Admin).
5. `DELETE /chats/{chat_id}` – Delete chat (owner/Admin).

**Frontend relevance:** Chat list, chat detail, chat creation UI.

---

## chat_messages.py

**Prefix:** `/chat-messages`
**Roles:** Participant (sender/receiver), Admin

### Endpoints

1. `POST /chat-messages/` – Create message (current user is sender).
2. `GET /chat-messages/{message_id}` – Retrieve message by ID.
3. `GET /chat-messages/` – List messages (filters: chat_id, sender_type).
4. `GET /chat-messages/by-chat/{chat_id}` – List messages for specific chat.
5. `PATCH /chat-messages/{message_id}` – Update message (only sender).
6. `DELETE /chat-messages/{message_id}` – Delete message (sender/Admin).

**Frontend relevance:** Chat message feed, sending/receiving, edit/delete UI.

---

### General Frontend Notes

* All endpoints (except `/auth/register` and `/auth/login`) require JWT in Authorization header.
* Standard pagination (`limit`, `offset`) across listings.
* Role-based access controls dictate which UI actions/buttons are visible.
* UUIDs used consistently for IDs.
* Update endpoints accept JSON with only fields to be updated.
