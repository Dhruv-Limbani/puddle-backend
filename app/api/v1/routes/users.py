from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.auth import get_current_user
from app.crud import users as crud_users
from app.schemas.user import UserRead
from app.models.models import User

router = APIRouter(prefix="/users", tags=["Users"])

# =========================================================
# ROLE-BASED ACCESS DECORATOR
# =========================================================
def require_roles(*allowed_roles: str):
    """
    Dependency generator to restrict access by user role.
    Example:
        current_user = Depends(require_roles("admin", "vendor"))
    """
    async def role_checker(current_user: UserRead = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# =========================================================
# GET CURRENT USER PROFILE
# =========================================================
@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: UserRead = Depends(get_current_user)):
    """Return profile details of the currently authenticated user."""
    return current_user


# =========================================================
# LIST ALL USERS (Admin + Vendor + Buyer)
# =========================================================
@router.get("/", response_model=List[UserRead])
async def list_users(
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(require_roles("admin", "vendor", "buyer")),
    role: Optional[str] = Query(None, description="Filter users by role"),
    limit: int = Query(100, le=500, description="Maximum number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip for pagination"),
):
    """
    List all users (admin, vendor, buyer).  
    - Admin sees everyone  
    - Vendor or Buyer sees only active users  
    - Optional `role` query filter: ?role=vendor
    """
    include_inactive = current_user.role == "admin"
    all_users = await crud_users.list_users(
        db, limit=limit, offset=offset, include_inactive=include_inactive
    )

    if role:
        all_users = [u for u in all_users if u.role == role]

    # Optional: restrict sensitive fields for non-admins
    if current_user.role != "admin":
        for u in all_users:
            u.email = None  # Hide email for privacy

    return all_users


# =========================================================
# GET USER BY ID
# =========================================================
@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(require_roles("admin", "vendor", "buyer")),
):
    """
    Retrieve a single user by ID.
    - Admins can see all details
    - Vendors/Buyers see limited info
    """
    user = await crud_users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Non-admins cannot see sensitive fields
    if current_user.role != "admin":
        user.email = None

    return user


# =========================================================
# UPDATE OWN PROFILE (Self or Admin)
# =========================================================
@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    update_data: dict,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Update a user.
    - Admin can edit any user
    - Users can edit only themselves
    """
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    updated_user = await crud_users.update_user(db, user_id, update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found or inactive")
    return updated_user


# =========================================================
# DELETE USER (Admin Only)
# =========================================================
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(require_roles("admin")),
):
    """
    Soft-delete a user (mark inactive).
    - Admin-only access.
    """
    success = await crud_users.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or already inactive")
    return {"detail": "User deleted successfully"}
