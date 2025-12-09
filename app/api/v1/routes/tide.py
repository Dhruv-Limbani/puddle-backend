"""
TIDE Agent Routes - Vendor-facing AI assistant

This module provides endpoints for:
 Vendor inquiry management
 AI-powered inquiry summarization
 Vendor response handling
 Vendor chat with TIDE
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
import json

from app.core.db import get_session
from app.core.auth import get_current_user
from app.schemas.user import UserRead
from app.schemas.conversation import ConversationCreate, ConversationRead, ConversationUpdate
from app.schemas.chat_message import ChatMessageCreate, ChatMessageRead
from app.schemas.inquiry import InquiryCreate, InquiryRead, InquiryUpdate, InquiryReadEnriched
from app.crud import crud_conversation, crud_chat_message, crud_inquiry
from app.models.models import Vendor, Inquiry, Dataset, Buyer

router = APIRouter(prefix="/tide", tags=["tide"])


# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def _get_vendor_for_user(db: AsyncSession, user_id: str) -> Optional[Vendor]:
    """Helper to get vendor profile for a user"""
    result = await db.execute(select(Vendor).where(Vendor.user_id == str(user_id)))
    return result.scalars().first()


async def _verify_vendor_access(
    db: AsyncSession, 
    current_user: UserRead
) -> Vendor:
    """Verify user is a vendor and return vendor profile"""
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only vendors can access TIDE"
        )
    
    vendor = await _get_vendor_for_user(db, current_user.id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Vendor profile not found"
        )
    
    return vendor

# ==========================================
# PYDANTIC SCHEMAS FOR TIDE
# ==========================================

class VendorResponseInput(BaseModel):
    """Schema for vendor response to an inquiry"""
    action: str  # 'approve', 'reject', 'request_info'
    final_price: Optional[float] = None
    currency: str = "USD"
    terms: Optional[str] = None
    notes: Optional[str] = None
    valid_until: Optional[str] = None  # ISO date string


class InquiryDetailResponse(BaseModel):
    """Detailed inquiry response including related data"""
    inquiry: InquiryRead
    dataset: Optional[Dict[str, Any]] = None
    buyer_info: Optional[Dict[str, Any]] = None


class InquirySummaryResponse(BaseModel):
    """AI-generated inquiry summary response"""
    inquiry_id: str
    summary: str
    dataset_title: Optional[str] = None
    status: str
    buyer_requirements: Optional[Dict[str, Any]] = None
# ==========================================
# INQUIRY ENDPOINTS (Vendor View)
# ==========================================

@router.get("/inquiries", response_model=List[InquiryReadEnriched])
async def list_vendor_inquiries(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List all inquiries for the current vendor with enriched data.
    
    Returns inquiries with buyer_name and dataset_title resolved.
    """
    vendor = await _verify_vendor_access(db, current_user)
    
    query = select(
        Inquiry,
        Dataset.title.label('dataset_title'),
        Buyer.name.label('buyer_name')
    ).join(
        Dataset, Inquiry.dataset_id == Dataset.id
    ).join(
        Buyer, Inquiry.buyer_id == Buyer.id
    ).where(
        Inquiry.vendor_id == vendor.id
    ).order_by(
        Inquiry.created_at.desc()
    ).limit(limit).offset(offset)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Build enriched response
    enriched_inquiries = []
    for row in rows:
        inquiry = row[0]
        # Create enriched inquiry with explicit field mapping
        enriched = InquiryReadEnriched(
            id=inquiry.id,
            buyer_id=inquiry.buyer_id,
            vendor_id=inquiry.vendor_id,
            dataset_id=inquiry.dataset_id,
            conversation_id=inquiry.conversation_id,
            buyer_inquiry=inquiry.buyer_inquiry,
            vendor_response=inquiry.vendor_response,
            summary=inquiry.summary,
            status=inquiry.status,
            created_at=inquiry.created_at,
            updated_at=inquiry.updated_at,
            dataset_title=row[1],
            buyer_name=row[2],
            vendor_name=None  # Not needed for vendor view
        )
        enriched_inquiries.append(enriched)
    
    # Filter by status if provided
    if status_filter:
        enriched_inquiries = [i for i in enriched_inquiries if i.status == status_filter]
    
    return enriched_inquiries


