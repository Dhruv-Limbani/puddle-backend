"""
MCP Client - Communicate with the Puddle MCP Server

This module uses OpenAI GPT-3.5 Turbo with function calling to intelligently
interact with MCP tools for dataset search, inquiry management, etc.
"""

import os
from typing import Dict, Any, List, Optional
import json
from openai import AsyncOpenAI


# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8002/puddle-mcp/mcp")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



# OpenAI client will be initialized when first used
_openai_client = None

def get_openai_client():
    """Get or create the OpenAI client (lazy initialization)"""
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _openai_client = AsyncOpenAI(api_key=api_key)
    return _openai_client


# Define MCP tools as OpenAI function schemas
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_datasets_semantic",
            "description": "Search for datasets using natural language. Use this when the user asks to find, search, or discover datasets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's search query in natural language"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_datasets",
            "description": "Filter datasets by specific criteria like domain or pricing model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "The domain or industry (e.g., Finance, Healthcare)"
                    },
                    "price_model": {
                        "type": "string",
                        "description": "Pricing model (e.g., Free, Subscription)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_details_complete",
            "description": "Get complete details about a specific dataset including schema and columns. Use this when user wants to know more about a dataset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "The UUID of the dataset"
                    }
                },
                "required": ["dataset_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_buyer_inquiry",
            "description": "Create and submit a new inquiry for a dataset. USE THIS when buyer wants to request access, create an inquiry, submit a request, or purchase a dataset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "buyer_id": {
                        "type": "string",
                        "description": "The buyer's UUID"
                    },
                    "dataset_id": {
                        "type": "string",
                        "description": "The dataset UUID"
                    },
                    "conversation_id": {
                        "type": "string",
                        "description": "The conversation UUID"
                    },
                    "initial_state_json": {
                        "type": "object",
                        "description": "Inquiry details including use_case, budget, requirements, questions"
                    }
                },
                "required": ["buyer_id", "dataset_id", "conversation_id", "initial_state_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_inquiry_full_state",
            "description": "Get the full state of an inquiry including buyer request and vendor response. Use this to check inquiry status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "inquiry_id": {
                        "type": "string",
                        "description": "The inquiry UUID"
                    }
                },
                "required": ["inquiry_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_inquiry_to_vendor",
            "description": "Submit the inquiry to the vendor for review. Use after creating an inquiry.",
            "parameters": {
                "type": "object",
                "properties": {
                    "inquiry_id": {
                        "type": "string",
                        "description": "The inquiry UUID"
                    }
                },
                "required": ["inquiry_id"]
            }
        }
    }
]


import httpx

