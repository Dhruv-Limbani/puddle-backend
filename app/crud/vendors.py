from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Vendor
from app.schemas.vendor import VendorCreate


async def create_vendor(db: AsyncSession, vendor_in: VendorCreate | dict) -> Vendor:
    if isinstance(vendor_in, dict):
        vendor_in = VendorCreate(**vendor_in)
    vendor = Vendor(**vendor_in.model_dump())
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    return vendor


async def get_vendor(db: AsyncSession, vendor_id: str) -> Optional[Vendor]:
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    return result.scalars().first()


async def list_vendors(db: AsyncSession, *, limit: int = 100, offset: int = 0) -> List[Vendor]:
    result = await db.execute(select(Vendor).limit(limit).offset(offset))
    return result.scalars().all()


async def update_vendor(db: AsyncSession, vendor_id: str, update_data: dict) -> Optional[Vendor]:
    vendor = await get_vendor(db, vendor_id)
    if not vendor:
        return None
    for key, value in update_data.items():
        if key in ("id", "created_at"):
            continue
        if hasattr(vendor, key):
            setattr(vendor, key, value)
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    return vendor


async def delete_vendor(db: AsyncSession, vendor_id: str) -> bool:
    vendor = await get_vendor(db, vendor_id)
    if not vendor:
        return False
    await db.delete(vendor)
    await db.commit()
    return True
