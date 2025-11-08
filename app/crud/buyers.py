from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Buyer
from app.schemas.buyer import BuyerCreate, BuyerRead


async def create_buyer(db: AsyncSession, buyer_in: BuyerCreate, user_id: Optional[str] = None) -> BuyerRead:
    """
    Create a new buyer.
    Optionally associate it with a user_id.
    """
    buyer_data = buyer_in.model_dump()
    if user_id:
        buyer_data["user_id"] = user_id
    buyer = Buyer(**buyer_data)
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    return BuyerRead.model_validate(buyer)


async def get_buyer(db: AsyncSession, buyer_id: str) -> Optional[Buyer]:
    """Fetch a buyer ORM object by ID."""
    result = await db.execute(select(Buyer).where(Buyer.id == buyer_id))
    buyer = result.scalars().first()
    return buyer


async def list_buyers(db: AsyncSession, *, limit: int = 100, offset: int = 0) -> List[BuyerRead]:
    """List buyers with pagination."""
    result = await db.execute(select(Buyer).limit(limit).offset(offset))
    buyers = result.scalars().all()
    return [BuyerRead.model_validate(b) for b in buyers]


async def update_buyer(db: AsyncSession, buyer_id: str, update_data: dict) -> Optional[BuyerRead]:
    """Update an existing buyer by ID."""
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
    return BuyerRead.model_validate(buyer)


async def delete_buyer(db: AsyncSession, buyer_id: str) -> bool:
    """Delete a buyer by ID."""
    buyer = await get_buyer(db, buyer_id)
    if not buyer:
        return False
    await db.delete(buyer)
    await db.commit()
    return True
