from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.core.db import get_session
from app.core import auth as auth_core
from app.schemas.user import UserRead
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])

# =========================================================
# REGISTER NEW USER
# =========================================================
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    email: str,
    password: str,
    role: str,
    full_name: str | None = None,
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new user with hashed password.
    - email: user email (must be unique)
    - password: plaintext password
    - role: user role (buyer/vendor/admin)
    - full_name: optional full name
    """
    new_user = await auth_core.register_user(
        db=db, email=email, password=password, role=role, full_name=full_name
    )
    return new_user


# =========================================================
# LOGIN USER
# =========================================================
@router.post("/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    Authenticate user and return JWT token.
    Expects form data with:
    - username (email)
    - password
    """
    user = await auth_core.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_core.create_token_response(user)


# =========================================================
# GET CURRENT LOGGED-IN USER
# =========================================================
@router.get("/me", response_model=UserRead)
async def get_me(current_user: UserRead = Depends(auth_core.get_current_user)):
    """
    Returns the currently authenticated user's info.
    """
    return current_user
