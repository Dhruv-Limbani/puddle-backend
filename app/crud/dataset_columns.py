from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import DatasetColumn
from app.schemas.dataset_column import DatasetColumnCreate


async def create_dataset_column(db: AsyncSession, col_in: DatasetColumnCreate) -> DatasetColumn:
    col = DatasetColumn(**col_in.dict())
    db.add(col)
    await db.commit()
    await db.refresh(col)
    return col


async def list_dataset_columns(db: AsyncSession, dataset_id: str) -> List[DatasetColumn]:
    result = await db.execute(select(DatasetColumn).where(DatasetColumn.dataset_id == dataset_id))
    return result.scalars().all()


async def get_dataset_column(db: AsyncSession, col_id: int) -> Optional[DatasetColumn]:
    result = await db.execute(select(DatasetColumn).where(DatasetColumn.id == col_id))
    return result.scalars().first()


async def update_dataset_column(db: AsyncSession, col_id: int, update_data: dict) -> Optional[DatasetColumn]:
    col = await get_dataset_column(db, col_id)
    if not col:
        return None
    for key, value in update_data.items():
        if key in ("id", "created_at"):
            continue
        if hasattr(col, key):
            setattr(col, key, value)
    db.add(col)
    await db.commit()
    await db.refresh(col)
    return col


async def delete_dataset_column(db: AsyncSession, col_id: int) -> bool:
    col = await get_dataset_column(db, col_id)
    if not col:
        return False
    await db.delete(col)
    await db.commit()
    return True
