from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import AIAgent
from app.schemas.agent import AgentCreate, AgentRead


async def create_agent(db: AsyncSession, agent_in: AgentCreate) -> AgentRead:
    """Create a new AI agent."""
    agent = AIAgent(**agent_in.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return AgentRead.model_validate(agent)


async def get_agent(db: AsyncSession, agent_id: str) -> Optional[AIAgent]:
    """Fetch an AI agent ORM object by ID."""
    result = await db.execute(select(AIAgent).where(AIAgent.id == agent_id))
    agent = result.scalars().first()
    return agent


async def list_agents(
    db: AsyncSession,
    *,
    vendor_id: Optional[str] = None,
    active: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[AgentRead]:
    """List AI agents with optional filters."""
    q = select(AIAgent)
    if vendor_id:
        q = q.where(AIAgent.vendor_id == vendor_id)
    if active is not None:
        q = q.where(AIAgent.active == active)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    agents = result.scalars().all()
    return [AgentRead.model_validate(a) for a in agents]


async def update_agent(db: AsyncSession, agent_id: str, update_data: dict) -> Optional[AgentRead]:
    """Update an AI agent by ID."""
    agent = await get_agent(db, agent_id)
    if not agent:
        return None

    # Update attributes safely
    for key, value in update_data.items():
        if key in ("id", "created_at"):
            continue
        if hasattr(agent, key):
            setattr(agent, key, value)

    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return AgentRead.model_validate(agent)


async def delete_agent(db: AsyncSession, agent_id: str) -> bool:
    """Delete an AI agent by ID."""
    agent = await get_agent(db, agent_id)
    if not agent:
        return False
    await db.delete(agent)
    await db.commit()
    return True
