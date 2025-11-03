from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.vendor import VendorCreate, VendorRead
from app.crud import vendors as crud_vendors

router = APIRouter(
    prefix="/vendors",
    tags=["vendors"],
    responses={404: {"description": "Vendor not found"}},
)


@router.post(
    "/",
    response_model=VendorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vendor",
    description="""
    Create a new dataset vendor/provider in the marketplace.
    
    A vendor can:
    - Upload and manage datasets
    - Configure AI agents for dataset processing
    - Set pricing and licensing terms
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
):
    vendor = await crud_vendors.create_vendor(db, vendor_in)
    return vendor


@router.get(
    "/",
    response_model=List[VendorRead],
    summary="List all vendors",
    description="Get a paginated list of all dataset vendors in the marketplace.",
    response_description="List of vendor profiles",
)
async def get_vendors(
    limit: int = Query(100, description="Maximum number of vendors to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of vendors to skip", ge=0),
    db: AsyncSession = Depends(get_session),
):
    vendors = await crud_vendors.list_vendors(db, limit=limit, offset=offset)
    return vendors


@router.get(
    "/{vendor_id}",
    response_model=VendorRead,
    summary="Get a specific vendor",
    description="Get detailed information about a vendor by their ID.",
    response_description="The vendor's full profile information",
)
async def get_vendor(
    vendor_id: str = Path(..., description="The UUID of the vendor to retrieve"),
    db: AsyncSession = Depends(get_session),
):
    vendor = await crud_vendors.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.put(
    "/{vendor_id}",
    response_model=VendorRead,
    summary="Update a vendor",
    description="Update a vendor's profile information.",
    response_description="The updated vendor profile",
)
async def update_vendor(
    vendor_id: str = Path(..., description="The UUID of the vendor to update"),
    update: Dict = Body(
        ...,
        description="Fields to update",
        example={
            "description": "Updated company description",
            "contact_email": "new.contact@example.com",
        },
    ),
    db: AsyncSession = Depends(get_session),
):
    vendor = await crud_vendors.update_vendor(db, vendor_id, update)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.delete(
    "/{vendor_id}",
    summary="Delete a vendor",
    description="""
    Delete a vendor profile.
    
    This will also delete:
    - All vendor's datasets
    - All vendor's AI agents
    - All associated dataset columns
    """,
    responses={
        200: {"description": "Vendor successfully deleted"},
        404: {"description": "Vendor not found"},
    },
)
async def delete_vendor(
    vendor_id: str = Path(..., description="The UUID of the vendor to delete"),
    db: AsyncSession = Depends(get_session),
):
    ok = await crud_vendors.delete_vendor(db, vendor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"deleted": True}
