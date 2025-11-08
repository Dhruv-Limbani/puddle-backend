from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_session
from app.core.auth import get_current_user
from app.crud import chats as crud_chats
from app.schemas.chat import ChatCreate, ChatRead
from app.schemas.user import UserRead
from app.models.models import Chat, Vendor

router = APIRouter(prefix="/chats", tags=["chats"])


# =============================
# HELPER: VERIFY USER ACCESS
# =============================
async def verify_chat_access(chat: Chat, current_user: UserRead):
    """
    Check if current user can access this chat.
    - Admin: full access
    - Vendor: can access only their vendor_id chats
    - Buyer/User: can access only their user_id chats
    """
    if current_user.role == "admin":
        return True

    if current_user.role == "vendor":
        if chat.vendor_id != getattr(current_user.vendor_profile, "id", None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this chat.",
            )
        return True

    # Buyers or general users
    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this chat.",
        )

    return True


# =============================
# CREATE CHAT
# =============================
@router.post("/", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_in: ChatCreate,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Create a new chat.
    RBAC:
    - Users can create their own chats
    - Vendors can create chats under their vendor_id
    """
    # Enforce ownership: user_id must match current_user.id unless admin
    if current_user.role != "admin" and str(chat_in.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create chat for another user.",
        )

    # Vendors cannot create chats for other vendors
    if current_user.role == "vendor" and chat_in.vendor_id:
        if str(chat_in.vendor_id) != str(current_user.vendor_profile.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create chat for another vendor.",
            )

    chat = await crud_chats.create_chat(db, chat_in)
    return chat


# =============================
# GET CHAT BY ID
# =============================
@router.get("/{chat_id}", response_model=ChatRead)
async def get_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    chat = await crud_chats.get_chat(db, str(chat_id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    await verify_chat_access(chat.model_copy(), current_user)
    return chat


# =============================
# LIST CHATS
# =============================
@router.get("/", response_model=List[ChatRead])
async def list_chats(
    user_id: Optional[UUID] = None,
    vendor_id: Optional[UUID] = None,
    agent_id: Optional[UUID] = None,
    chat_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    List chats with optional filters.
    RBAC:
    - Admin: can list all
    - Vendor: can list only their vendor_id chats
    - User/Buyer: can list only their own user_id chats
    """
    # Enforce RBAC filters automatically
    if current_user.role == "vendor":
        vendor_id = getattr(current_user.vendor_profile, "id", None)
    elif current_user.role != "admin":
        user_id = current_user.id

    chats = await crud_chats.list_chats(
        db=db,
        user_id=str(user_id) if user_id else None,
        vendor_id=str(vendor_id) if vendor_id else None,
        agent_id=str(agent_id) if agent_id else None,
        chat_type=chat_type,
        limit=limit,
        offset=offset,
        include_inactive=include_inactive,
    )
    return chats


# =============================
# UPDATE CHAT
# =============================
@router.put("/{chat_id}", response_model=ChatRead)
async def update_chat(
    chat_id: UUID,
    update_data: dict,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    chat_obj = await crud_chats.get_chat(db, str(chat_id))
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found")

    await verify_chat_access(chat_obj.model_copy(), current_user)

    updated_chat = await crud_chats.update_chat(db, str(chat_id), update_data)
    return updated_chat


# =============================
# DELETE CHAT
# =============================
@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    chat_obj = await crud_chats.get_chat(db, str(chat_id))
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found")

    await verify_chat_access(chat_obj.model_copy(), current_user)

    success = await crud_chats.delete_chat(db, str(chat_id))
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete chat")

    return None
