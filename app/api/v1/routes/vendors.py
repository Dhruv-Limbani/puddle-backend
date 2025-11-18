from typing import List, Dict
from fastapi import (
    APIRouter, Depends, HTTPException, status, Query, Path, Body
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.auth import get_current_user
from app.schemas.vendor import VendorCreate, VendorRead
from app.crud import vendors as crud_vendors
from app.schemas.user import UserRead

router = APIRouter(
    prefix="/vendors",
    tags=["vendors"],
    responses={
        401: {"description": "Unauthorized access"},
        403: {"description": "Forbidden"},
        404: {"description": "Vendor not found"},
    },
)


# =========================================================
# CREATE VENDOR
# =========================================================
@router.post(
    "/",
    response_model=VendorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vendor profile",
    description="""
    Create a new vendor profile in the marketplace.

    - Only users with the **vendor** role can create their vendor profile.
    - A user can have only one vendor profile linked to their account.
    """,
    response_description="The created vendor profile",
)
async def create_vendor(
    vendor_in: VendorCreate = Body(
        ...,
        description="Vendor details to create",
        example={
            "name": "Example Data Corp",
            "industry_focus": "Finance",
            "description": "Provider of high-quality financial datasets",
            "contact_email": "data@example.com",
        },
    ),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    if current_user.role not in ("vendor", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors or admins can create vendor profiles.",
        )

    # ensure one vendor per user
    existing_vendors = await crud_vendors.list_vendors(db, limit=1000)
    if any(v.user_id == current_user.id for v in existing_vendors):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user already has a vendor profile.",
        )

    vendor_data = vendor_in.model_dump()
    vendor_data["user_id"] = current_user.id

    vendor = await crud_vendors.create_vendor(db, vendor_data)
    return vendor


# =========================================================
# GET CURRENT USER'S VENDOR PROFILE
# =========================================================
@router.get(
    "/me/",
    response_model=VendorRead,
    summary="Get my vendor profile",
    description="Retrieve the vendor profile associated with the current logged-in user. Only accessible by vendors.",
    response_description="Current user's vendor profile",
)
async def get_my_vendor_profile(
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this endpoint"
        )
    
    vendor = await crud_vendors.get_vendor_by_user_id(db, current_user.id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found for this user"
        )
    return vendor


# =========================================================
# LIST VENDORS
# =========================================================
@router.get(
    "/",
    response_model=List[VendorRead],
    summary="List all vendors",
    description="Get a paginated list of all vendors in the marketplace. Accessible to all authenticated users.",
    response_description="List of vendor profiles",
)
async def list_vendors(
    limit: int = Query(100, description="Maximum number of vendors to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of vendors to skip", ge=0),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    vendors = await crud_vendors.list_vendors(db, limit=limit, offset=offset)
    return vendors


# =========================================================
# GET VENDOR BY ID
# =========================================================
@router.get(
    "/{vendor_id}",
    response_model=VendorRead,
    summary="Get vendor details by ID",
    description="Retrieve a vendor’s full profile using their UUID. Accessible to all authenticated users.",
    response_description="Vendor details",
)
async def get_vendor(
    vendor_id: str = Path(..., description="The UUID of the vendor to retrieve"),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    vendor = await crud_vendors.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


# =========================================================
# UPDATE VENDOR
# =========================================================
@router.put(
    "/{vendor_id}",
    response_model=VendorRead,
    summary="Update a vendor profile",
    description="""
    Update a vendor’s profile information.

    - **Admins** can update any vendor.
    - **Vendors** can only update their own profile.
    """,
    response_description="The updated vendor profile",
)
async def update_vendor(
    vendor_id: str = Path(..., description="The UUID of the vendor to update"),
    update: Dict = Body(
        ...,
        description="Fields to update (partial or full)",
        example={
            "description": "Updated description of the vendor",
            "contact_email": "new.email@vendor.com",
        },
    ),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    vendor = await crud_vendors.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    # role-based check
    if current_user.role != "admin" and str(vendor.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own vendor profile.",
        )

    updated_vendor = await crud_vendors.update_vendor(db, vendor_id, update)
    return updated_vendor


# =========================================================
# DELETE VENDOR
# =========================================================
@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a vendor profile",
    description="""
    Delete a vendor and all associated resources.

    - **Admins** can delete any vendor.
    - **Vendors** can delete only their own profile.
    """,
    responses={
        200: {"description": "Vendor successfully deleted"},
        403: {"description": "Forbidden"},
        404: {"description": "Vendor not found"},
    },
)
async def delete_vendor(
    vendor_id: str = Path(..., description="The UUID of the vendor to delete"),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    vendor = await crud_vendors.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    if current_user.role != "admin" and str(vendor.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own vendor profile.",
        )

    ok = await crud_vendors.delete_vendor(db, vendor_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return {"deleted": True, "vendor_id": vendor_id}
