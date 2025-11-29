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
                "content": """You are ACID, a helpful data marketplace assistant. You help buyers find and evaluate datasets.

Your personality:
- Professional and concise
- Proactive in suggesting relevant datasets
- Ask clarifying questions when needed

When users ask about datasets:
- Use search_datasets_semantic for general queries
- Use filter_datasets for specific criteria
- Use get_dataset_details_complete when they want details about a specific dataset

Always be helpful and guide the conversation toward finding the right dataset for their needs."""
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
