from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Chat
from app.schemas.chat import ChatCreate, ChatRead


# =============================
# CREATE CHAT
# =============================
async def create_chat(db: AsyncSession, chat_in: Union[ChatCreate, dict]) -> ChatRead:
    if isinstance(chat_in, dict):
        chat_in = ChatCreate(**chat_in)

    chat = Chat(**chat_in.model_dump())
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return ChatRead.model_validate(chat)


# =============================
# GET CHAT (ORM object)
# =============================
async def get_chat_obj(db: AsyncSession, chat_id: str) -> Optional[Chat]:
    """Return ORM object for a chat, regardless of active status."""
    return await db.get(Chat, chat_id)


# =============================
# LIST CHATS
# =============================
async def list_chats(
    db: AsyncSession,
    user_id: Optional[str] = None,
    vendor_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    chat_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    include_inactive: bool = False,
) -> List[ChatRead]:
    query = select(Chat)
    if not include_inactive:
        query = query.where(Chat.is_active == True)
    if user_id:
        query = query.where(Chat.user_id == user_id)
    if vendor_id:
        query = query.where(Chat.vendor_id == vendor_id)
    if agent_id:
        query = query.where(Chat.agent_id == agent_id)
    if chat_type:
        query = query.where(Chat.chat_type == chat_type)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    chats = result.scalars().all()
    return [ChatRead.model_validate(c) for c in chats]


# =============================
# UPDATE CHAT
# =============================
async def update_chat(db: AsyncSession, chat_id: str, update_data: dict) -> Optional[ChatRead]:
    chat = await db.get(Chat, chat_id)
    if not chat or not chat.is_active:
        return None

    for key, value in update_data.items():
        if key in ("id", "created_at"):
            continue
        if hasattr(chat, key):
            setattr(chat, key, value)

    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return ChatRead.model_validate(chat)


# =============================
# SOFT DELETE CHAT
# =============================
async def delete_chat(db: AsyncSession, chat_id: str) -> bool:
    chat = await db.get(Chat, chat_id)
    if not chat or not chat.is_active:
        return False

    chat.is_active = False
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return True
