from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.models import ChatMessage
from app.schemas.chat_message import ChatMessageCreate, ChatMessageRead

async def create_chat_message(db: AsyncSession, message_in: Union[ChatMessageCreate, dict]) -> ChatMessageRead:
    if isinstance(message_in, dict):
        message_in = ChatMessageCreate(**message_in)

    message = ChatMessage(**message_in.model_dump())
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return ChatMessageRead.model_validate(message)

async def list_chat_messages(
    db: AsyncSession, *, conversation_id: UUID, limit: int = 100, offset: int = 0
) -> List[ChatMessageRead]:
    query = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id).order_by(ChatMessage.created_at).limit(limit).offset(offset)
    result = await db.execute(query)
    messages = result.scalars().all()
    return [ChatMessageRead.model_validate(m) for m in messages]
