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
                    dataset_id=c.dataset_id,
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
    await db.flush() # dataset.id is now available

    if columns_data:
        # --- START FIX ---
        # Don't assign to dataset.columns
        # Instead, create columns with the new dataset_id and add to session
        for col in columns_data:
            # accept dicts or pydantic models
            if hasattr(col, "model_dump"):
                col_payload = col.model_dump()
            elif isinstance(col, dict):
                col_payload = col
            else:
                # fallback convert to dict
                col_payload = dict(col)
            
            # Remove 'id' if it's a temp ID from the frontend
            if 'id' in col_payload and str(col_payload['id']).startswith('temp_'):
                del col_payload['id']
            
            # Manually set the foreign key
            col_payload['dataset_id'] = dataset.id
            
            # Create the object and add it to the session
            new_col_obj = DatasetColumn(**col_payload)
            db.add(new_col_obj)
        # --- END FIX ---
        
        # REMOVED THIS LINE:
        # dataset.columns = new_columns_list

    await db.commit()
    
    # Reload with columns to ensure relationship is populated for the serializer
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
# LIST DATASETS (for Marketplace)
# ======================================================
async def list_datasets(
    db: AsyncSession,
    role: str,
    search: Optional[str],
    limit: int,
    offset: int,
) -> List[DatasetRead]:
    query = select(Dataset)

    # Marketplace logic: Buyers/Vendors only see public
    if role == "buyer" or role == "vendor":
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
# LIST DATASETS BY VENDOR ID (for Data Catalog)
# ======================================================
async def list_datasets_by_vendor(
    db: AsyncSession,
    vendor_id: str,
) -> List[DatasetRead]:
    query = (
        select(Dataset)
        .where(Dataset.vendor_id == vendor_id)
        .options(selectinload(Dataset.columns))
        .order_by(Dataset.updated_at.desc())
    )
    
    result = await db.execute(query)
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
    
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.columns))
        .where(Dataset.id == dataset_id)
    )
    ds = result.scalars().first()

    if not ds:
        return None

    columns_data = update_data.pop("columns", None)

    # apply dataset field updates
    for k, v in update_data.items():
        if hasattr(ds, k):
            setattr(ds, k, v)

    # Rebuild embedding if certain fields changed
    if any(k in update_data for k in ["title", "description", "domain", "topics", "entities"]):
        
        # --- THIS IS THE FIX ---
        column_payload_for_embedding = []
        if columns_data is not None:
            # Use the new column data (which are dicts or pydantic models)
            for c_data in columns_data:
                if hasattr(c_data, "model_dump"): # Handle pydantic model
                    c_dict = c_data.model_dump()
                    column_payload_for_embedding.append({
                        "name": c_dict.get("name"),
                        "description": c_dict.get("description")
                    })
                elif isinstance(c_data, dict): # Handle dict
                    column_payload_for_embedding.append({
                        "name": c_data.get("name"), 
                        "description": c_data.get("description")
                    })
        else:
            # Use the existing column data (which are ORM objects)
            column_payload_for_embedding = [
                {"name": c.name, "description": c.description}
                for c in ds.columns
            ]
        # --- END FIX ---

        ds_payload = {
            "title": getattr(ds, "title", None),
            "description": getattr(ds, "description", None),
            "domain": getattr(ds, "domain", None),
            "topics": getattr(ds, "topics", None),
            "columns": column_payload_for_embedding # Use the corrected list
        }
        text = build_embedding_input(ds_payload)
        ds.embedding_input = text
        ds.embedding = await generate_embedding(text)

    # Column replacement behaviour
    if columns_data is not None:
        
        # 1. Create a list of new DatasetColumn ORM objects
        new_columns_list = []
        for col_data in columns_data:
            if hasattr(col_data, "model_dump"):
                col_payload = col_data.model_dump()
            elif isinstance(col_data, dict):
                col_payload = col_data
            else:
                col_payload = dict(col_data)
            
            if 'id' in col_payload:
                del col_payload['id']

            new_columns_list.append(DatasetColumn(**col_payload))

        # 2. Simply assign the new list to the relationship.
        ds.columns = new_columns_list

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