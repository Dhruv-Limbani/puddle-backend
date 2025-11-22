from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import json
from google import genai
from google.genai import types

from app.core.db import get_session
from app.core.config import settings
from app.core.auth import get_current_user
from app.schemas.user import UserRead
from app.tools.acid_ai_tool import acid_ai_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/acid-ai", tags=["acid-ai"])

class ChatMessage(BaseModel):
    role: str
    content: str

class AcidAiQueryRequest(BaseModel):
    query: str
    history: Optional[List[ChatMessage]] = []

class AcidAiResponse(BaseModel):
    answer: str
    tool_output: Optional[Dict[str, Any]] = None

async def decide_and_generate(query: str, history: List[ChatMessage], db: AsyncSession) -> tuple[str, Optional[Dict[str, Any]]]:
    """
    Uses the LLM to decide whether to call the tool (dataset search) or just chat,
    taking conversation history into account.
    """
    
    # Format history for the prompt
    history_text = ""
    if history:
        history_text = "Conversation History:\n"
        for msg in history[-5:]: # Keep last 5 messages for context
            role = "User" if msg.role == "user" else "ACID AI"
            history_text += f"{role}: {msg.content}\n"

    # Fallback if no API key is present
    if not settings.GEMINI_API_KEY:
        # Simple fallback logic
        if "find" in query.lower() or "dataset" in query.lower():
             tool_result = await acid_ai_query(query, db)
             return f"I found {tool_result.get('count', 0)} datasets.", tool_result
        return "Hello! I am ACID AI (Fallback Mode). I can help you find datasets.", None

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    # 1. Decision Step: Ask LLM if we need to search DB
    decision_prompt = f"""
    You are ACID AI, an assistant for a dataset marketplace.
    
    {history_text}
    User Query: "{query}"
    
    Determine if the user is asking to find/search for NEW datasets, OR if they are asking a follow-up question about previously discussed datasets or general chat.
    
    Reply with ONLY one word:
    - "SEARCH" if they are explicitly looking for data/datasets.
    - "CHAT" if it is a greeting, general question, follow-up question, or off-topic.
    """
    
    try:
        decision_resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=decision_prompt
        )
        intent = decision_resp.text.strip().upper()
        logger.info(f"ACID AI Intent Decision: {intent} for query: {query}")
        
        tool_result = None
        
        if "SEARCH" in intent:
            # 2. Execute Tool
            tool_result = await acid_ai_query(query, db)
            
            # 3. Generate Final Answer with Context
            final_prompt = f"""
            You are ACID AI, an expert dataset consultant.
            
            {history_text}
            User Query: "{query}"
            
            I have retrieved the following datasets from the database (Mock Data):
            {json.dumps(tool_result.get('results', []), default=str)}
            
            Please answer the user's query using this information.
            - Highlight the top match if relevant.
            - Mention price or domain if asked.
            - If the results seem irrelevant, politely say so.
            """
        else:
            # 3. Generate Chat Answer (with history)
            final_prompt = f"""
            You are ACID AI, a friendly assistant for Puddle (a dataset marketplace).
            
            {history_text}
            User Query: "{query}"
            
            Respond helpfully and professionally to the user's query, maintaining the context of the conversation.
            If they are asking about a specific dataset mentioned previously, try to answer from context.
            Encourage the user to search for datasets if they seem interested.
            Do NOT invent datasets.
            """

        final_resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=final_prompt
        )
        return final_resp.text, tool_result

    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return "I'm having a bit of trouble thinking right now. Please try again.", None


@router.post("/query", response_model=AcidAiResponse)
async def query_acid_ai(
    request: AcidAiQueryRequest,
    db: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    ACID AI endpoint for Buyers.
    Uses LLM to decide intent and generate response with history context.
    """
    if current_user.role not in ["buyer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. ACID AI is only available for Buyers."
        )
    
    answer, tool_result = await decide_and_generate(request.query, request.history or [], db)
    
    return AcidAiResponse(
        answer=answer,
        tool_output=tool_result
    )
