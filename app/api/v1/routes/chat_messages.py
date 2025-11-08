from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_session
from app.core.auth import get_current_user
from app.crud import chat_messages as chat_crud
from app.schemas.chat_message import ChatMessageCreate, ChatMessageRead
from app.schemas.user import UserRead
from app.models.models import Chat

router = APIRouter(prefix="/chat-messages", tags=["chat-messages"])


# =========================================================
# CREATE NEW CHAT MESSAGE
# =========================================================
@router.post("/", response_model=ChatMessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_in: ChatMessageCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new chat message. The current user is the sender.
    """
    chat_obj = await db.get(Chat, str(message_in.chat_id))
    if not chat_obj or (chat_obj.user_id != current_user.id and chat_obj.vendor_id != current_user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this chat")

    return await chat_crud.create_chat_message(db, message_in)


# =========================================================
# GET CHAT MESSAGE BY ID
# =========================================================
@router.get("/{message_id}", response_model=ChatMessageRead)
async def get_message(
    message_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Retrieve a single chat message by its ID.
    Only participants of the chat can access it.
    """
    message = await chat_crud.get_chat_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    chat_obj = await db.get(Chat, message.chat_id)
    if not chat_obj or (chat_obj.user_id != current_user.id and chat_obj.vendor_id != current_user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this chat")

    return message


# =========================================================
# LIST MESSAGES (OPTIONAL FILTERING, SORTED LATEST FIRST)
# =========================================================
@router.get("/", response_model=List[ChatMessageRead])
async def list_messages(
    chat_id: Optional[UUID] = Query(None, description="Filter messages by chat ID"),
    sender_type: Optional[str] = Query(None, description="Filter messages by sender type"),
    limit: int = Query(100, ge=1, le=500, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    include_metadata: bool = Query(True, description="Include message_metadata field"),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List chat messages with optional filtering by chat_id or sender_type.
    - Sorted by created_at descending (latest first)
    - RBAC enforced: user must be participant in chat.
    """
    if chat_id:
        chat_obj = await db.get(Chat, str(chat_id))
        if not chat_obj or (chat_obj.user_id != current_user.id and chat_obj.vendor_id != current_user.id):
            raise HTTPException(status_code=403, detail="You do not have access to this chat")

    messages = await chat_crud.list_chat_messages(
        db,
        chat_id=str(chat_id) if chat_id else None,
        sender_type=sender_type,
        limit=limit,
        offset=offset,
    )

    if not include_metadata:
        # Strip metadata from response for lightweight payload
        for msg in messages:
            msg.message_metadata = None

    # Sort messages by created_at descending
    messages.sort(key=lambda x: x.created_at or 0, reverse=True)
    return messages


# =========================================================
# LIST MESSAGES BY CHAT
# =========================================================
@router.get("/by-chat/{chat_id}", response_model=List[ChatMessageRead])
async def list_messages_by_chat(
    chat_id: UUID,
    limit: int = Query(50, ge=1, le=200, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    include_metadata: bool = Query(True, description="Include message_metadata field"),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List all messages for a specific chat, sorted by creation time (latest first).
    - RBAC enforced: only participants of the chat can view.
    - Supports pagination via limit and offset.
    """
    chat_obj = await db.get(Chat, str(chat_id))
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat_obj.user_id != current_user.id and chat_obj.vendor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this chat")

    messages = await chat_crud.list_chat_messages(
        db, chat_id=str(chat_id), limit=limit, offset=offset
    )

    if not include_metadata:
        for msg in messages:
            msg.message_metadata = None

    messages.sort(key=lambda x: x.created_at or 0, reverse=True)
    return messages


# =========================================================
# UPDATE CHAT MESSAGE
# =========================================================
@router.patch("/{message_id}", response_model=ChatMessageRead)
async def update_message(
    message_id: int,
    update_data: dict,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update a chat message. Only 'message' and 'message_metadata' are updatable.
    Only the sender of the message can update it.
    """
    message = await chat_crud.get_chat_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    if message.sender_type == "user" and str(message.chat.user_id) != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this message")

    updated_message = await chat_crud.update_chat_message(db, message_id, update_data)
    return updated_message


# =========================================================
# DELETE CHAT MESSAGE
# =========================================================
@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Permanently delete a chat message by ID.
    Only the sender or an admin can delete messages.
    """
    message = await chat_crud.get_chat_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    if message.sender_type == "user" and str(message.chat.user_id) != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to delete this message")

    deleted = await chat_crud.delete_chat_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete message")
    return
