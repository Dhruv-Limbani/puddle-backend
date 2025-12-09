"""
Conversation History Manager

Properly reconstructs conversation history from database messages,
preserving tool calls in the correct OpenAI format.
"""

import json
from typing import List, Dict, Any
from app.schemas.chat_message import ChatMessageRead


def rebuild_conversation_history(messages: List[ChatMessageRead]) -> List[Dict[str, Any]]:
    """
    Rebuild conversation history in OpenAI message format.
    
    The key insight: We need to reconstruct the EXACT conversation that happened,
    including assistant messages with tool_calls and the corresponding tool responses.
    
    Args:
        messages: Database messages (ordered by created_at)
    
    Returns:
        List of messages in OpenAI format, ready to send to LLM
    """
    rebuilt = []
    
    for msg in messages:
        if msg.role == "user":
            # Simple user message
            rebuilt.append({
                "role": "user",
                "content": msg.content
            })
        
        elif msg.role == "assistant":
            # Assistant message
            base_msg = {
                "role": "assistant",
                "content": msg.content
            }
            
            # If assistant made tool calls, we need to include them
            # AND add synthetic "tool" role messages with the results
            if msg.tool_call:
                # Handle both dict and ToolCallPayload object
                tool_call_data = msg.tool_call
                if hasattr(tool_call_data, 'model_dump'):
                    tool_call_data = tool_call_data.model_dump()
                
                if isinstance(tool_call_data, dict) and "calls" in tool_call_data:
                    # Add tool_calls to assistant message
                    tool_calls = []
                    for idx, call in enumerate(tool_call_data["calls"]):
                        tool_calls.append({
                            "id": f"call_{msg.id}_{idx}",  # Generate consistent ID
                            "type": "function",
                            "function": {
                                "name": call["name"],
                                "arguments": json.dumps(call.get("arguments", {}))
                            }
                        })
                    
                    base_msg["tool_calls"] = tool_calls
                    rebuilt.append(base_msg)
                    
                    # Add tool results as separate messages
                    for idx, call in enumerate(tool_call_data["calls"]):
                        if call.get("result"):
                            rebuilt.append({
                                "role": "tool",
                                "tool_call_id": f"call_{msg.id}_{idx}",
                                "content": call["result"]
                            })
                else:
                    # No valid tool call structure, just add message
                    rebuilt.append(base_msg)
            else:
                # No tool calls, just add the message
                rebuilt.append(base_msg)
    
    return rebuilt