async def call_mcp_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    timeout: float = 60.0
) -> Dict[str, Any]:
    """
    Call an MCP tool using the HTTP transport with SSE support.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
        timeout: Request timeout in seconds
        
    Returns:
        Tool result as a dictionary
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # MCP StreamableHTTP requires specific headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        response = await client.post(MCP_SERVER_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        # Parse SSE response
        # The response comes as:
        # event: message
        # data: {"jsonrpc":"2.0",...}
        
        response_text = response.text
        for line in response_text.splitlines():
            if line.startswith("data: "):
                json_str = line[6:]  # Skip "data: "
                try:
                    result = json.loads(json_str)
                    
                    if "result" in result:
                        # Extract content from result
                        content = result["result"].get("content", [])
                        # If content is a list of objects with 'text', extract it
                        if isinstance(content, list):
                            text_content = []
                            for item in content:
                                if isinstance(item, dict) and "text" in item:
                                    text_content.append(item["text"])
                                else:
                                    text_content.append(str(item))
                            return {"content": text_content}
                        return result["result"]
                    elif "error" in result:
                        raise Exception(f"MCP Error: {result['error']}")
                except json.JSONDecodeError:
                    continue
                    
        raise Exception("No valid JSON-RPC response found in SSE stream")





async def process_chat_with_ai(
    message: str,
    conversation_history: List[Dict[str, str]],
    buyer_id: str,
    conversation_id: str,
    timeout: float = 90.0
) -> Dict[str, Any]:
    """
    Process a chat message using GPT-3.5 Turbo with MCP tools.
    
    GPT-3.5 will decide which MCP tools to call based on the user's intent.
    
    Args:
        message: User's message
        conversation_history: Previous messages in the conversation
        buyer_id: Buyer's UUID
        conversation_id: Conversation UUID
        timeout: Request timeout
        
    Returns:
        Dictionary with 'content', 'tool_calls', and other metadata
    """
    try:
        # Build messages for GPT
        messages = [
            {
            "role": "system",
            "content": f"""You are ACID, a helpful data marketplace assistant. You help buyers find and purchase datasets.

            === CURRENT SESSION ===
            Buyer ID: {buyer_id}
            Conversation ID: {conversation_id}

            === YOUR TOOLS ===
            - search_datasets_semantic: Search for datasets
            - filter_datasets: Filter by domain/pricing
            - get_dataset_details_complete: Get full dataset info
            - create_buyer_inquiry: CREATE an inquiry for a dataset
            - get_inquiry_full_state: Check inquiry status

            === IMPORTANT ===
            When buyer wants to create an inquiry, request access, or purchase a dataset:
            1. Call create_buyer_inquiry with:
            - buyer_id: "{buyer_id}"
            - dataset_id: "<the dataset UUID>"
            - conversation_id: "{conversation_id}"
            - initial_state_json: {{"use_case": "...", "budget": "...", "requirements": "...", "questions": [...]}}

            Always use the EXACT buyer_id and conversation_id provided above!"""
        }
        ]
        
        # Add conversation history
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Call GPT-3.5 Turbo with function calling
        openai_client = get_openai_client()
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=MCP_TOOLS,
            tool_choice="auto",
            temperature=0.7,
        )
        
        assistant_message = response.choices[0].message
        tool_calls_made = []
        
        # Check if GPT wants to call tools
        if assistant_message.tool_calls:
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Call the MCP tool
                tool_result = await call_mcp_tool(function_name, function_args)
                
                # Extract text from MCP response
                tool_output = tool_result.get("content", [])
                
                tool_text = ""
                if isinstance(tool_output, list) and len(tool_output) > 0:
                    first_item = tool_output[0]
                    if isinstance(first_item, dict):
                        tool_text = first_item.get("text", str(tool_output))
                    else:
                        tool_text = str(first_item)
                elif isinstance(tool_output, str):
                    tool_text = tool_output
                else:
                    tool_text = str(tool_output)
                
                tool_calls_made.append({
                    "tool": function_name,
                    "arguments": function_args,
                    "result": tool_text
                })

            
            # Send tool results back to GPT for final response
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            # Add tool results
            for i, tool_call in enumerate(assistant_message.tool_calls):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_calls_made[i]["result"]
                })
            
            # Get final response from GPT
            final_response = await get_openai_client().chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
            )
            
            final_content = final_response.choices[0].message.content
        else:
            # No tool calls, just use GPT's response
            final_content = assistant_message.content or "I'm here to help you find datasets. What are you looking for?"
        
        return {
            "content": final_content,
            "tool_calls": tool_calls_made if tool_calls_made else None,
            "action": "ai_response"
        }
        
    except Exception as e:
        return {
            "content": f"I'm having trouble processing your request. Error: {str(e)}",
            "tool_calls": None,
            "action": "error"
        }


async def create_inquiry_via_mcp(
    buyer_id: str,
    dataset_id: str,
    conversation_id: str,
    inquiry_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create an inquiry using the MCP tool.
    
    Args:
        buyer_id: Buyer UUID
        dataset_id: Dataset UUID
        conversation_id: Conversation UUID
        inquiry_data: Initial inquiry JSON data
        
    Returns:
        MCP tool result
    """
    return await call_mcp_tool(
        "create_buyer_inquiry",
        {
            "buyer_id": buyer_id,
            "dataset_id": dataset_id,
            "conversation_id": conversation_id,
            "initial_state_json": inquiry_data
        }
    )


# async def process_tide_chat(
#     message: str,
#     conversation_history: List[Dict[str, str]],
#     vendor_id: str,
#     conversation_id: str,
#     timeout: float = 90.0
# ) -> Dict[str, Any]:
#     """
#     Process a chat message for TIDE (vendor-facing agent).
    
#     TIDE helps vendors:
#     - Review incoming inquiries
#     - Understand buyer requirements
#     - Prepare responses with pricing
#     """
#     try:
#         messages = [
#             {
#                 "role": "system",
#                 "content": """You are TIDE, an AI assistant for data vendors on the Puddle marketplace.

