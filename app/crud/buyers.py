from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Buyer
from app.schemas.buyer import BuyerCreate


async def create_buyer(db: AsyncSession, buyer_in: BuyerCreate) -> Buyer:
    buyer = Buyer(**buyer_in.dict())
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    return buyer


async def get_buyer(db: AsyncSession, buyer_id: str) -> Optional[Buyer]:
    result = await db.execute(select(Buyer).where(Buyer.id == buyer_id))
    return result.scalars().first()


async def list_buyers(db: AsyncSession, *, limit: int = 100, offset: int = 0) -> List[Buyer]:
    result = await db.execute(select(Buyer).limit(limit).offset(offset))
    return result.scalars().all()


async def update_buyer(db: AsyncSession, buyer_id: str, update_data: dict) -> Optional[Buyer]:
    buyer = await get_buyer(db, buyer_id)
    if not buyer:
        return None
    for key, value in update_data.items():
        if key in ("id", "created_at"):
            continue
        if hasattr(buyer, key):
            setattr(buyer, key, value)
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    return buyer


async def delete_buyer(db: AsyncSession, buyer_id: str) -> bool:
    buyer = await get_buyer(db, buyer_id)
    if not buyer:
        return False
    await db.delete(buyer)
    await db.commit()
    return True
