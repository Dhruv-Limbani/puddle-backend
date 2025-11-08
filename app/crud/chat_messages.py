from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import ChatMessage
from app.schemas.chat_message import ChatMessageCreate, ChatMessageRead


# =============================
# CREATE CHAT MESSAGE
# =============================
async def create_chat_message(
    db: AsyncSession, message_in: Union[ChatMessageCreate, dict]
) -> ChatMessageRead:
    if isinstance(message_in, dict):
        message_in = ChatMessageCreate(**message_in)

    message = ChatMessage(**message_in.model_dump())
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return ChatMessageRead.model_validate(message)


# =============================
# GET MESSAGE (ORM object)
# =============================
async def get_chat_message_obj(db: AsyncSession, message_id: int) -> Optional[ChatMessage]:
    """Return ORM object, not Pydantic model."""
    return await db.get(ChatMessage, message_id)


# =============================
# LIST MESSAGES
# =============================
async def list_chat_messages(
    db: AsyncSession,
    chat_id: Optional[str] = None,
    sender_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[ChatMessageRead]:
    query = select(ChatMessage)
    if chat_id:
        query = query.where(ChatMessage.chat_id == chat_id)
    if sender_type:
        query = query.where(ChatMessage.sender_type == sender_type)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    messages = result.scalars().all()
    return [ChatMessageRead.model_validate(m) for m in messages]


# =============================
# UPDATE MESSAGE
# =============================
async def update_chat_message(
    db: AsyncSession, message_id: int, update_data: dict
) -> Optional[ChatMessageRead]:
    message = await db.get(ChatMessage, message_id)
    if not message:
        return None

    for key in ("message", "message_metadata"):
        if key in update_data:
            setattr(message, key, update_data[key])

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return ChatMessageRead.model_validate(message)


# =============================
# DELETE MESSAGE
# =============================
async def delete_chat_message(db: AsyncSession, message_id: int) -> bool:
    message = await db.get(ChatMessage, message_id)
    if not message:
        return False

    await db.delete(message)
    await db.commit()
    return True
