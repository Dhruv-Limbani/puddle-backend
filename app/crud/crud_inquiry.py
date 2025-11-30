from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.models import Inquiry
from app.schemas.inquiry import InquiryCreate, InquiryRead

async def create_inquiry(db: AsyncSession, inquiry_in: Union[InquiryCreate, dict]) -> InquiryRead:
    if isinstance(inquiry_in, dict):
        inquiry_in = InquiryCreate(**inquiry_in)

    inquiry = Inquiry(**inquiry_in.model_dump())
    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)
    return InquiryRead.model_validate(inquiry)

async def get_inquiry(db: AsyncSession, inquiry_id: UUID) -> Optional[InquiryRead]:
    inquiry = await db.get(Inquiry, inquiry_id)
    if inquiry:
        return InquiryRead.model_validate(inquiry)
    return None

async def list_inquiries_by_buyer(
    db: AsyncSession, *, buyer_id: UUID, limit: int = 100, offset: int = 0
) -> List[InquiryRead]:
    query = select(Inquiry).where(Inquiry.buyer_id == buyer_id).limit(limit).offset(offset)
    result = await db.execute(query)
    inquiries = result.scalars().all()
    return [InquiryRead.model_validate(i) for i in inquiries]

async def list_inquiries_by_vendor(
    db: AsyncSession, *, vendor_id: UUID, limit: int = 100, offset: int = 0
) -> List[InquiryRead]:
    query = select(Inquiry).where(Inquiry.vendor_id == vendor_id).limit(limit).offset(offset)
    result = await db.execute(query)
    inquiries = result.scalars().all()
    return [InquiryRead.model_validate(i) for i in inquiries]

async def update_inquiry(db: AsyncSession, inquiry_id: UUID, update_data: dict) -> Optional[InquiryRead]:
    inquiry = await db.get(Inquiry, inquiry_id)
    if not inquiry:
        return None

    for key, value in update_data.items():
        if hasattr(inquiry, key):
            setattr(inquiry, key, value)

    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)
    return InquiryRead.model_validate(inquiry)
