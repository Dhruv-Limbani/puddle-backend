from typing import List, Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.auth import get_current_user
from app.schemas.agent import AgentCreate, AgentRead
from app.crud import agents as crud_agents
from app.crud import vendors as crud_vendors
from app.schemas.user import UserRead

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Agent not found"}},
)

# =========================================================
# CREATE NEW AI AGENT (Admin or Vendor)
# =========================================================
@router.post(
    "/",
    response_model=AgentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new AI agent",
)
async def create_agent(
    agent_in: AgentCreate = Body(...),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """Create a new AI agent (Admin or Vendor only)."""
    if current_user.role not in {"admin", "vendor"}:
        raise HTTPException(status_code=403, detail="Only admins or vendors can create agents")

    if current_user.role == "vendor":
        vendor = await crud_vendors.get_vendor_by_user_id(db, current_user.id)
        if not vendor:
            raise HTTPException(status_code=400, detail="Vendor profile not found")
        if str(agent_in.vendor_id) != str(vendor.id):
            raise HTTPException(status_code=403, detail="Vendors can only create agents for their own vendor profile")
    else:
        vendor_exists = await crud_vendors.get_vendor(db, str(agent_in.vendor_id))
        if not vendor_exists:
            raise HTTPException(status_code=400, detail="Vendor not found for provided vendor_id")

    agent = await crud_agents.create_agent(db, agent_in)
    return agent


# =========================================================
# LIST AGENTS
# =========================================================
@router.get(
    "/",
    response_model=List[AgentRead],
    summary="List AI agents",
)
async def list_agents(
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor ID"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, description="Max number of agents", ge=1, le=1000),
    offset: int = Query(0, description="Number of agents to skip", ge=0),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    - Admin: list all agents.
    - Vendor: list only own agents.
    - Buyer: read-only list view of all agents (marketplace discovery).
    """
    if current_user.role == "vendor":
        vendor = await crud_vendors.get_vendor_by_user_id(db, current_user.id)
        if not vendor:
            return []
        vendor_id = vendor.id

    agents = await crud_agents.list_agents(db, vendor_id=vendor_id, active=active, limit=limit, offset=offset)
    return agents


# =========================================================
# GET A SPECIFIC AGENT
# =========================================================
@router.get(
    "/{agent_id}",
    response_model=AgentRead,
    summary="Get a specific AI agent",
)
async def get_agent(
    agent_id: str = Path(..., description="The UUID of the agent"),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    agent = await crud_agents.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Vendors can only view their own agents
    if current_user.role == "vendor" and str(agent.vendor_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this agent")

    return agent


# =========================================================
# UPDATE AN AGENT
# =========================================================
@router.put(
    "/{agent_id}",
    response_model=AgentRead,
    summary="Update an AI agent",
)
async def update_agent(
    agent_id: str,
    update_data: Dict = Body(...),
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """Update an AI agent's configuration (Admin or owning Vendor)."""
    agent = await crud_agents.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if current_user.role == "admin":
        pass
    elif current_user.role == "vendor":
        vendor = await crud_vendors.get_vendor_by_user_id(db, current_user.id)
        if not vendor or str(agent.vendor_id) != str(vendor.id):
            raise HTTPException(status_code=403, detail="Vendors can only update their own agents")
    else:
        raise HTTPException(status_code=403, detail="Only admins or vendors can update agents")

    updated_agent = await crud_agents.update_agent(db, agent_id, update_data)
    return updated_agent


# =========================================================
# DELETE AN AGENT
# =========================================================
@router.delete(
    "/{agent_id}",
    summary="Delete an AI agent",
)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """Delete an AI agent (Admin or owning Vendor)."""
    agent = await crud_agents.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if current_user.role == "admin":
        pass
    elif current_user.role == "vendor":
        vendor = await crud_vendors.get_vendor_by_user_id(db, current_user.id)
        if not vendor or str(agent.vendor_id) != str(vendor.id):
            raise HTTPException(status_code=403, detail="Vendors can only delete their own agents")
    else:
        raise HTTPException(status_code=403, detail="Only admins or vendors can delete agents")

    await crud_agents.delete_agent(db, agent_id)
    return {"deleted": True}
