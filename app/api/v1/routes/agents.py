from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.agent import AgentCreate, AgentRead
from app.crud import agents as crud_agents

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Agent not found"}},
)


@router.post(
    "/",
    response_model=AgentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new AI agent",
    description="""
    Create a new AI agent configuration for dataset processing.
    
    An AI agent can:
    - Process and analyze datasets
    - Generate embeddings and metadata
    - Handle data transformations
    - Compute dataset statistics
    """,
    response_description="The created AI agent configuration",
)
async def create_agent(
    agent_in: AgentCreate = Body(
        ...,
        description="Agent configuration to create",
        example={
            "vendor_id": "uuid-here",
            "name": "Data Embedding Agent",
            "description": "Generates embeddings for dataset search",
            "model_used": "gemini-embedding-001",
            "config": {"batch_size": 32, "compute_stats": True},
        },
    ),
    db: AsyncSession = Depends(get_session),
):
    agent = await crud_agents.create_agent(db, agent_in)
    return agent


@router.get(
    "/",
    response_model=List[AgentRead],
    summary="List AI agents",
    description="""
    Get a paginated list of AI agents. Can be filtered by:
    - Vendor ID (to get all agents for a specific vendor)
    - Active status (to get only active/inactive agents)
    """,
    response_description="List of AI agent configurations",
)
async def get_agents(
    vendor_id: Optional[str] = Query(None, description="Filter agents by vendor ID"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, description="Maximum number of agents to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of agents to skip", ge=0),
    db: AsyncSession = Depends(get_session),
):
    agents = await crud_agents.list_agents(db, vendor_id=vendor_id, active=active, limit=limit, offset=offset)
    return agents


@router.get(
    "/{agent_id}",
    response_model=AgentRead,
    summary="Get a specific AI agent",
    description="Get detailed information about an AI agent by its ID.",
    response_description="The agent's full configuration",
)
async def get_agent(
    agent_id: str = Path(..., description="The UUID of the agent to retrieve"),
    db: AsyncSession = Depends(get_session),
):
    agent = await crud_agents.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put(
    "/{agent_id}",
    response_model=AgentRead,
    summary="Update an AI agent",
    description="""
    Update an AI agent's configuration.
    
    Common updates include:
    - Changing the model or parameters
    - Updating the description
    - Enabling/disabling the agent
    """,
    response_description="The updated agent configuration",
)
async def update_agent(
    agent_id: str = Path(..., description="The UUID of the agent to update"),
    update: Dict = Body(
        ...,
        description="Fields to update",
        example={
            "config": {"batch_size": 64, "compute_stats": True},
            "active": False,
            "description": "Updated agent description",
        },
    ),
    db: AsyncSession = Depends(get_session),
):
    agent = await crud_agents.update_agent(db, agent_id, update)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete(
    "/{agent_id}",
    summary="Delete an AI agent",
    description="Delete an AI agent configuration.",
    responses={
        200: {"description": "Agent successfully deleted"},
        404: {"description": "Agent not found"},
    },
)
async def delete_agent(
    agent_id: str = Path(..., description="The UUID of the agent to delete"),
    db: AsyncSession = Depends(get_session),
):
    ok = await crud_agents.delete_agent(db, agent_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"deleted": True}
