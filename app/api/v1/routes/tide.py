"""
TIDE Agent Routes - Vendor-facing AI assistant

This module provides endpoints for:
- Vendor inquiry management
- AI-powered inquiry summarization
- Vendor response handling
- Vendor chat with TIDE
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
from app.schemas.inquiry import InquiryCreate, InquiryRead, InquiryUpdate
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


async def _get_inquiry_for_vendor(
    db: AsyncSession, 
    inquiry_id: UUID, 
    vendor: Vendor
) -> Inquiry:
    """Get inquiry and verify it belongs to the vendor"""
    inquiry = await crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Inquiry not found"
        )
    
    if str(inquiry.vendor_id) != str(vendor.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this inquiry"
        )
    
    return inquiry


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

@router.get("/inquiries", response_model=List[InquiryRead])
async def list_vendor_inquiries(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List all inquiries for the current vendor.
    
    Optionally filter by status:
    - draft: Buyer is still working on inquiry
    - submitted: Buyer submitted, awaiting vendor review
    - pending_review: Vendor is reviewing
    - responded: Vendor has responded with pricing
    - accepted: Buyer accepted the offer
    - rejected: Vendor rejected the inquiry
    """
    vendor = await _verify_vendor_access(db, current_user)
    
    inquiries = await crud_inquiry.list_inquiries_by_vendor(
        db, vendor_id=vendor.id, limit=limit, offset=offset
    )
    
    # Filter by status if provided
    if status_filter:
        inquiries = [i for i in inquiries if i.status == status_filter]
    
    return inquiries


@router.get("/inquiries/pending", response_model=List[InquiryRead])
async def list_pending_inquiries(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List inquiries that need vendor review.
    These are inquiries with status 'submitted' or 'pending_review'.
    
    This is the primary endpoint for vendors to see what needs attention.
    """
    vendor = await _verify_vendor_access(db, current_user)
    
    # Get all vendor inquiries
    all_inquiries = await crud_inquiry.list_inquiries_by_vendor(
        db, vendor_id=vendor.id, limit=100, offset=0
    )
    
    # Filter for pending ones
    pending_statuses = ['submitted', 'pending_review']
    pending = [i for i in all_inquiries if i.status in pending_statuses]
    
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
        "pending": len([i for i in all_inquiries if i.status in ['submitted', 'pending_review']]),
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
    inquiry = await _get_inquiry_for_vendor(db, inquiry_id, vendor)
    
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
    inquiry = await _get_inquiry_for_vendor(db, inquiry_id, vendor)
    
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
        new_status = "pending_review"  # Keep in review until buyer responds
        
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
    - pending_review: Mark as under review
    - responded: Mark as responded (usually done via /respond endpoint)
    - rejected: Mark as rejected
    """
    vendor = await _verify_vendor_access(db, current_user)
    inquiry = await _get_inquiry_for_vendor(db, inquiry_id, vendor)
    
    allowed_statuses = ['pending_review', 'responded', 'rejected']
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
    inquiry = await _get_inquiry_for_vendor(db, inquiry_id, vendor)
    
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
    
    # Use AI to generate summary
    from app.utils.mcp_client import get_openai_client
    
    prompt = f"""You are TIDE, an AI assistant helping data vendors review buyer inquiries.

Summarize this dataset inquiry for the vendor representative:

DATASET INFORMATION:
- Title: {context['dataset_title']}
- Description: {context['dataset_description']}
- Domain: {context['dataset_domain']}
- Pricing Model: {context['dataset_pricing_model']}

BUYER INFORMATION:
- Organization: {context['buyer_organization']}
- Industry: {context['buyer_industry']}
- Use Case Focus: {context['buyer_use_case']}

BUYER'S INQUIRY DETAILS:
{json.dumps(context['buyer_inquiry'], indent=2) if context['buyer_inquiry'] else 'No specific details provided'}

Please provide a clear, concise summary covering:
1. **What the buyer wants**: Summarize their request in 1-2 sentences
2. **Key requirements**: Any specific needs mentioned (data format, time period, volume, etc.)
3. **Buyer context**: Relevant info about their organization/use case
4. **Considerations**: Any points the vendor should think about
5. **Recommended action**: Approve, reject, or request more info - with brief reasoning

Keep the summary brief (under 300 words) and actionable."""

    try:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        
        summary = response.choices[0].message.content
        
        return InquirySummaryResponse(
            inquiry_id=str(inquiry_id),
            summary=summary,
            dataset_title=dataset.title if dataset else None,
            status=inquiry.status,
            buyer_requirements=inquiry.buyer_inquiry
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to generate summary: {str(e)}"
        )


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
    
    # 2. Get conversation history for context
    all_messages = await crud_chat_message.list_chat_messages(
        db, conversation_id=conversation_id, limit=50
    )
    
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in all_messages[:-1]  # Exclude the message we just added
    ]
    
    # 3. Call TIDE AI processor
    from app.utils.mcp_client import process_tide_chat
    
    try:
        response_data = await process_tide_chat(
        message=message.get("content", ""),
        conversation_history=history,
        vendor_id=str(vendor.id),
        conversation_id=str(conversation_id),
        db=db,  # <-- ADD THIS LINE
    )
        
        ai_content = response_data.get("content", "I'm having trouble processing that request.")
        tool_calls = response_data.get("tool_calls")
        
    except Exception as e:
        ai_content = f"I'm having trouble connecting to my AI systems. Please try again. Error: {str(e)}"
        tool_calls = None
    
    # 4. Save AI response
    ai_message = await crud_chat_message.create_chat_message(
        db,
        {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": ai_content,
            "tool_call": tool_calls,
        }
    )
    
    return {
        "user_message": user_message,
        "ai_message": ai_message,
    }


