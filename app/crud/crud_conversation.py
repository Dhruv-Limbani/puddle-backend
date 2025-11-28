from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.models import Conversation
from app.schemas.conversation import ConversationCreate, ConversationRead

async def create_conversation(db: AsyncSession, conversation_in: Union[ConversationCreate, dict]) -> ConversationRead:
    if isinstance(conversation_in, dict):
        conversation_in = ConversationCreate(**conversation_in)

    conversation = Conversation(**conversation_in.model_dump())
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return ConversationRead.model_validate(conversation)

async def get_conversation(db: AsyncSession, conversation_id: UUID) -> Optional[ConversationRead]:
    conversation = await db.get(Conversation, conversation_id)
    if conversation:
        return ConversationRead.model_validate(conversation)
    return None

async def list_conversations(
    db: AsyncSession, *, user_id: UUID, limit: int = 100, offset: int = 0
) -> List[ConversationRead]:
    query = select(Conversation).where(Conversation.user_id == user_id).limit(limit).offset(offset)
    result = await db.execute(query)
    conversations = result.scalars().all()
    return [ConversationRead.model_validate(c) for c in conversations]

async def update_conversation(db: AsyncSession, conversation_id: UUID, update_data: dict) -> Optional[ConversationRead]:
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        return None

    for key, value in update_data.items():
        if hasattr(conversation, key):
            setattr(conversation, key, value)

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return ConversationRead.model_validate(conversation)

async def delete_conversation(db: AsyncSession, conversation_id: UUID) -> bool:
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        return False

    await db.delete(conversation)
    await db.commit()
    return True