# Your role is to help vendors:
# 1. Review and understand incoming dataset inquiries from buyers
# 2. Summarize buyer requirements clearly
# 3. Help prepare responses with appropriate pricing
# 4. Answer questions about their inquiries and datasets

# Your personality:
# - Professional and efficient
# - Provide clear, actionable information
# - Help vendors make informed decisions quickly
# - Flag any concerns or special requirements

# When vendors ask about inquiries, provide helpful summaries and recommendations.
# When they want to respond to an inquiry, help them craft an appropriate response.

# Always be concise and focus on business-relevant information."""
#             }
#         ]
        
#         # Add conversation history (last 5 messages for context)
#         for msg in conversation_history[-5:]:
#             messages.append({
#                 "role": msg["role"],
#                 "content": msg["content"]
#             })
        
#         # Add current message
#         messages.append({
#             "role": "user",
#             "content": message
#         })
        
#         # Call GPT-3.5 Turbo
#         openai_client = get_openai_client()
#         response = await openai_client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#             temperature=0.7,
#         )
        
#         final_content = response.choices[0].message.content or "I'm here to help you manage inquiries. What would you like to do?"
        
#         return {
#             "content": final_content,
#             "tool_calls": None,
#             "action": "ai_response"
#         }
        
#     except Exception as e:
#         return {
#             "content": f"I'm having trouble processing your request. Error: {str(e)}",
#             "tool_calls": None,
#             "action": "error"
#         }

# ==========================================
# TIDE TOOLS (Vendor-facing) - Uses MCP Server
# ==========================================

TIDE_MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_vendor_work_queue",
            "description": "Get all pending inquiries that need vendor review (status='submitted'). Use when vendor asks about new inquiries, what needs attention, or pending requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "string",
                        "description": "The vendor's UUID"
                    }
                },
                "required": ["vendor_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_inquiry_full_state",
            "description": "Get complete details of a specific inquiry including buyer's request and current status. Use when vendor asks about a specific inquiry.",
            "parameters": {
                "type": "object",
                "properties": {
                    "inquiry_id": {
                        "type": "string",
                        "description": "The inquiry UUID"
                    }
                },
                "required": ["inquiry_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_vendor_response_json",
            "description": "Update the vendor's response to an inquiry. Use to draft responses, provide pricing, ask clarifications, or approve/reject.",
            "parameters": {
                "type": "object",
                "properties": {
                    "inquiry_id": {
                        "type": "string",
                        "description": "The inquiry UUID"
                    },
                    "new_response_json": {
                        "type": "object",
                        "description": "The vendor's response JSON containing action, pricing, terms, notes, etc."
                    },
                    "mark_ready_for_review": {
                        "type": "boolean",
                        "description": "If true, marks inquiry as 'pending_review' for human approval.",
                        "default": False
                    }
                },
                "required": ["inquiry_id", "new_response_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_details_complete",
            "description": "Get complete details about a dataset including schema, pricing, and license info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "The dataset UUID"
                    }
                },
                "required": ["dataset_id"]
            }
        }
    }
]


# ==========================================
# TIDE HELPER FUNCTIONS
# ==========================================

async def load_vendor_agent_config(db, vendor_id: str) -> Dict[str, Any]:
    """Load the vendor's AI agent configuration from the database."""
    from sqlalchemy import select
    from app.models.models import AIAgent
    
    result = await db.execute(
        select(AIAgent).where(
            AIAgent.vendor_id == vendor_id,
            AIAgent.active == True
        )
    )
    agent = result.scalars().first()
    
    default_config = {
        "temperature": 0.7,
        "pricing_policies": None,
        "response_style": "professional",
        "custom_instructions": None,
    }
    
    if agent and agent.config:
        return {**default_config, **agent.config}
    
    return default_config


async def load_vendor_datasets_summary(db, vendor_id: str) -> str:
    """Load a summary of the vendor's datasets for context."""
    from sqlalchemy import select
    from app.models.models import Dataset
    
    result = await db.execute(
        select(Dataset).where(
            Dataset.vendor_id == vendor_id,
            Dataset.status == 'active'
        ).limit(20)
    )
    datasets = result.scalars().all()
    
    if not datasets:
        return "No active datasets in catalog."
    
    summary = f"Your catalog has {len(datasets)} active dataset(s):\n"
    for d in datasets:
        summary += f"- {d.title} | Domain: {d.domain} | Pricing: {d.pricing_model}\n"
    
    return summary


