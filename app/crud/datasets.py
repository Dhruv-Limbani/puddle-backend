# app/crud/datasets.py
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.models.models import Dataset, DatasetColumn
from app.schemas.dataset import (
    DatasetCreate,
    DatasetRead,
    DatasetUpdate,
    DatasetColumn as DatasetColumnSchema,
    DatasetColumnRead,
)
from app.utils.embedding_utils import build_embedding_input, generate_embedding


# ======================================================
# Helper: serialize dataset with nested columns
# ======================================================
def serialize_dataset(ds: Dataset) -> DatasetRead:
    # Explicitly serialize columns to avoid lazy-loading issues
    columns_list = []
    if hasattr(ds, 'columns') and ds.columns is not None:
        try:
            columns_list = [
                DatasetColumnRead(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    data_type=c.data_type,
                    sample_values=c.sample_values,
                    created_at=c.created_at,
                )
                for c in ds.columns
            ]
        except Exception as e:
            print(f"Error serializing columns: {e}")
            columns_list = []
    
    return DatasetRead(
        id=ds.id,
        vendor_id=ds.vendor_id,
        title=ds.title,
        description=ds.description,
        domain=ds.domain,
        dataset_type=ds.dataset_type,
        granularity=ds.granularity,
        pricing_model=ds.pricing_model,
        license=ds.license,
        topics=ds.topics,
        entities=ds.entities,
        temporal_coverage=ds.temporal_coverage,
        geographic_coverage=ds.geographic_coverage,
        visibility=ds.visibility,
        status=ds.status,
        embedding_input=ds.embedding_input,
        embedding=ds.embedding,
        created_at=ds.created_at,
        updated_at=ds.updated_at,
        columns=columns_list,
    )


# ======================================================
# CREATE with nested columns
# ======================================================
async def create_dataset_with_columns(db: AsyncSession, data: Dict[str, Any]) -> DatasetRead:
    columns_data = data.pop("columns", None)

    # Defensive: ensure embedding exists (route already does, but double-check)
    if not data.get("embedding") or not data.get("embedding_input"):
        text = build_embedding_input(data)
        data["embedding_input"] = text
        data["embedding"] = await generate_embedding(text)

    dataset = Dataset(**data)
    db.add(dataset)
    await db.flush()

    if columns_data:
        for col in columns_data:
            # accept dicts or pydantic models
            if hasattr(col, "model_dump"):
                col_payload = col.model_dump()
            elif isinstance(col, dict):
                col_payload = col
            else:
                # fallback convert to dict
                col_payload = dict(col)
            db.add(DatasetColumn(dataset_id=dataset.id, **col_payload))

    await db.commit()
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.columns))
        .where(Dataset.id == dataset.id)
    )
    dataset = result.scalars().first()
    return serialize_dataset(dataset)


# ======================================================
# GET dataset + columns
# ======================================================
async def get_dataset_with_columns(db: AsyncSession, dataset_id: str) -> Optional[DatasetRead]:
    result = await db.execute(
        select(Dataset)
            .options(selectinload(Dataset.columns))
            .where(Dataset.id == dataset_id)
    )
    ds = result.scalars().first()
    if not ds:
        return None
    return serialize_dataset(ds)


# ======================================================
# GET dataset ORM object
# ======================================================
async def get_dataset_obj(db: AsyncSession, dataset_id: str) -> Optional[Dataset]:
    return await db.get(Dataset, dataset_id)


# ======================================================
# LIST DATASETS (with search + role filtering)
# ======================================================
async def list_datasets(
    db: AsyncSession,
    role: str,
    search: Optional[str],
    limit: int,
    offset: int,
) -> List[DatasetRead]:
    query = select(Dataset)

    if role == "buyer":
        query = query.where(Dataset.visibility == "public")

    if search:
        ilike = f"%{search}%"
        query = query.where(Dataset.title.ilike(ilike))

    result = await db.execute(
        query.options(selectinload(Dataset.columns)).limit(limit).offset(offset)
    )
    datasets = result.scalars().unique().all()
    return [serialize_dataset(ds) for ds in datasets]


# ======================================================
# UPDATE with full column replacement (if columns provided)
# ======================================================
async def update_dataset_with_columns(
    db: AsyncSession,
    dataset_id: str,
    update_data: Dict[str, Any],
) -> Optional[DatasetRead]:
    ds = await db.get(Dataset, dataset_id)
    if not ds:
        return None

    # detect replacement
    replace_columns = update_data.pop("replace_columns", False)
    # support clients sending `columns` directly
    columns_data = update_data.pop("columns", None)

    # apply dataset field updates
    for k, v in update_data.items():
        if hasattr(ds, k):
            setattr(ds, k, v)

    # Rebuild embedding if certain fields changed
    if any(k in update_data for k in ["title", "description", "domain", "topics", "entities"]):
        # build clean payload for embedding builder
        ds_payload = {
            "title": getattr(ds, "title", None),
            "description": getattr(ds, "description", None),
            "domain": getattr(ds, "domain", None),
            "topics": getattr(ds, "topics", None),
            "columns": [
                {"name": c.name, "description": c.description}
                for c in ds.columns
            ],
        }
        text = build_embedding_input(ds_payload)
        ds.embedding_input = text
        ds.embedding = await generate_embedding(text)

    # Column replacement behaviour
    if columns_data is not None:
        # replace_columns is implicitly True when columns provided
        await db.execute(delete(DatasetColumn).where(DatasetColumn.dataset_id == dataset_id))
        for col in columns_data:
            if hasattr(col, "model_dump"):
                col_payload = col.model_dump()
            elif isinstance(col, dict):
                col_payload = col
            else:
                col_payload = dict(col)
            db.add(DatasetColumn(dataset_id=dataset_id, **col_payload))

    db.add(ds)
    await db.commit()
    
    # Reload with columns to ensure relationship is populated
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.columns))
        .where(Dataset.id == dataset_id)
    )
    ds = result.scalars().first()
    return serialize_dataset(ds)


# ======================================================
# DELETE DATASET
# ======================================================
async def delete_dataset(db: AsyncSession, dataset_id: str) -> bool:
    ds = await db.get(Dataset, dataset_id)
    if not ds:
        return False

    await db.delete(ds)
    await db.commit()
    return True


# ======================================================
# EMBEDDING SEARCH (uses pgvector .cosine_distance or fallback)
# ======================================================
async def search_by_embedding(
    db: AsyncSession,
    embedding: List[float],
    top_k: int,
    role: str,
):
    vector = embedding

    # This uses the pgvector column method .cosine_distance if available.
    # If your dialect doesn't support that expression, adapt accordingly.
    stmt = select(
        Dataset.id,
        Dataset.title,
        Dataset.embedding.cosine_distance(vector).label("distance")
    )

    if role == "buyer":
        stmt = stmt.where(Dataset.visibility == "public")

    stmt = stmt.order_by("distance").limit(top_k)
    result = await db.execute(stmt)
    rows = result.mappings().all()

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "score": 1 - r["distance"],
        }
        for r in rows
    ]
