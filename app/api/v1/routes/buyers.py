from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.auth import get_current_user
from app.schemas.user import UserRead
from app.schemas.buyer import BuyerCreate, BuyerRead
from app.crud import buyers as crud_buyers

router = APIRouter(
    prefix="/buyers",
    tags=["buyers"],
    responses={404: {"description": "Buyer not found"}},
)

# =========================================================
# CREATE BUYER (Buyer role only)
# =========================================================
@router.post(
    "/",
    response_model=BuyerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new buyer profile",
    description="Only users with role='buyer' can create their buyer profile.",
)
async def create_buyer(
    buyer_in: BuyerCreate = Body(..., description="Buyer profile details"),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can create buyer profiles")

    # Prevent duplicate profile creation
    existing_buyers = await crud_buyers.list_buyers(db)
    if any(b.user_id == current_user.id for b in existing_buyers):
        raise HTTPException(status_code=400, detail="Buyer profile already exists for this user")

    buyer = await crud_buyers.create_buyer(db, buyer_in, user_id=current_user.id)
    return buyer


# =========================================================
# LIST BUYERS
# =========================================================
@router.get(
    "/",
    response_model=List[BuyerRead],
    summary="List all buyers",
    description="""
    Accessible to:
    - **Admin**: can view all buyers.
    - **Vendor**: can view all buyers.
    - **Buyer**: can view all buyers (for discovery).
    """,
)
async def get_buyers(
    limit: int = Query(100, description="Maximum number of buyers to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of buyers to skip", ge=0),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    if current_user.role not in ("admin", "vendor", "buyer"):
        raise HTTPException(status_code=403, detail="Access denied")

    buyers = await crud_buyers.list_buyers(db, limit=limit, offset=offset)
    return buyers


# =========================================================
# GET BUYER BY ID
# =========================================================
@router.get(
    "/{buyer_id}",
    response_model=BuyerRead,
    summary="Get buyer details by ID",
    description="Accessible to admins, vendors, or the buyer themselves.",
)
async def get_buyer(
    buyer_id: str = Path(..., description="The UUID of the buyer to retrieve"),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    buyer = await crud_buyers.get_buyer(db, buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    if current_user.role not in ("admin", "vendor", "buyer"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Buyers can only view their own private profile
    if current_user.role == "buyer" and buyer.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only view your own profile")

    return buyer


# =========================================================
# UPDATE BUYER (Buyer or Admin)
# =========================================================
@router.put(
    "/{buyer_id}",
    response_model=BuyerRead,
    summary="Update buyer profile",
    description="Buyers can update their own profile. Admins can update any profile.",
)
async def update_buyer(
    buyer_id: str = Path(..., description="The UUID of the buyer to update"),
    update: Dict = Body(..., description="Fields to update"),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    buyer = await crud_buyers.get_buyer(db, buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    if current_user.role not in ("buyer", "admin"):
        raise HTTPException(status_code=403, detail="Only buyers or admins can update profiles")

    if current_user.role == "buyer" and buyer.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    updated_buyer = await crud_buyers.update_buyer(db, buyer_id, update)
    return updated_buyer


# =========================================================
# DELETE BUYER (Admin only)
# =========================================================
@router.delete(
    "/{buyer_id}",
    summary="Delete a buyer profile",
    description="Admin-only route for deleting buyer profiles.",
)
async def delete_buyer(
    buyer_id: str = Path(..., description="The UUID of the buyer to delete"),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete buyers")

    ok = await crud_buyers.delete_buyer(db, buyer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return {"deleted": True}