def build_tide_system_prompt(
    vendor_id: str,
    agent_config: Dict[str, Any],
    datasets_summary: str
) -> str:
    """Build a customized system prompt for TIDE based on vendor's agent config."""
    
    base_prompt = """You are TIDE, an AI sales assistant for a data vendor on the Puddle marketplace.

Your role is to help the vendor:
1. Review and respond to incoming dataset inquiries from buyers
2. Provide pricing quotes based on the vendor's policies
3. Answer questions about datasets
4. Flag inquiries that need human review

"""
    
    # Add vendor's data catalog context
    base_prompt += f"=== YOUR DATA CATALOG ===\n{datasets_summary}\n\n"
    
    # Add pricing policies if configured
    if agent_config.get("pricing_policies"):
        base_prompt += f"=== PRICING POLICIES ===\n{agent_config['pricing_policies']}\n\n"
    
    # Add custom instructions if configured
    if agent_config.get("custom_instructions"):
        base_prompt += f"=== SPECIAL INSTRUCTIONS ===\n{agent_config['custom_instructions']}\n\n"
    
    # Add tool usage instructions
    base_prompt += """=== TOOLS & WHEN TO USE THEM ===

    1. get_vendor_work_queue(vendor_id) 
    → Use when: vendor asks "what inquiries do I have?" or "any pending requests?"

    2. get_inquiry_full_state(inquiry_id)
    → Use when: vendor asks for details about a specific inquiry

    3. update_vendor_response_json(inquiry_id, new_response_json, mark_ready_for_review)
    → Use when: vendor wants to APPROVE, REJECT, or RESPOND to an inquiry
    → THIS IS CRITICAL: You MUST call this tool to save any response!
    CRITICAL:
    If vendor says "approve", "reject", "accept", or "respond" to ANY inquiry,
    you MUST call update_vendor_response_json.
    
    CRITICAL: ALWAYS set mark_ready_for_review = true when approving or rejecting!
    WITHOUT calling this tool, NOTHING IS SAVED!
    
    For APPROVE:
    {
        "action": "approve",
        "price": <amount>,
        "currency": "USD",
        "terms": "<license terms>",
        "notes": "<any notes>",
        "mark_ready_for_review": true
    }
    
    For REJECT:
    {
        "action": "reject", 
        "reason": "<rejection reason>",
        "mark_ready_for_review": true
    }

    4. get_dataset_details_complete(dataset_id)
    → Use when: need dataset information

    IMPORTANT: When vendor says "approve", "reject", "respond", or "accept" an inquiry, 
    you MUST call update_vendor_response_json. Do NOT just say you approved it - actually call the tool!
    """

    return base_prompt


# ==========================================
# TIDE CHAT PROCESSOR (Vendor-facing)
# ==========================================

