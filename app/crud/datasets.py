from typing import List, Optional, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Dataset
from app.schemas.dataset import DatasetCreate, DatasetRead
from app.utils.embedding_utils import build_and_embed


async def create_dataset(db: AsyncSession, dataset_in: Union[DatasetCreate, dict]) -> DatasetRead:
    if isinstance(dataset_in, dict):
        dataset_in = DatasetCreate(**dataset_in)

    ds_dict: Dict[str, Any] = dataset_in.model_dump()

    if not ds_dict.get("embedding") or not ds_dict.get("embedding_input"):
        embedding_vector = await build_and_embed(ds_dict)
        ds_dict["embedding"] = embedding_vector
        ds_dict["embedding_input"] = ds_dict.get("embedding_input") or ""

    dataset_obj = Dataset(**ds_dict)
    db.add(dataset_obj)
    await db.commit()
    await db.refresh(dataset_obj)
    return DatasetRead.model_validate(dataset_obj)


async def get_dataset(db: AsyncSession, dataset_id: str) -> Optional[DatasetRead]:
    dataset_obj = await db.get(Dataset, dataset_id)
    return DatasetRead.model_validate(dataset_obj) if dataset_obj else None


async def list_datasets(db: AsyncSession, *, limit: int = 100, offset: int = 0) -> List[DatasetRead]:
    result = await db.execute(select(Dataset).limit(limit).offset(offset))
    datasets = result.scalars().all()
    return [DatasetRead.model_validate(ds) for ds in datasets]


async def update_dataset(db: AsyncSession, dataset_id: str, update_data: dict) -> Optional[DatasetRead]:
    dataset_obj = await db.get(Dataset, dataset_id)
    if not dataset_obj:
        return None

    embedding_fields = {"title", "description", "domain", "topics", "columns"}
    rebuild_embedding = any(field in update_data for field in embedding_fields)

    for key, value in update_data.items():
        if key in ("id", "created_at"):
            continue
        if hasattr(dataset_obj, key):
            setattr(dataset_obj, key, value)

    if rebuild_embedding:
        embedding_vector = await build_and_embed(dataset_obj.__dict__)
        dataset_obj.embedding = embedding_vector
        dataset_obj.embedding_input = dataset_obj.embedding_input or ""

    db.add(dataset_obj)
    await db.commit()
    await db.refresh(dataset_obj)
    return DatasetRead.model_validate(dataset_obj)


async def delete_dataset(db: AsyncSession, dataset_id: str) -> bool:
    dataset_obj = await db.get(Dataset, dataset_id)
    if not dataset_obj:
        return False

    if hasattr(dataset_obj, "status"):
        dataset_obj.status = "inactive"
        db.add(dataset_obj)
        await db.commit()
        await db.refresh(dataset_obj)
        return True

    await db.delete(dataset_obj)
    await db.commit()
    return True
