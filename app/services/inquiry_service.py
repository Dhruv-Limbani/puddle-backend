from typing import Dict, Any, Optional
from uuid import UUID
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud import crud_conversation, crud_chat_message, crud_inquiry
from app.models.models import Vendor, Conversation, Inquiry, Dataset, Buyer
from app.utils.mcp_client import get_openai_client


async def notify_vendor_of_new_inquiry(
    db: AsyncSession,
    vendor_id: str,
    inquiry_id: str,
    dataset_title: str,
    buyer_organization: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        vendor = await db.get(Vendor, vendor_id)
        if not vendor:
            return {"success": False, "error": "Vendor not found"}

        result = await db.execute(
            select(Conversation).where(
                Conversation.user_id == vendor.user_id,
                Conversation.title == "TIDE Notifications",
            )
        )
        notification_conv = result.scalars().first()

        if not notification_conv:
            from app.schemas.conversation import ConversationCreate

            notification_conv = await crud_conversation.create_conversation(
                db,
                ConversationCreate(user_id=vendor.user_id, title="TIDE Notifications"),
            )
            notification_conv_id = notification_conv.id
        else:
            notification_conv_id = notification_conv.id

        buyer_info = f" from **{buyer_organization}**" if buyer_organization else ""
        notification_lines = [
            "🔔 **New Inquiry Alert**",
            "",
            f"A new inquiry{buyer_info} has been submitted for your dataset: **{dataset_title}**",
            "",
            f"**Inquiry ID:** `{inquiry_id}`",
            "",
            "To review this inquiry, ask me:",
            f"- \"Show me details for inquiry {inquiry_id}\"",
            "- \"What are my pending inquiries?\"",
        ]
        notification_content = "\n".join(notification_lines)

        await crud_chat_message.create_chat_message(
            db,
            {
                "conversation_id": notification_conv_id,
                "role": "assistant",
                "content": notification_content,
                "tool_call": {"calls": [], "trace_id": None},
            },
        )

        return {"success": True, "conversation_id": str(notification_conv_id)}

    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_inquiry_summary(db: AsyncSession, inquiry_id: UUID) -> Dict[str, Any]:
    inquiry = await db.get(Inquiry, inquiry_id)
    if not inquiry:
        return {"error": "Inquiry not found"}

    dataset = await db.get(Dataset, inquiry.dataset_id)
    buyer = await db.get(Buyer, inquiry.buyer_id)

    buyer_inquiry_render = (
        json.dumps(inquiry.buyer_inquiry, indent=2) if inquiry.buyer_inquiry else "No specific details provided"
    )

    prompt = (
        "You are TIDE, an AI assistant helping data vendors review buyer inquiries.\n\n"
        "Summarize this dataset inquiry for the vendor representative:\n\n"
        f"DATASET INFORMATION:\n- Title: {dataset.title if dataset else 'Unknown'}\n"
        f"- Description: {dataset.description if dataset else 'N/A'}\n"
        f"- Domain: {dataset.domain if dataset else 'N/A'}\n"
        f"- Pricing Model: {dataset.pricing_model if dataset else 'N/A'}\n\n"
        f"BUYER INFORMATION:\n- Organization: {buyer.organization if buyer else 'Unknown'}\n"
        f"- Industry: {buyer.industry if buyer else 'N/A'}\n"
        f"- Use Case Focus: {buyer.use_case_focus if buyer else 'N/A'}\n\n"
        f"BUYER'S INQUIRY DETAILS:\n{buyer_inquiry_render}\n\n"
        "Please provide a clear, concise summary covering:\n"
        "1. What the buyer wants\n"
        "2. Key requirements\n"
        "3. Buyer context\n"
        "4. Considerations\n"
        "5. Recommended action (approve/reject/request info)\n\n"
        "Keep the summary brief (under 300 words) and actionable."
    )

    client = get_openai_client()
    response = await client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500,
    )

    summary = response.choices[0].message.content
    return {
        "inquiry_id": str(inquiry_id),
        "summary": summary,
        "dataset_title": dataset.title if dataset else None,
        "status": inquiry.status,
        "buyer_requirements": inquiry.buyer_inquiry,
    }
