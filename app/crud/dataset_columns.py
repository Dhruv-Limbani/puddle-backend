from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import DatasetColumn
from app.schemas.dataset_column import DatasetColumnCreate, DatasetColumnRead


# =============================
# CREATE DATASET COLUMN
# =============================
async def create_dataset_column(
    db: AsyncSession, col_in: Union[DatasetColumnCreate, dict]
) -> DatasetColumnRead:
    if isinstance(col_in, dict):
        col_in = DatasetColumnCreate(**col_in)

    col = DatasetColumn(**col_in.model_dump())
    db.add(col)
    await db.commit()
    await db.refresh(col)
    return DatasetColumnRead.model_validate(col)


# =============================
# GET DATASET COLUMN (ORM)
# =============================
async def get_dataset_column_obj(db: AsyncSession, col_id: int) -> Optional[DatasetColumn]:
    return await db.get(DatasetColumn, col_id)


# =============================
# LIST DATASET COLUMNS
# =============================
async def list_dataset_columns(db: AsyncSession, dataset_id: str) -> List[DatasetColumnRead]:
    result = await db.execute(select(DatasetColumn).where(DatasetColumn.dataset_id == dataset_id))
    cols = result.scalars().all()
    return [DatasetColumnRead.model_validate(col) for col in cols]


# =============================
# UPDATE DATASET COLUMN
# =============================
async def update_dataset_column(
    db: AsyncSession, col_id: int, update_data: dict
) -> Optional[DatasetColumnRead]:
    col = await db.get(DatasetColumn, col_id)
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
    return DatasetColumnRead.model_validate(col)


# =============================
# DELETE DATASET COLUMN
# =============================
async def delete_dataset_column(db: AsyncSession, col_id: int) -> bool:
    col = await db.get(DatasetColumn, col_id)
    if not col:
        return False
    await db.delete(col)
    await db.commit()
    return True
