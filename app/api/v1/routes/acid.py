"""
ACID Agent Routes - Buyer-facing AI chat interface

This module provides endpoints for:
- Conversation management
- Chat messages with AI responses
- Inquiry creation and tracking
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID


from app.core.db import get_session
from app.core.auth import get_current_user
from app.schemas.user import UserRead
from app.schemas.conversation import ConversationCreate, ConversationRead, ConversationUpdate
from app.schemas.chat_message import ChatMessageCreate, ChatMessageRead
from app.schemas.inquiry import InquiryCreate, InquiryRead, InquiryUpdate, InquiryReadEnriched
from app.crud import crud_conversation, crud_chat_message, crud_inquiry
from app.models.models import Buyer, Inquiry, Dataset, Vendor

router = APIRouter(prefix="/acid", tags=["acid"])


async def _get_buyer_for_user(db: AsyncSession, user_id: str):
    """Helper to get buyer profile for a user"""
    result = await db.execute(select(Buyer).where(Buyer.user_id == str(user_id)))
    return result.scalars().first()


# ==========================================
# CONVERSATION ENDPOINTS
# ==========================================

@router.post("/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_in: ConversationCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new conversation for the current user.
    Only buyers can create conversations with ACID.
    """
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can chat with ACID")
    
    # Verify user_id matches current user
    if str(conversation_in.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Cannot create conversation for another user")
    
    conversation = await crud_conversation.create_conversation(db, conversation_in)
    return conversation


@router.get("/conversations", response_model=List[ConversationRead])
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List all conversations for the current user.
    """
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can access ACID conversations")
    
    conversations = await crud_conversation.list_conversations(
        db, user_id=current_user.id, limit=limit, offset=offset
    )
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get a specific conversation by ID.
    """
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    return conversation


@router.patch("/conversations/{conversation_id}", response_model=ConversationRead)
async def update_conversation(
    conversation_id: UUID,
    update_in: ConversationUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update a conversation (e.g., change title).
    """
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this conversation")
    
    update_data = update_in.model_dump(exclude_unset=True)
    updated = await crud_conversation.update_conversation(db, conversation_id, update_data)
    return updated

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Delete a conversation owned by the current user.
    """
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this conversation")

    deleted = await crud_conversation.delete_conversation(db, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return None


# ==========================================
# CHAT MESSAGE ENDPOINTS
# ==========================================

@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessageRead])
async def get_conversation_messages(
    conversation_id: UUID,
    limit: int = 100,
    offset: int = 0,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get all messages in a conversation.
    """
    # Verify conversation exists and user owns it
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    messages = await crud_chat_message.list_chat_messages(
        db, conversation_id=conversation_id, limit=limit, offset=offset
    )
    return messages


@router.post("/conversations/{conversation_id}/messages", response_model=Dict[str, Any])
async def send_message(
    conversation_id: UUID,
    message: Dict[str, str],
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Send a message to ACID and get a response.
    
    This endpoint:
    1. Saves the user's message
    2. Reconstructs conversation history properly
    3. Calls the AI engine to process the message
    4. Saves the AI response
    5. Returns both messages
    """
    # Verify conversation exists and user owns it
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Get buyer profile
    buyer = await _get_buyer_for_user(db, current_user.id)
    if not buyer:
        raise HTTPException(status_code=400, detail="Buyer profile not found")
    
    # 1. Save user message
    user_message = await crud_chat_message.create_chat_message(
        db,
        {
            "conversation_id": conversation_id,
            "role": "user",
            "content": message.get("content", ""),
        }
    )
    
    # 2. Get conversation history and rebuild it properly
    all_messages = await crud_chat_message.list_chat_messages(db, conversation_id=conversation_id, limit=50)
    
    # Use the conversation manager to rebuild history with proper tool call format
    from app.core.conversation_manager import rebuild_conversation_history
    history = rebuild_conversation_history(all_messages[:-1])  # Exclude the just-saved user message
    
    # Add current user message
    messages = history + [{"role": "user", "content": message.get("content", "")}]
    
    # 3. Process with AI engine
    from app.core.ai_engine import get_acid_engine, get_acid_system_prompt
    
    try:
        acid = await get_acid_engine()
        
        # Process conversation
        response_data = await acid.process_conversation(
            messages=messages,
            system_prompt=get_acid_system_prompt(),
            context={"buyer_id": str(buyer.id), "conversation_id": str(conversation_id)}
        )
        
        ai_content = response_data.get("content", "I'm having trouble processing that request.")
        tool_calls_list = response_data.get("tool_calls")
        
        # Convert tool_calls format for database
        tool_call_payload = None
        if tool_calls_list:
            tool_call_payload = {
                "calls": tool_calls_list  # Already in correct format: [{name, arguments, result}]
            }
        
    except Exception as e:
        print(f"❌ ACID error: {e}")
        import traceback
        traceback.print_exc()
        ai_content = f"I'm having trouble connecting to my AI systems. Please try again."
        tool_call_payload = None
    
    # 4. Save AI response
    ai_message = await crud_chat_message.create_chat_message(db, {
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": ai_content,
        "tool_call": tool_call_payload,
    })
    
    return {
        "user_message": user_message,
        "ai_message": ai_message,
    }



# ==========================================
# INQUIRY ENDPOINTS
# ==========================================

@router.post("/inquiries", response_model=InquiryRead, status_code=status.HTTP_201_CREATED)
async def create_inquiry(
    inquiry_in: InquiryCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new inquiry.
    This is typically called by ACID through the chat flow.
    """
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can create inquiries")
    
    # Get buyer profile
    buyer = await _get_buyer_for_user(db, current_user.id)
    if not buyer:
        raise HTTPException(status_code=400, detail="Buyer profile not found")
    
    # Verify buyer_id matches
    if str(inquiry_in.buyer_id) != str(buyer.id):
        raise HTTPException(status_code=403, detail="Cannot create inquiry for another buyer")
    
    inquiry = await crud_inquiry.create_inquiry(db, inquiry_in)
    return inquiry


@router.get("/inquiries", response_model=List[InquiryReadEnriched])
async def list_inquiries(
    limit: int = 50,
    offset: int = 0,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List all inquiries for the current buyer.
    """
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can access inquiries")
    
    # Get buyer profile
    buyer = await _get_buyer_for_user(db, current_user.id)
    if not buyer:
        return []
    
    inquiries = await crud_inquiry.list_inquiries_by_buyer(
        db, buyer_id=buyer.id, limit=limit, offset=offset
    )
    # Enrich with dataset title and vendor name
    enriched: List[InquiryReadEnriched] = []
    for i in inquiries:
        dataset_title = None
        vendor_name = None
        try:
            ds = await db.get(Dataset, i.dataset_id)
            if ds:
                dataset_title = ds.title
        except Exception:
            pass
        try:
            v = await db.get(Vendor, i.vendor_id)
            if v:
                vendor_name = v.name
        except Exception:
            pass
        enriched.append(InquiryReadEnriched(**i.model_dump(), dataset_title=dataset_title, vendor_name=vendor_name))
    return enriched


@router.get("/inquiries/{inquiry_id}", response_model=InquiryReadEnriched)
async def get_inquiry(
    inquiry_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get a specific inquiry by ID.
    """
    inquiry = await crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    # Get buyer profile to verify ownership
    buyer = await _get_buyer_for_user(db, current_user.id)
    if not buyer or str(inquiry.buyer_id) != str(buyer.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this inquiry")
    
    # Enrich with dataset title and vendor name
    dataset_title = None
    vendor_name = None
    try:
        ds = await db.get(Dataset, inquiry.dataset_id)
        if ds:
            dataset_title = ds.title
    except Exception:
        pass
    try:
        v = await db.get(Vendor, inquiry.vendor_id)
        if v:
            vendor_name = v.name
    except Exception:
        pass
    return InquiryReadEnriched(**inquiry.model_dump(), dataset_title=dataset_title, vendor_name=vendor_name)


@router.patch("/inquiries/{inquiry_id}", response_model=InquiryRead)
async def update_inquiry(
    inquiry_id: UUID,
    update_in: InquiryUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update an inquiry (e.g., update buyer_inquiry JSON or status).
    """
    inquiry = await crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    # Get buyer profile to verify ownership
    buyer = await _get_buyer_for_user(db, current_user.id)
    if not buyer or str(inquiry.buyer_id) != str(buyer.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this inquiry")
    
    update_data = update_in.model_dump(exclude_unset=True)
    updated = await crud_inquiry.update_inquiry(db, inquiry_id, update_data)
    return updated


@router.get("/conversations/{conversation_id}/inquiries", response_model=List[InquiryReadEnriched])
async def get_conversation_inquiries(
    conversation_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get all inquiries associated with a conversation.
    Useful for the frontend to show inquiry status in the chat.
    """
    # Verify conversation exists and user owns it
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Query inquiries for this conversation
    result = await db.execute(
        select(Inquiry).where(Inquiry.conversation_id == str(conversation_id))
    )
    inquiries = result.scalars().all()

    enriched: List[InquiryReadEnriched] = []
    for i in inquiries:
        base = InquiryRead.model_validate(i)
        dataset_title = None
        vendor_name = None
        try:
            ds = await db.get(Dataset, base.dataset_id)
            if ds:
                dataset_title = ds.title
        except Exception:
            pass
        try:
            v = await db.get(Vendor, base.vendor_id)
            if v:
                vendor_name = v.name
        except Exception:
            pass
        enriched.append(InquiryReadEnriched(**base.model_dump(), dataset_title=dataset_title, vendor_name=vendor_name))
    return enriched
