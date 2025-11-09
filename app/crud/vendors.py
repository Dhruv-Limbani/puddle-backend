from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Vendor
from app.schemas.vendor import VendorCreate, VendorRead


# =============================
# CREATE VENDOR
# =============================
async def create_vendor(db: AsyncSession, vendor_in: Union[VendorCreate, dict]) -> VendorRead:
    """
    Create a new vendor.
    Accepts either a VendorCreate Pydantic model or a dict.
    """
    if isinstance(vendor_in, dict):
        vendor_in = VendorCreate(**vendor_in)

    vendor_obj = Vendor(**vendor_in.model_dump())
    db.add(vendor_obj)
    await db.commit()
    await db.refresh(vendor_obj)
    return VendorRead.model_validate(vendor_obj)


# =============================
# GET VENDOR BY ID
# =============================
async def get_vendor(db: AsyncSession, vendor_id: str) -> Optional[VendorRead]:
    """
    Fetch a vendor by ID.
    Only active vendors are returned.
    """
    vendor_obj = await db.get(Vendor, vendor_id)
    if vendor_obj and (not hasattr(vendor_obj, "is_active") or vendor_obj.is_active):
        return VendorRead.model_validate(vendor_obj)
    return None


async def get_vendor_by_user_id(db: AsyncSession, user_id: Union[str, UUID]) -> Optional[VendorRead]:
    """
    Fetch the vendor profile associated with a user.
    """
    query = select(Vendor).where(Vendor.user_id == str(user_id))
    result = await db.execute(query)
    vendor_obj = result.scalars().first()
    if vendor_obj and (not hasattr(vendor_obj, "is_active") or vendor_obj.is_active):
        return VendorRead.model_validate(vendor_obj)
    return None


# =============================
# LIST VENDORS
# =============================
async def list_vendors(
    db: AsyncSession, *, limit: int = 100, offset: int = 0, include_inactive: bool = False
) -> List[VendorRead]:
    """
    List vendors with pagination.
    Set include_inactive=True to include soft-deleted vendors.
    """
    query = select(Vendor)
    if not include_inactive and hasattr(Vendor, "is_active"):
        query = query.where(Vendor.is_active == True)
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    vendors = result.scalars().all()
    return [VendorRead.model_validate(v) for v in vendors]


# =============================
# UPDATE VENDOR
# =============================
async def update_vendor(db: AsyncSession, vendor_id: str, update_data: dict) -> Optional[VendorRead]:
    """
    Update an existing vendor by ID.
    Immutable fields are ignored.
    """
    vendor_obj = await db.get(Vendor, vendor_id)
    if not vendor_obj or (hasattr(vendor_obj, "is_active") and not vendor_obj.is_active):
        return None

    immutable_fields = {"id", "created_at"}
    for key, value in update_data.items():
        if key in immutable_fields:
            continue
        if hasattr(vendor_obj, key):
            setattr(vendor_obj, key, value)

    db.add(vendor_obj)
    await db.commit()
    await db.refresh(vendor_obj)
    return VendorRead.model_validate(vendor_obj)


# =============================
# DELETE VENDOR (SOFT DELETE)
# =============================
async def delete_vendor(db: AsyncSession, vendor_id: str) -> bool:
    """
    Soft-delete a vendor by marking is_active=False.
    Falls back to hard-delete if no is_active field exists.
    Returns True if vendor existed, False otherwise.
    """
    vendor_obj = await db.get(Vendor, vendor_id)
    if not vendor_obj:
        return False

    if hasattr(vendor_obj, "is_active"):
        vendor_obj.is_active = False
        db.add(vendor_obj)
        await db.commit()
        await db.refresh(vendor_obj)
        return True

    await db.delete(vendor_obj)
    await db.commit()
    return True