async def process_tide_chat(
    message: str,
    conversation_history: List[Dict[str, str]],
    vendor_id: str,
    conversation_id: str,
    db=None,
    timeout: float = 90.0
) -> Dict[str, Any]:
    """
    Process a chat message for TIDE (vendor-facing agent).
    Uses MCP tools and loads vendor's agent configuration.
    """
    try:
        # Load vendor's agent config and dataset summary
        agent_config = {"temperature": 0.7}
        datasets_summary = "Dataset catalog not loaded."
        
        if db:
            agent_config = await load_vendor_agent_config(db, vendor_id)
            datasets_summary = await load_vendor_datasets_summary(db, vendor_id)
        
        # Build customized system prompt
        system_prompt = build_tide_system_prompt(vendor_id, agent_config, datasets_summary)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-5:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        messages.append({"role": "user", "content": message})
        
        message_lower = message.lower()
        if any(word in message_lower for word in ["approve", "reject", "accept", "respond to", "send response"]):
            tool_choice = {"type": "function", "function": {"name": "update_vendor_response_json"}}
        else:
            tool_choice = "auto"
        
        # Get temperature from config
        temperature = agent_config.get("temperature", 0.7)
        
        # Call GPT with TIDE tools
        openai_client = get_openai_client()
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=TIDE_MCP_TOOLS,
            tool_choice=tool_choice,  # <-- Change this line
            temperature=temperature,
        )
        
        assistant_message = response.choices[0].message
        tool_calls_made = []
        
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "update_vendor_response_json":
                    # Check if arguments are flat (missing new_response_json wrapper)
                    if "new_response_json" not in function_args and "action" in function_args:
                        # Extract inquiry_id
                        inquiry_id = function_args.pop("inquiry_id", None)
                        mark_ready = function_args.pop("mark_ready_for_review", True)
                        
                        # Everything else goes in new_response_json
                        function_args = {
                            "inquiry_id": inquiry_id,
                            "new_response_json": function_args,
                            "mark_ready_for_review": mark_ready
                        }
                
                # Inject vendor_id for vendor-specific tools
                if function_name == "get_vendor_work_queue":
                    function_args["vendor_id"] = vendor_id
                
                # Call MCP server
                tool_result = await call_mcp_tool(function_name, function_args)
                
                # Extract text from result
                tool_output = tool_result.get("content", [])
                if isinstance(tool_output, list) and len(tool_output) > 0:
                    first_item = tool_output[0]
                    if isinstance(first_item, dict):
                        tool_text = first_item.get("text", str(tool_output))
                    else:
                        tool_text = str(first_item)
                elif isinstance(tool_output, str):
                    tool_text = tool_output
                else:
                    tool_text = str(tool_output)
                
                tool_calls_made.append({
                    "tool": function_name,
                    "arguments": function_args,
                    "result": tool_text
                })
            
            # Send tool results back to GPT
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            for i, tool_call in enumerate(assistant_message.tool_calls):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_calls_made[i]["result"]
                })
            
            # Get final response
            final_response = await get_openai_client().chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=temperature,
            )
            
            final_content = final_response.choices[0].message.content
        else:
            final_content = assistant_message.content or "I'm here to help you manage inquiries. What would you like to do?"
        
        return {
            "content": final_content,
            "tool_calls": tool_calls_made if tool_calls_made else None,
            "action": "ai_response"
        }
        
    except Exception as e:
        return {
            "content": f"I'm having trouble processing your request. Error: {str(e)}",
            "tool_calls": None,
            "action": "error"
        }
        
# ==========================================
# TIDE NOTIFICATION SYSTEM
# ==========================================

async def notify_vendor_of_new_inquiry(
    db,
    vendor_id: str,
    inquiry_id: str,
    dataset_title: str,
    buyer_organization: str = None
) -> Dict[str, Any]:
    """
    Send a notification to the vendor when a new inquiry is submitted.
    Creates a message in the vendor's TIDE notification conversation.
    """
    from app.crud import crud_conversation, crud_chat_message
    from app.models.models import Vendor, Conversation
    from sqlalchemy import select
    
    try:
        # Get vendor's user_id
        vendor = await db.get(Vendor, vendor_id)
        if not vendor:
            return {"success": False, "error": "Vendor not found"}
        
        # Find or create a TIDE notification conversation
        result = await db.execute(
            select(Conversation).where(
                Conversation.user_id == vendor.user_id,
                Conversation.title == "TIDE Notifications"
            )
        )
        notification_conv = result.scalars().first()
        
        if not notification_conv:
            # Create notification conversation
            from app.schemas.conversation import ConversationCreate
            notification_conv = await crud_conversation.create_conversation(
                db,
                ConversationCreate(
                    user_id=vendor.user_id,
                    title="TIDE Notifications"
                )
            )
            notification_conv_id = notification_conv.id
        else:
            notification_conv_id = notification_conv.id
        
        # Build notification message
        buyer_info = f" from **{buyer_organization}**" if buyer_organization else ""
        notification_content = f"""🔔 **New Inquiry Alert**

A new inquiry{buyer_info} has been submitted for your dataset: **{dataset_title}**

**Inquiry ID:** `{inquiry_id}`

To review this inquiry, ask me:
- "Show me details for inquiry {inquiry_id}"
- "What are my pending inquiries?"

I'm here to help you respond quickly!"""

        # Create the notification message
        await crud_chat_message.create_chat_message(
            db,
            {
                "conversation_id": notification_conv_id,
                "role": "assistant",
                "content": notification_content,
                "tool_call": {
                    "type": "notification",
                    "inquiry_id": inquiry_id
                }
            }
        )
        
        return {
            "success": True,
            "conversation_id": str(notification_conv_id)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}