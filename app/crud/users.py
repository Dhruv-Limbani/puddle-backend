from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User
from app.schemas.user import UserCreate, UserRead


# =============================
# CREATE USER
# =============================
async def create_user(db: AsyncSession, user_in: Union[UserCreate, dict]) -> UserRead:
    """
    Create a new user.
    """
    if isinstance(user_in, dict):
        user_in = UserCreate(**user_in)

    user = User(**user_in.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


# =============================
# GET USER BY ID
# =============================
async def get_user(db: AsyncSession, user_id: str) -> Optional[UserRead]:
    """
    Retrieve a single user by ID.
    Only active users are returned.
    """
    user = await db.get(User, user_id)
    if user and user.is_active:
        return UserRead.model_validate(user)
    return None


# =============================
# GET USER BY EMAIL
# =============================
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserRead]:
    """
    Retrieve a single user by email.
    Only active users are returned.
    """
    result = await db.execute(select(User).where(User.email == email, User.is_active == True))
    user = result.scalars().first()
    if user:
        return UserRead.model_validate(user)
    return None


# =============================
# LIST USERS
# =============================
async def list_users(
    db: AsyncSession, *, limit: int = 100, offset: int = 0, include_inactive: bool = False
) -> List[UserRead]:
    """
    List users with pagination.
    Set include_inactive=True to also return inactive users.
    """
    query = select(User)
    if not include_inactive:
        query = query.where(User.is_active == True)
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    users = result.scalars().all()
    return [UserRead.model_validate(u) for u in users]


# =============================
# UPDATE USER
# =============================
async def update_user(db: AsyncSession, user_id: str, update_data: dict) -> Optional[UserRead]:
    """
    Update a user by ID. Ignores immutable fields.
    """
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        return None

    for key, value in update_data.items():
        if key in ("id", "created_at", "email"):
            continue
        if hasattr(user, key):
            setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


# =============================
# SOFT DELETE USER
# =============================
async def delete_user(db: AsyncSession, user_id: str) -> bool:
    """
    Soft-delete a user by marking is_active=False.
    Returns True if user existed and was deactivated, False if not found.
    """
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        return False

    user.is_active = False
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True
