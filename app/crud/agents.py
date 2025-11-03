from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import AIAgent
from app.schemas.agent import AgentCreate


async def create_agent(db: AsyncSession, agent_in: AgentCreate) -> AIAgent:
    agent = AIAgent(**agent_in.dict())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def get_agent(db: AsyncSession, agent_id: str) -> Optional[AIAgent]:
    result = await db.execute(select(AIAgent).where(AIAgent.id == agent_id))
    return result.scalars().first()


async def list_agents(db: AsyncSession, *, vendor_id: Optional[str] = None, active: Optional[bool] = None, limit: int = 100, offset: int = 0) -> List[AIAgent]:
    q = select(AIAgent)
    if vendor_id:
        q = q.where(AIAgent.vendor_id == vendor_id)
    if active is not None:
        q = q.where(AIAgent.active == active)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


async def update_agent(db: AsyncSession, agent_id: str, update_data: dict) -> Optional[AIAgent]:
    agent = await get_agent(db, agent_id)
    if not agent:
        return None
    for key, value in update_data.items():
        if key in ("id", "created_at"):
            continue
        if hasattr(agent, key):
            setattr(agent, key, value)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def delete_agent(db: AsyncSession, agent_id: str) -> bool:
    agent = await get_agent(db, agent_id)
    if not agent:
        return False
    await db.delete(agent)
    await db.commit()
    return True