# ==========================================
# DATASET ENDPOINTS (Vendor's Own Datasets)
# ==========================================

@router.get("/datasets", response_model=List[Dict[str, Any]])
async def list_vendor_datasets(
    limit: int = 50,
    offset: int = 0,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    List all datasets owned by the current vendor.
    Useful for TIDE to reference when discussing inquiries.
    """
    vendor = await _verify_vendor_access(db, current_user)
    
    result = await db.execute(
        select(Dataset)
        .where(Dataset.vendor_id == str(vendor.id))
        .limit(limit)
        .offset(offset)
    )
    datasets = result.scalars().all()
    
    return [
        {
            "id": str(d.id),
            "title": d.title,
            "description": d.description,
            "domain": d.domain,
            "pricing_model": d.pricing_model,
            "license": d.license,
            "status": d.status,
        }
        for d in datasets
    ]


@router.get("/datasets/{dataset_id}", response_model=Dict[str, Any])
async def get_vendor_dataset(
    dataset_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get detailed information about a vendor's dataset.
    """
    vendor = await _verify_vendor_access(db, current_user)
    
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Dataset not found"
        )
    
    if str(dataset.vendor_id) != str(vendor.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this dataset"
        )
    
    return {
        "id": str(dataset.id),
        "title": dataset.title,
        "description": dataset.description,
        "domain": dataset.domain,
        "dataset_type": dataset.dataset_type,
        "granularity": dataset.granularity,
        "pricing_model": dataset.pricing_model,
        "license": dataset.license,
        "topics": dataset.topics,
        "entities": dataset.entities,
        "temporal_coverage": dataset.temporal_coverage,
        "geographic_coverage": dataset.geographic_coverage,
        "status": dataset.status,
        "visibility": dataset.visibility,
    }
    
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
    
    from app.utils.mcp_client import notify_vendor_of_new_inquiry
    
    result = await notify_vendor_of_new_inquiry(
        db=db,
        vendor_id=str(inquiry.vendor_id),
        inquiry_id=str(inquiry_id),
        dataset_title=dataset.title if dataset else "Unknown Dataset",
        buyer_organization=buyer.organization if buyer else None
    )
    
    return result