@router.get("/inquiries/pending", response_model=List[InquiryRead])
async def list_pending_inquiries(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List inquiries that need vendor review.
    These are inquiries with status 'submitted'.
    
    This is the primary endpoint for vendors to see what needs attention.
    """
    vendor = await _verify_vendor_access(db, current_user)
    
    # Get all vendor inquiries
    all_inquiries = await crud_inquiry.list_inquiries_by_vendor(
        db, vendor_id=vendor.id, limit=100, offset=0
    )
    
    # Filter for pending ones
    pending = [i for i in all_inquiries if i.status == 'submitted']
    
    return pending


@router.get("/inquiries/stats", response_model=Dict[str, int])
async def get_inquiry_stats(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get count of inquiries by status for the vendor dashboard.
    """
    vendor = await _verify_vendor_access(db, current_user)
    
    all_inquiries = await crud_inquiry.list_inquiries_by_vendor(
        db, vendor_id=vendor.id, limit=1000, offset=0
    )
    
    stats = {
        "total": len(all_inquiries),
        "pending": len([i for i in all_inquiries if i.status == 'submitted']),
        "responded": len([i for i in all_inquiries if i.status == 'responded']),
        "accepted": len([i for i in all_inquiries if i.status == 'accepted']),
        "rejected": len([i for i in all_inquiries if i.status == 'rejected']),
    }
    
    return stats


@router.get("/inquiries/{inquiry_id}", response_model=InquiryDetailResponse)
async def get_inquiry_details(
    inquiry_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get detailed information about an inquiry including:
    - Full inquiry data
    - Dataset information
    - Buyer information (limited for privacy)
    """
    vendor = await _verify_vendor_access(db, current_user)
    inquiry = await crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry or str(inquiry.vendor_id) != str(vendor.id):
        raise HTTPException(status_code=404, detail="Inquiry not found for this vendor")
    
    # Get dataset details
    dataset = await db.get(Dataset, inquiry.dataset_id)
    dataset_info = None
    if dataset:
        dataset_info = {
            "id": str(dataset.id),
            "title": dataset.title,
            "description": dataset.description,
            "domain": dataset.domain,
            "pricing_model": dataset.pricing_model,
            "license": dataset.license,
            "dataset_type": dataset.dataset_type,
        }
    
    # Get buyer info (limited)
    buyer = await db.get(Buyer, inquiry.buyer_id)
    buyer_info = None
    if buyer:
        buyer_info = {
            "id": str(buyer.id),
            "name": buyer.name,
            "organization": buyer.organization,
            "industry": buyer.industry,
            "use_case_focus": buyer.use_case_focus,
        }
    
    return InquiryDetailResponse(
        inquiry=inquiry,
        dataset=dataset_info,
        buyer_info=buyer_info
    )


# ==========================================
# VENDOR RESPONSE ENDPOINTS
# ==========================================

@router.patch("/inquiries/{inquiry_id}/respond", response_model=InquiryRead)
async def respond_to_inquiry(
    inquiry_id: UUID,
    response_in: VendorResponseInput,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Vendor responds to an inquiry.
    
    Actions:
    - 'approve': Accept the inquiry and provide final pricing
    - 'reject': Decline the inquiry
    - 'request_info': Ask buyer for more information
    
    For 'approve' action, final_price is required.
    """
    vendor = await _verify_vendor_access(db, current_user)
    inquiry = await crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry or str(inquiry.vendor_id) != str(vendor.id):
        raise HTTPException(status_code=404, detail="Inquiry not found for this vendor")
    
    # Build vendor_response JSON
    vendor_response = {
        "action": response_in.action,
        "responded_at": datetime.utcnow().isoformat(),
        "responded_by": current_user.full_name or current_user.email,
    }
    
    if response_in.action == "approve":
        if not response_in.final_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="final_price is required for approval"
            )
        vendor_response["final_price"] = response_in.final_price
        vendor_response["currency"] = response_in.currency
        vendor_response["terms"] = response_in.terms
        vendor_response["valid_until"] = response_in.valid_until
        if response_in.notes:
            vendor_response["notes"] = response_in.notes
        new_status = "responded"
        
    elif response_in.action == "reject":
        vendor_response["rejection_reason"] = response_in.notes
        new_status = "rejected"
        
    elif response_in.action == "request_info":
        if not response_in.notes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="notes field is required when requesting more information"
            )
        vendor_response["info_requested"] = response_in.notes
        new_status = "submitted"  # Keep as submitted until buyer responds
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid action. Must be 'approve', 'reject', or 'request_info'"
        )
    
    # Update the inquiry
    update_data = {
        "vendor_response": vendor_response,
        "status": new_status
    }
    
    updated = await crud_inquiry.update_inquiry(db, inquiry_id, update_data)
    return updated


