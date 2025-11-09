from typing import List, Dict, Any, Optional
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text
from pydantic import BaseModel

from app.core.db import get_session
from app.core.auth import get_current_user
from app.schemas.dataset import DatasetCreate, DatasetRead
from app.schemas.user import UserRead
from app.crud import datasets as crud_datasets
from app.crud import vendors as crud_vendors
from app.utils.embedding_utils import generate_embedding, build_embedding_input

router = APIRouter(prefix="/datasets", tags=["datasets"])


# =============================
# Dataset Update Model
# =============================
class DatasetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    dataset_type: Optional[str] = None
    granularity: Optional[str] = None
    pricing_model: Optional[str] = None
    license: Optional[str] = None
    topics: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    temporal_coverage: Optional[Any] = None
    geographic_coverage: Optional[Any] = None
    visibility: Optional[str] = None
    status: Optional[str] = None
    columns: Optional[List[Dict[str, Any]]] = None


# =============================
# CREATE DATASET
# =============================
@router.post("/", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset_in: DatasetCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if current_user.role not in {"vendor", "admin"}:
        raise HTTPException(status_code=403, detail="Only vendors or admins can create datasets")

    # Validate vendor ownership
    vendor = await crud_vendors.get_vendor_by_user_id(db, current_user.id) if current_user.role == "vendor" else None
    if current_user.role == "vendor":
        if not vendor:
            raise HTTPException(status_code=400, detail="Vendor profile not found")
        if str(vendor.id) != str(dataset_in.vendor_id):
            raise HTTPException(status_code=403, detail="You can only create datasets for your vendor profile")

    # Ensure vendor exists when admin creates datasets
    if current_user.role == "admin":
        vendor_check = await crud_vendors.get_vendor(db, str(dataset_in.vendor_id))
        if not vendor_check:
            raise HTTPException(status_code=400, detail="Vendor not found for provided vendor_id")

    data = dataset_in.dict()

    # Build embedding
    embedding_input = build_embedding_input(data)
    embedding_vector = await generate_embedding(embedding_input)
    data["embedding_input"] = embedding_input
    data["embedding"] = embedding_vector

    created = await crud_datasets.create_dataset(db, DatasetCreate(**data))
    return DatasetRead.model_validate(created)


# =============================
# LIST DATASETS WITH FILTERING
# =============================
@router.get("/", response_model=List[DatasetRead])
async def list_datasets(
    filters: Optional[str] = Query(None, description="JSON string of dynamic filters"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List datasets with optional search and dynamic filters.
    Buyers only see public datasets.
    """
    query = select(crud_datasets.Dataset)
    where_clauses = []

    # Role-based visibility
    if current_user.role == "buyer":
        where_clauses.append(crud_datasets.Dataset.visibility == "public")

    # Parse filters JSON
    filter_dict = {}
    if filters:
        try:
            filter_dict = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON for filters")

    for key, value in filter_dict.items():
        if not hasattr(crud_datasets.Dataset, key):
            continue
        attr = getattr(crud_datasets.Dataset, key)
        # Handle list fields
        if isinstance(value, list):
            where_clauses.append(attr.contains(value))
        else:
            where_clauses.append(attr == value)

    # Full-text search
    if search:
        where_clauses.append(
            or_(
                crud_datasets.Dataset.title.ilike(f"%{search}%"),
                crud_datasets.Dataset.description.ilike(f"%{search}%"),
            )
        )

    if where_clauses:
        query = query.where(and_(*where_clauses))

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    datasets = result.scalars().all()
    return [crud_datasets.to_dataset_read(ds) for ds in datasets]


# =============================
# GET SINGLE DATASET
# =============================
@router.get("/{dataset_id}", response_model=DatasetRead)
async def get_dataset(
    dataset_id: str = Path(...),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    dataset = await crud_datasets.get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if current_user.role == "buyer" and dataset.visibility != "public":
        raise HTTPException(status_code=403, detail="Access denied")
    return dataset


# =============================
# UPDATE DATASET
# =============================
@router.put("/{dataset_id}", response_model=DatasetRead)
async def update_dataset(
    dataset_id: str,
    update: DatasetUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    dataset = await crud_datasets.get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if current_user.role == "admin":
        pass
    elif current_user.role == "vendor":
        vendor = await crud_vendors.get_vendor_by_user_id(db, current_user.id)
        if not vendor or str(vendor.id) != str(dataset.vendor_id):
            raise HTTPException(status_code=403, detail="Not allowed to update this dataset")
    else:
        raise HTTPException(status_code=403, detail="Not allowed to update this dataset")

    updated_dataset = await crud_datasets.update_dataset(db, dataset_id, update.dict(exclude_none=True))
    return updated_dataset


# =============================
# DELETE DATASET
# =============================
@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    dataset = await crud_datasets.get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if current_user.role == "admin":
        pass
    elif current_user.role == "vendor":
        vendor = await crud_vendors.get_vendor_by_user_id(db, current_user.id)
        if not vendor or str(vendor.id) != str(dataset.vendor_id):
            raise HTTPException(status_code=403, detail="Not allowed to delete this dataset")
    else:
        raise HTTPException(status_code=403, detail="Not allowed to delete this dataset")

    ok = await crud_datasets.delete_dataset(db, dataset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"deleted": True}


# =============================
# SEARCH DATASETS BY EMBEDDING
# =============================
class DatasetSearchQuery(BaseModel):
    query: str
    top_k: int = Query(5, ge=1, le=100)


class DatasetSearchResult(BaseModel):
    results: List[Dict[str, Any]]


@router.post("/search/embedding", response_model=DatasetSearchResult)
async def search_by_embedding(
    query: DatasetSearchQuery = Body(...),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    emb = await generate_embedding(query.query)

    # Wrap raw SQL string with text()
    result = await db.execute(
        text("SELECT id, title, description, embedding, visibility FROM datasets WHERE embedding IS NOT NULL")
    )
    rows = result.fetchall()

    import numpy as np

    def cosine(a, b):
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    scored = []
    for r in rows:
        emb_db = r[3]
        vis = r[4]

        if current_user.role == "buyer" and vis != "public":
            continue

        if emb_db is None:
            continue
        emb_db_list = list(emb_db) if not isinstance(emb_db, list) else emb_db
        score = cosine(emb, emb_db_list)
        scored.append({"id": r[0], "title": r[1], "description": r[2], "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"results": scored[: query.top_k]}

