**Backend Summary: Core Layer (app.core)**

---

### 1. `config.py`

**Purpose:** Defines application configuration and environment variable management.

**Frontend-Relevant Details:**

* The backend connects to a PostgreSQL database (`DATABASE_URL`).
* Environment variables such as `OPENAI_API_KEY` and `GEMINI_API_KEY` may indicate AI features in the app.
* Config values (like database URL or API keys) are loaded from `.env` and not hardcoded.

**Frontend Implication:** No direct interaction needed, but ensures all API routes and authentication rely on a properly configured backend environment.

---

### 2. `db.py`

**Purpose:** Defines the asynchronous database connection using SQLAlchemy.

**Frontend-Relevant Details:**

* All database operations are asynchronous.
* API responses (CRUD routes) are powered by this async DB session.
* Each request to the backend will automatically open and close a database session.

**Frontend Implication:**

* API routes will respond asynchronously, suitable for concurrent requests from frontend.

---

### 3. `auth.py`

**Purpose:** Handles authentication, password hashing, and JWT token management.

**Frontend-Relevant Details:**

#### a. **Authentication Flow:**

* Uses OAuth2 with `Bearer` token via `/api/v1/auth/login` endpoint.
* Upon successful login, the backend returns:

  ```json
  {
    "access_token": "<JWT_TOKEN>",
    "token_type": "bearer",
    "user": {
      "id": "string",
      "email": "user@example.com",
      "role": "admin|vendor|buyer",
      "is_active": true,
      ...
    }
  }
  ```
* This token must be stored on the frontend (e.g., in memory, local storage, or cookies) and included in every protected request as an Authorization header:

  ```http
  Authorization: Bearer <JWT_TOKEN>
  ```

#### b. **Registration Flow:**

* User registration is supported (via helper `register_user`). Expected input:

  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "role": "buyer|vendor|admin",
    "full_name": "John Doe"
  }
  ```
* Returns a user object after successful registration.

#### c. **Password and Token Security:**

* Passwords are hashed using bcrypt.
* JWT tokens have an expiration time (default: 60 minutes).
* Token payload contains `sub` = user email.

#### d. **Role-Based Access (RBAC):**

* User object contains a `role` field used by route-level access control.
* Frontend should store this role and use it to conditionally show/hide features (e.g., admin dashboards, vendor tools).

**Frontend Implication:**

* Frontend must:

  * Implement login and signup forms.
  * Persist and send JWT tokens for authenticated requests.
  * Handle 401 (Unauthorized) and 403 (Forbidden) responses by redirecting to login or showing permission errors.
  * Read user role from token response to control access to protected sections.

---

**Summary for Frontend Engineer:**

* Base API URLs likely start with `/api/v1/`.
* Authentication is JWT-based and required for most operations.
* Login endpoint returns both token and user object.
* Role-based permissions will affect UI components.
* API requests must always include the Authorization header.
* The backend is fully asynchronous, so all responses are non-blocking and fast.