@router.patch("/inquiries/{inquiry_id}/status", response_model=InquiryRead)
async def update_inquiry_status(
    inquiry_id: UUID,
    new_status: str,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update inquiry status manually.
    
    Allowed statuses for vendor:
    - submitted: Mark as submitted (awaiting response)
    - responded: Mark as responded (usually done via /respond endpoint)
    - rejected: Mark as rejected
    """
    vendor = await _verify_vendor_access(db, current_user)
    inquiry = await crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry or str(inquiry.vendor_id) != str(vendor.id):
        raise HTTPException(status_code=404, detail="Inquiry not found for this vendor")
    
    allowed_statuses = ['submitted', 'responded', 'rejected']
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Status must be one of: {allowed_statuses}"
        )
    
    updated = await crud_inquiry.update_inquiry(db, inquiry_id, {"status": new_status})
    return updated


# ==========================================
# AI SUMMARY ENDPOINT
# ==========================================

@router.post("/inquiries/{inquiry_id}/summary", response_model=InquirySummaryResponse)
async def generate_inquiry_summary(
    inquiry_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Generate an AI summary of the inquiry for the vendor.
    
    This helps vendors quickly understand:
    - What the buyer is requesting
    - Key requirements and use case
    - Recommended next steps
    """
    vendor = await _verify_vendor_access(db, current_user)
    inquiry = await crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry or str(inquiry.vendor_id) != str(vendor.id):
        raise HTTPException(status_code=404, detail="Inquiry not found for this vendor")
    
    # Get dataset info
    dataset = await db.get(Dataset, inquiry.dataset_id)
    
    # Get buyer info
    buyer = await db.get(Buyer, inquiry.buyer_id)
    
    # Build context for AI
    context = {
        "dataset_title": dataset.title if dataset else "Unknown",
        "dataset_description": dataset.description if dataset else "N/A",
        "dataset_domain": dataset.domain if dataset else "N/A",
        "dataset_pricing_model": dataset.pricing_model if dataset else "N/A",
        "buyer_organization": buyer.organization if buyer else "Unknown",
        "buyer_industry": buyer.industry if buyer else "N/A",
        "buyer_use_case": buyer.use_case_focus if buyer else "N/A",
        "buyer_inquiry": inquiry.buyer_inquiry if inquiry.buyer_inquiry else {},
    }
    
    # Generate summary via service
    from app.services.inquiry_service import generate_inquiry_summary as svc_generate_summary
    try:
        res = await svc_generate_summary(db, inquiry_id)
        return InquirySummaryResponse(
            inquiry_id=res["inquiry_id"],
            summary=res["summary"],
            dataset_title=res.get("dataset_title"),
            status=res.get("status", inquiry.status),
            buyer_requirements=res.get("buyer_requirements"),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate summary: {str(e)}")


# ==========================================
# CONVERSATION ENDPOINTS (Chat with TIDE)
# ==========================================

@router.post("/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
async def create_tide_conversation(
    conversation_in: ConversationCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new conversation with TIDE for the vendor.
    """
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only vendors can chat with TIDE"
        )
    
    if str(conversation_in.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot create conversation for another user"
        )
    
    conversation = await crud_conversation.create_conversation(db, conversation_in)
    return conversation


@router.get("/conversations", response_model=List[ConversationRead])
async def list_tide_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List all TIDE conversations for the current vendor.
    """
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only vendors can access TIDE conversations"
        )
    
    conversations = await crud_conversation.list_conversations(
        db, user_id=current_user.id, limit=limit, offset=offset
    )
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
async def get_tide_conversation(
    conversation_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get a specific TIDE conversation by ID.
    """
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only vendors can access TIDE conversations"
        )
    
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversation not found"
        )
    
    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this conversation"
        )
    
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessageRead])
async def get_tide_conversation_messages(
    conversation_id: UUID,
    limit: int = 100,
    offset: int = 0,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get all messages in a TIDE conversation.
    """
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only vendors can access TIDE conversations"
        )
    
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversation not found"
        )
    
    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this conversation"
        )
    
    messages = await crud_chat_message.list_chat_messages(
        db, conversation_id=conversation_id, limit=limit, offset=offset
    )
    return messages


@router.post("/conversations/{conversation_id}/messages", response_model=Dict[str, Any])
async def send_tide_message(
    conversation_id: UUID,
    message: Dict[str, str],
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Send a message to TIDE and get a response.
    
    This endpoint:
    1. Saves the vendor's message
    2. Calls the AI to process the message
    3. Saves the AI response
    4. Returns both messages
    """
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only vendors can chat with TIDE"
        )
    
    # Verify conversation ownership
    conversation = await crud_conversation.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversation not found"
        )
    
    if str(conversation.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this conversation"
        )
    
    # Get vendor profile
    vendor = await _get_vendor_for_user(db, current_user.id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Vendor profile not found"
        )
    
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
    all_messages = await crud_chat_message.list_chat_messages(
        db, conversation_id=conversation_id, limit=50
    )
    
    # Use the conversation manager to rebuild history with proper tool call format
    from app.core.conversation_manager import rebuild_conversation_history
    history = rebuild_conversation_history(all_messages[:-1])  # Exclude the just-saved user message
    
    # Add current user message
    messages = history + [{"role": "user", "content": message.get("content", "")}]
    
    # 3. Process with AI engine
    from app.core.ai_engine import get_tide_engine, get_tide_system_prompt

    try:
        tide = await get_tide_engine()
        
        # Process conversation
        response_data = await tide.process_conversation(
            messages=messages,
            system_prompt=get_tide_system_prompt(),
            context={"vendor_id": str(vendor.id), "conversation_id": str(conversation_id)}
        )
        
        ai_content = response_data.get("content", "I'm having trouble processing that request.")
        tool_calls_list = response_data.get("tool_calls")
        
        # Convert tool_calls format for database
        tool_call_payload = None
        if tool_calls_list:
            tool_call_payload = {
                "calls": tool_calls_list  # Already in correct format
            }
        
    except Exception as e:
        print(f"❌ TIDE error: {e}")
        import traceback
        traceback.print_exc()
        ai_content = f"I'm having trouble connecting to my AI systems. Please try again."
        tool_call_payload = None
    
    # 4. Save AI response
    ai_message = await crud_chat_message.create_chat_message(
        db,
        {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": ai_content,
            "tool_call": tool_call_payload,
        }
    )
    
    return {
        "user_message": user_message,
        "ai_message": ai_message,
    }


# ==========================================
### NOTE: Dataset-related endpoints removed.
# Vendors should use global /datasets endpoints:
#   GET /api/v1/datasets/me/        (their own datasets)
#   GET /api/v1/datasets/{id}       (detail with RBAC)
# This keeps dataset logic centralized.
@router.post("/notify/{inquiry_id}")
async def trigger_inquiry_notification(
    inquiry_id: UUID,
    db: AsyncSession = Depends(get_session),
):
    """
    Trigger a notification for a new inquiry.
    Called after buyer submits an inquiry.
    """
    from app.models.models import Inquiry, Dataset, Buyer
    
    inquiry = await db.get(Inquiry, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    dataset = await db.get(Dataset, inquiry.dataset_id)
    buyer = await db.get(Buyer, inquiry.buyer_id)
    
    from app.services.inquiry_service import notify_vendor_of_new_inquiry

    result = await notify_vendor_of_new_inquiry(
        db=db,
        vendor_id=str(inquiry.vendor_id),
        inquiry_id=str(inquiry_id),
        dataset_title=dataset.title if dataset else "Unknown Dataset",
        buyer_organization=buyer.organization if buyer else None
    )
    
    return result

# ==========================================
# TIDE CHAT ENDPOINT (Stateless)
# ==========================================

class TideChatMessage(BaseModel):
    """Chat message for TIDE with conversation history"""
    content: str
    inquiry_id: str
    conversation_history: Optional[List[Dict[str, str]]] = []  # List of {role, content} messages


class TideChatResponse(BaseModel):
    """TIDE chat response"""
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


@router.post("/chat", response_model=TideChatResponse)
async def tide_chat(
    message: TideChatMessage,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Stateful chat with TIDE for inquiry assistance.
    
    This endpoint:
    1. Verifies vendor access and inquiry ownership
    2. Gets fresh inquiry context from database
    3. Uses conversation history provided by frontend
    4. Returns response with any tool calls
    
    NO conversation history is persisted - frontend manages the session state.
    """
    vendor = await _verify_vendor_access(db, current_user)
    
    # Verify inquiry belongs to this vendor
    inquiry_id = UUID(message.inquiry_id)
    inquiry = await db.get(Inquiry, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    if str(inquiry.vendor_id) != str(vendor.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this inquiry")
    
    # Get related data for fresh context
    dataset = await db.get(Dataset, inquiry.dataset_id) if inquiry.dataset_id else None
    buyer = await db.get(Buyer, inquiry.buyer_id) if inquiry.buyer_id else None
    
    # Build context for TIDE
    context = {
        "vendor_id": str(vendor.id),
        "inquiry_id": str(inquiry.id),
        "inquiry_summary": inquiry.summary,
        "inquiry_status": inquiry.status,
        "dataset_title": dataset.title if dataset else None,
        "dataset_description": dataset.description if dataset else None,
        "buyer_name": buyer.name if buyer else None,
        "buyer_organization": buyer.organization if buyer else None,
        "buyer_industry": buyer.industry if buyer else None,
    }
    
    # Build concise context message for TIDE
    buyer_inquiry_str = json.dumps(inquiry.buyer_inquiry, indent=2) if inquiry.buyer_inquiry else 'No specific requirements listed'
    vendor_response_str = json.dumps(inquiry.vendor_response, indent=2) if inquiry.vendor_response else 'No response yet'
    
    context_message = f"""[INQUIRY CONTEXT - inquiry_id: {inquiry.id}]
Dataset: {dataset.title if dataset else 'N/A'}
Buyer: {buyer.name if buyer else 'Unknown'} from {buyer.organization if buyer else 'N/A'}
Status: {inquiry.status}

Buyer's Requirements:
{buyer_inquiry_str}

Vendor's Response (if any):
{vendor_response_str}

Negotiation History:
{inquiry.summary if inquiry.summary else 'New inquiry - no history yet.'}

---
Vendor asks: {message.content}"""
    
    # Build messages array from conversation history + current message
    messages = []
    if message.conversation_history:
        messages.extend(message.conversation_history)
    
    # Add current message with fresh context
    messages.append({"role": "user", "content": context_message})
    
    # Process with TIDE AI engine
    from app.core.ai_engine import get_tide_engine, get_tide_system_prompt
    
    try:
        tide = await get_tide_engine()
        
        # Include conversation history with fresh context
        response_data = await tide.process_conversation(
            messages=messages,
            system_prompt=get_tide_system_prompt(),
            context=context
        )
        
        ai_content = response_data.get("content", "I'm having trouble processing that request.")
        tool_calls_list = response_data.get("tool_calls")
        
        return TideChatResponse(
            content=ai_content,
            tool_calls=tool_calls_list
        )
        
    except Exception as e:
        print(f"❌ TIDE chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat message"
        )
