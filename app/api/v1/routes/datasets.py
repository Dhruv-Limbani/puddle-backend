from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.db import get_session
from app.schemas.dataset import DatasetCreate, DatasetRead
from app.crud import datasets as crud_datasets
from app.utils.embedding_utils import generate_embedding, build_embedding_input


class DatasetSearchQuery(BaseModel):
    query: str = Query(..., description="The text to find similar datasets for")
    top_k: int = Query(5, description="Number of results to return", ge=1, le=100)


class DatasetSearchResult(BaseModel):
    results: List[Dict[str, Any]]


router = APIRouter(prefix="/datasets", tags=["datasets"])

from app.core.db import get_session
from app.schemas.dataset import DatasetCreate, DatasetRead
from app.crud import datasets as crud_datasets
from app.utils.embedding_utils import generate_embedding, build_embedding_input


class DatasetSearchQuery(BaseModel):
    query: str = Query(..., description="The text to find similar datasets for")
    top_k: int = Query(5, description="Number of results to return", ge=1, le=100)


class DatasetSearchResult(BaseModel):
    results: List[Dict[str, Any]]


router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post(
    "/",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new dataset",
    description="""
    Create a new dataset with automatic embedding generation.
    
    The embedding is generated from:
    - Domain field
    - Topics (if provided)
    - Description
    - Column information (names and descriptions)
    
    The generated embedding can be used for similarity search.
    """,
    response_description="The created dataset including its ID and embedding vector",
)
async def create_dataset(dataset_in: DatasetCreate, db: AsyncSession = Depends(get_session)):
    # Build embedding input from domain, topics, description and columns
    data = dataset_in.dict()
    embedding_input = build_embedding_input(data)
    emb = await generate_embedding(embedding_input)
    data["embedding_input"] = embedding_input
    data["embedding"] = emb
    dataset = await crud_datasets.create_dataset(db, DatasetCreate(**data))
    return dataset
    # Build embedding input from domain, topics, description and columns
    data = dataset_in.dict()
    embedding_input = build_embedding_input(data)
    emb = await generate_embedding(embedding_input)
    data["embedding_input"] = embedding_input
    data["embedding"] = emb
    dataset = await crud_datasets.create_dataset(db, DatasetCreate(**data))
    return dataset


@router.get(
    "/",
    response_model=List[DatasetRead],
    summary="List all datasets",
    description="Get a paginated list of all datasets in the catalog.",
    response_description="List of datasets with their metadata and embeddings",
)
async def get_datasets(
    limit: int = Query(100, description="Maximum number of datasets to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of datasets to skip", ge=0),
    db: AsyncSession = Depends(get_session),
):
    datasets = await crud_datasets.list_datasets(db, limit=limit, offset=offset)
    return datasets


@router.get(
    "/{dataset_id}",
    response_model=DatasetRead,
    summary="Get a specific dataset",
    description="Get detailed information about a dataset by its ID.",
    response_description="The dataset's full information including metadata and embedding",
    responses={
        404: {"description": "Dataset not found"},
    },
)
async def get_dataset(
    dataset_id: str = Path(..., description="The UUID of the dataset to retrieve"),
    db: AsyncSession = Depends(get_session),
):
    dataset = await crud_datasets.get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.put("/{dataset_id}", response_model=DatasetRead)
async def update_dataset(dataset_id: str, update: dict, db: AsyncSession = Depends(get_session)):
    dataset = await crud_datasets.update_dataset(db, dataset_id, update)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, db: AsyncSession = Depends(get_session)):
    ok = await crud_datasets.delete_dataset(db, dataset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"deleted": True}


@router.post(
    "/search/embedding",
    response_model=DatasetSearchResult,
    summary="Search datasets by semantic similarity",
    description="""
    Find datasets similar to a text query using vector similarity search.
    
    The query text is converted to an embedding vector using the same model
    as dataset embeddings (Gemini). Then cosine similarity is computed between
    the query vector and all dataset vectors to find the most similar matches.
    
    Results are sorted by similarity score (highest first).
    """,
    response_description="List of datasets ordered by similarity to query",
)
async def search_by_embedding(
    query: DatasetSearchQuery = Body(..., description="Search parameters"),
    db: AsyncSession = Depends(get_session),
):
    emb = await generate_embedding(query.query)

    # Fetch datasets with embeddings and compute cosine similarity in Python (fallback when pgvector ops aren't used)
    result = await db.execute("SELECT id, title, description, embedding FROM datasets WHERE embedding IS NOT NULL")
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
        if emb_db is None:
            continue
        # Coerce embedding types (pgvector.Vector, memoryview, list, tuple) to Python list
        def coerce_embedding(v):
            if v is None:
                return None
            if isinstance(v, list):
                return v
            if isinstance(v, tuple):
                return list(v)
            # Some pgvector or driver types are iterable
            try:
                return list(v)
            except Exception:
                # Try common attribute names
                if hasattr(v, "embedding"):
                    try:
                        return list(v.embedding)
                    except Exception:
                        pass
                if hasattr(v, "vec"):
                    try:
                        return list(v.vec)
                    except Exception:
                        pass
                return None

        emb_db_list = coerce_embedding(emb_db)
        if emb_db_list is None:
            continue
        score = cosine(emb, emb_db_list)
        scored.append({"id": r[0], "title": r[1], "description": r[2], "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"results": scored[:query.top_k]}
