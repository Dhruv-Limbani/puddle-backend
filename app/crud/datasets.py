from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Dataset
from app.schemas.dataset import DatasetCreate


async def create_dataset(db: AsyncSession, dataset_in: DatasetCreate) -> Dataset:
    dataset = Dataset(**dataset_in.dict())
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset


async def get_dataset(db: AsyncSession, dataset_id: str) -> Optional[Dataset]:
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    return result.scalars().first()


async def list_datasets(db: AsyncSession, *, limit: int = 100, offset: int = 0) -> List[Dataset]:
    result = await db.execute(select(Dataset).limit(limit).offset(offset))
    return result.scalars().all()


async def update_dataset(db: AsyncSession, dataset_id: str, update_data: dict) -> Optional[Dataset]:
    dataset = await get_dataset(db, dataset_id)
    if not dataset:
        return None
    for key, value in update_data.items():
        if key in ("id", "created_at"):
            continue
        if hasattr(dataset, key):
            setattr(dataset, key, value)
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset


async def delete_dataset(db: AsyncSession, dataset_id: str) -> bool:
    dataset = await get_dataset(db, dataset_id)
    if not dataset:
        return False
    # Soft-delete by setting status to inactive if field exists
    if hasattr(dataset, "status"):
        dataset.status = "inactive"
        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)
        return True
    # Fallback: hard delete
    await db.delete(dataset)
    await db.commit()
    return True