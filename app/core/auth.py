from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.db import get_session
from app.crud.users import get_user_by_email
from app.schemas.user import UserRead
from app.models.models import User
import os

# =========================================================
# CONFIGURATION
# =========================================================

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# =========================================================
# SECURITY SETUP
# =========================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# =========================================================
# PASSWORD UTILITIES
# =========================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if provided password matches stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password safely with bcrypt.
    Bcrypt only supports up to 72 bytes — truncate and ensure it's a UTF-8 string.
    """
    if not isinstance(password, str):
        password = str(password)
    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)

# =========================================================
# JWT TOKEN CREATION
# =========================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =========================================================
# USER AUTHENTICATION
# =========================================================
async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[UserRead]:
    """
    Verify a user's email and password.
    Returns UserRead if successful, None otherwise.
    """
    query = text("SELECT * FROM users WHERE email = :email AND is_active = TRUE")
    result = await db.execute(query, {"email": email})
    row = result.mappings().first()
    if not row:
        return None

    user = User(**row)
    if not verify_password(password, user.password_hash):
        return None

    return UserRead.model_validate(user)

# =========================================================
# CURRENT USER FROM TOKEN
# =========================================================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> UserRead:
    """Extract user from JWT and verify validity."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = text("SELECT * FROM users WHERE email = :email AND is_active = TRUE")
    result = await db.execute(query, {"email": email})
    row = result.mappings().first()
    if not row:
        raise credentials_exception

    user = User(**row)
    return UserRead.model_validate(user)

# =========================================================
# TOKEN RESPONSE CREATION
# =========================================================
def create_token_response(user: UserRead) -> dict:
    """Generate JWT for a valid user and return response payload."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.model_dump(),
    }

# =========================================================
# USER REGISTRATION (Helper)
# =========================================================
async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    role: str,
    full_name: Optional[str] = None
) -> UserRead:
    """Create a new user with hashed password."""
    query = text("SELECT 1 FROM users WHERE email = :email")
    result = await db.execute(query, {"email": email})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        full_name=full_name,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)
