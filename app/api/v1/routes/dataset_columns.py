from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.dataset_column import DatasetColumnCreate, DatasetColumnRead
from app.crud import dataset_columns as crud_cols

router = APIRouter(prefix="/dataset-columns", tags=["dataset-columns"])


@router.post("/", response_model=DatasetColumnRead, status_code=status.HTTP_201_CREATED)
async def create_column(col_in: DatasetColumnCreate, db: AsyncSession = Depends(get_session)):
    col = await crud_cols.create_dataset_column(db, col_in)
    return col


@router.get("/{dataset_id}", response_model=List[DatasetColumnRead])
async def get_columns(dataset_id: str, db: AsyncSession = Depends(get_session)):
    cols = await crud_cols.list_dataset_columns(db, dataset_id)
    return cols


@router.get("/col/{col_id}", response_model=DatasetColumnRead)
async def get_column(col_id: int, db: AsyncSession = Depends(get_session)):
    col = await crud_cols.get_dataset_column(db, col_id)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    return col


@router.put("/col/{col_id}", response_model=DatasetColumnRead)
async def update_column(col_id: int, update: dict, db: AsyncSession = Depends(get_session)):
    col = await crud_cols.update_dataset_column(db, col_id, update)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    return col


@router.delete("/col/{col_id}")
async def delete_column(col_id: int, db: AsyncSession = Depends(get_session)):
    ok = await crud_cols.delete_dataset_column(db, col_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Column not found")
    return {"deleted": True}
