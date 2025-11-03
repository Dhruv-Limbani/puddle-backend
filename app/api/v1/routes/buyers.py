from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.buyer import BuyerCreate, BuyerRead
from app.crud import buyers as crud_buyers

router = APIRouter(
    prefix="/buyers",
    tags=["buyers"],
    responses={404: {"description": "Buyer not found"}},
)


@router.post(
    "/",
    response_model=BuyerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new buyer",
    description="""
    Create a new dataset buyer/consumer profile in the marketplace.
    
    A buyer can:
    - Browse and search datasets
    - View dataset details and samples
    - Track use cases and requirements
    """,
    response_description="The created buyer profile",
)
async def create_buyer(
    buyer_in: BuyerCreate = Body(
        ...,
        description="Buyer details to create",
        example={
            "name": "John Smith",
            "organization": "AI Research Labs",
            "contact_email": "john@airesearch.com",
            "industry": "Technology",
            "use_case_focus": "Machine Learning Model Training",
        },
    ),
    db: AsyncSession = Depends(get_session),
):
    buyer = await crud_buyers.create_buyer(db, buyer_in)
    return buyer


@router.get(
    "/",
    response_model=List[BuyerRead],
    summary="List all buyers",
    description="Get a paginated list of all dataset buyers/consumers.",
    response_description="List of buyer profiles",
)
async def get_buyers(
    limit: int = Query(100, description="Maximum number of buyers to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of buyers to skip", ge=0),
    db: AsyncSession = Depends(get_session),
):
    buyers = await crud_buyers.list_buyers(db, limit=limit, offset=offset)
    return buyers


@router.get(
    "/{buyer_id}",
    response_model=BuyerRead,
    summary="Get a specific buyer",
    description="Get detailed information about a buyer by their ID.",
    response_description="The buyer's full profile information",
)
async def get_buyer(
    buyer_id: str = Path(..., description="The UUID of the buyer to retrieve"),
    db: AsyncSession = Depends(get_session),
):
    buyer = await crud_buyers.get_buyer(db, buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return buyer


@router.put(
    "/{buyer_id}",
    response_model=BuyerRead,
    summary="Update a buyer",
    description="Update a buyer's profile information.",
    response_description="The updated buyer profile",
)
async def update_buyer(
    buyer_id: str = Path(..., description="The UUID of the buyer to update"),
    update: Dict = Body(
        ...,
        description="Fields to update",
        example={
            "organization": "New Organization Name",
            "use_case_focus": "Updated use case description",
        },
    ),
    db: AsyncSession = Depends(get_session),
):
    buyer = await crud_buyers.update_buyer(db, buyer_id, update)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return buyer


@router.delete(
    "/{buyer_id}",
    summary="Delete a buyer",
    description="Delete a buyer's profile from the marketplace.",
    responses={
        200: {"description": "Buyer successfully deleted"},
        404: {"description": "Buyer not found"},
    },
)
async def delete_buyer(
    buyer_id: str = Path(..., description="The UUID of the buyer to delete"),
    db: AsyncSession = Depends(get_session),
):
    ok = await crud_buyers.delete_buyer(db, buyer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return {"deleted": True}
