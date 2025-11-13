# app/api/v1/routes/datasets.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.db import get_session
from app.core.auth import get_current_user
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetUpdate
from app.schemas.user import UserRead
from app.crud import datasets as crud_datasets
from app.crud import vendors as crud_vendors
from app.models.models import Dataset, Vendor
from app.utils.embedding_utils import generate_embedding, build_embedding_input
from pydantic import BaseModel

router = APIRouter(prefix="/datasets", tags=["datasets"])


async def _get_vendor_for_user(db: AsyncSession, user_id: str) -> Optional[Vendor]:
    result = await db.execute(select(Vendor).where(Vendor.user_id == str(user_id)))
    return result.scalars().first()


async def verify_vendor_owns_dataset(dataset: Dataset, current_user: UserRead, db: AsyncSession):
    if current_user.role == "admin":
        return True
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not authorized")
    vendor = await _get_vendor_for_user(db, current_user.id)
    if not vendor or str(vendor.id) != str(dataset.vendor_id):
        raise HTTPException(status_code=403, detail="This dataset is not yours")
    return True


# CREATE DATASET (with nested columns)
@router.post("/", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset_in: DatasetCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if current_user.role not in {"admin", "vendor"}:
        raise HTTPException(status_code=403, detail="Only vendors or admins can create datasets")

    if current_user.role == "vendor":
        vendor = await _get_vendor_for_user(db, current_user.id)
        if not vendor:
            raise HTTPException(status_code=400, detail="Vendor profile missing")
        if str(vendor.id) != str(dataset_in.vendor_id):
            raise HTTPException(status_code=403, detail="You can only add datasets to your own vendor")
    else:
        vendor = await crud_vendors.get_vendor(db, str(dataset_in.vendor_id))
        if not vendor:
            raise HTTPException(status_code=400, detail="Vendor does not exist")

    data = dataset_in.model_dump(exclude_none=True)

    # Build embedding input and vector
    embedding_input = build_embedding_input(data)
    data["embedding_input"] = embedding_input
    data["embedding"] = await generate_embedding(embedding_input)

    created = await crud_datasets.create_dataset_with_columns(db, data)
    return created


# LIST DATASETS
@router.get("/", response_model=List[DatasetRead])
async def list_datasets(
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    results = await crud_datasets.list_datasets(
        db=db,
        role=current_user.role,
        search=search,
        limit=limit,
        offset=offset,
    )
    return results


# GET DATASET (with nested columns)
@router.get("/{dataset_id}", response_model=DatasetRead)
async def get_dataset(
    dataset_id: str,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    dataset = await crud_datasets.get_dataset_with_columns(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if current_user.role == "buyer" and dataset.visibility != "public":
        raise HTTPException(status_code=403, detail="Not authorized")

    return dataset


# UPDATE DATASET (all-or-nothing; columns replace if provided)
@router.put("/{dataset_id}", response_model=DatasetRead)
async def update_dataset(
    dataset_id: str,
    update_in: DatasetUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    dataset_obj = await crud_datasets.get_dataset_obj(db, dataset_id)
    if not dataset_obj:
        raise HTTPException(status_code=404, detail="Dataset not found")

    await verify_vendor_owns_dataset(dataset_obj, current_user, db)

    update_data = update_in.model_dump(exclude_none=True)
    # If columns provided, pass them through; CRUD detects and replaces accordingly.
    updated = await crud_datasets.update_dataset_with_columns(db, dataset_id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update dataset")
    return updated


# DELETE DATASET
@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: str,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    dataset_obj = await crud_datasets.get_dataset_obj(db, dataset_id)
    if not dataset_obj:
        raise HTTPException(status_code=404, detail="Dataset not found")

    await verify_vendor_owns_dataset(dataset_obj, current_user, db)

    ok = await crud_datasets.delete_dataset(db, dataset_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to delete dataset")
    return None


# EMBEDDING SEARCH
class DatasetSearchQuery(BaseModel):
    query: str
    top_k: int = 5


@router.post("/search/embedding")
async def search_by_embedding(
    body: DatasetSearchQuery,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    emb = await generate_embedding(body.query)
    results = await crud_datasets.search_by_embedding(
        db=db,
        embedding=emb,
        top_k=body.top_k,
        role=current_user.role,
    )
    return {"results": results}
