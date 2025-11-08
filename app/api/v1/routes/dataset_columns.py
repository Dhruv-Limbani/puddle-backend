from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_session
from app.schemas.dataset_column import DatasetColumnCreate, DatasetColumnRead
from app.crud import dataset_columns as crud_cols
from app.core.auth import get_current_user
from app.schemas.user import UserRead
from app.models.models import Dataset

router = APIRouter(prefix="/dataset-columns", tags=["dataset-columns"])


# --------------------------
# Helper: verify vendor ownership
# --------------------------
async def verify_vendor_owns_dataset(
    dataset_id: UUID, current_user: UserRead, db: AsyncSession
):
    """Check if current user is allowed to modify this dataset."""
    if current_user.role == "admin":
        return True

    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )

    dataset = await db.get(Dataset, str(dataset_id))
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )
    if dataset.vendor_id != current_user.vendor_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this dataset.",
        )
    return True


# --------------------------
# CREATE COLUMN
# --------------------------
@router.post("/", response_model=DatasetColumnRead, status_code=status.HTTP_201_CREATED)
async def create_column(
    col_in: DatasetColumnCreate,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    await verify_vendor_owns_dataset(col_in.dataset_id, current_user, db)
    col = await crud_cols.create_dataset_column(db, col_in)
    return col


# --------------------------
# LIST COLUMNS FOR A DATASET
# --------------------------
@router.get("/dataset/{dataset_id}", response_model=List[DatasetColumnRead])
async def get_columns(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    # Admins or vendors of this dataset can list; buyers can only view public datasets
    dataset = await db.get(Dataset, str(dataset_id))
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if current_user.role == "vendor" and dataset.vendor_id != current_user.vendor_profile.id:
        raise HTTPException(status_code=403, detail="Not authorized for this dataset")

    # Buyers can see only public datasets
    if current_user.role == "buyer" and dataset.visibility != "public":
        raise HTTPException(status_code=403, detail="Not authorized for this dataset")

    cols = await crud_cols.list_dataset_columns(db, str(dataset_id))
    return cols


# --------------------------
# GET SINGLE COLUMN
# --------------------------
@router.get("/{col_id}", response_model=DatasetColumnRead)
async def get_column(
    col_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    col = await crud_cols.get_dataset_column(db, col_id)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    # Ownership/visibility check
    dataset = await db.get(Dataset, col.dataset_id)
    if current_user.role == "vendor" and dataset.vendor_id != current_user.vendor_profile.id:
        raise HTTPException(status_code=403, detail="Not authorized for this dataset")
    if current_user.role == "buyer" and dataset.visibility != "public":
        raise HTTPException(status_code=403, detail="Not authorized for this dataset")

    return col


# --------------------------
# UPDATE COLUMN
# --------------------------
@router.put("/{col_id}", response_model=DatasetColumnRead)
async def update_column(
    col_id: int,
    update: dict,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    col = await crud_cols.get_dataset_column(db, col_id)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    await verify_vendor_owns_dataset(col.dataset_id, current_user, db)
    updated_col = await crud_cols.update_dataset_column(db, col_id, update)
    return updated_col


# --------------------------
# DELETE COLUMN
# --------------------------
@router.delete("/{col_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    col_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    col = await crud_cols.get_dataset_column(db, col_id)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    await verify_vendor_owns_dataset(col.dataset_id, current_user, db)
    await crud_cols.delete_dataset_column(db, col_id)
    return None  # 204 No Content
