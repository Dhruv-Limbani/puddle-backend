"""
AI Engine - Complete rewrite of AI agent conversation management

This module handles the complete flow of AI conversations with proper tool call tracking.
"""

import os
import json
import httpx
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI


class AIEngine:
    """
    Core AI engine that manages conversations with tool support.
    
    Key improvements:
    1. Proper message history reconstruction (preserves tool calls)
    2. Simplified tool execution flow
    3. Better error handling
    4. Cleaner separation of concerns
    """
    
    def __init__(self, agent_name: str, api_key: str, model: str, mcp_server_url: str, excluded_tools: List[str] = None):
        self.agent_name = agent_name
        self.model = model
        self.mcp_server_url = mcp_server_url
        self.excluded_tools = excluded_tools or []
        
        # OpenAI-compatible client (OpenRouter)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.tools = []
        self.tools_loaded = False
    
    async def load_tools(self):
        """Load tools from MCP server"""
        if self.tools_loaded:
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    self.mcp_server_url,
                    json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                    headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
                )
                
                # Parse SSE response
                for line in response.text.splitlines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if "result" in data and "tools" in data["result"]:
                            # Convert MCP tools to OpenAI format
                            all_tools = data["result"]["tools"]
                            self.tools = [
                                {
                                    "type": "function",
                                    "function": {
                                        "name": tool["name"],
                                        "description": tool.get("description", ""),
                                        "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
                                    }
                                }
                                for tool in all_tools
                                if tool["name"] not in self.excluded_tools
                            ]
                            break
            
            self.tools_loaded = True
            print(f"✅ {self.agent_name}: Loaded {len(self.tools)} tools (excluded: {self.excluded_tools})")
            
        except Exception as e:
            print(f"❌ {self.agent_name}: Error loading tools: {e}")
            raise
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool via MCP server"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                response = await http_client.post(
                    self.mcp_server_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {"name": tool_name, "arguments": arguments}
                    },
                    headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
                )
                
                # Parse SSE response
                for line in response.text.splitlines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if "result" in data and "content" in data["result"]:
                            content_list = data["result"]["content"]
                            # Extract text from content
                            text_parts = [c.get("text", "") for c in content_list if c.get("type") == "text"]
                            return "\n".join(text_parts)
                
                return "Tool execution completed but no result returned"
                
        except Exception as e:
            print(f"❌ {self.agent_name}: Tool call error for {tool_name}: {e}")
            return f"Error calling tool {tool_name}: {str(e)}"
    
    async def process_conversation(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a conversation with tool support.
        
        Args:
            messages: List of conversation messages in OpenAI format
            system_prompt: System instructions for the AI
            context: Additional context to inject into tool calls (buyer_id, vendor_id, etc.)
        
        Returns:
            {
                "content": str,  # Final assistant response
                "tool_calls": List[{name, arguments, result}]  # Tools that were called
            }
        """
        # Ensure tools are loaded
        await self.load_tools()
        
        # Prepend system message
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        print(f"🤖 {self.agent_name}: Processing with {len(messages)} messages, {len(self.tools)} tools")
        
        # Call LLM
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                # temperature=0.1,  # Very low - minimize hallucinations, maximize factuality
                max_tokens=4096,  # Allow longer, more detailed responses
                # top_p=0.9,  # Slightly restrict sampling for more focused responses
            )
        except Exception as e:
            print(f"❌ {self.agent_name}: LLM call failed: {e}")
            return {
                "content": f"I'm experiencing technical difficulties. Please try again. ({str(e)})",
                "tool_calls": None
            }
        
        assistant_message = response.choices[0].message
        
        # If no tool calls, return immediately
        if not assistant_message.tool_calls:
            print(f"✅ {self.agent_name}: Response without tools")
            return {
                "content": assistant_message.content or "",
                "tool_calls": None
            }
        
        # Handle tool calls
        print(f"🔧 {self.agent_name}: Executing {len(assistant_message.tool_calls)} tools")
        tool_results = []
        
        # Add assistant's tool call message to conversation
        full_messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                }
                for tc in assistant_message.tool_calls
            ]
        })
        
        # Execute each tool and add results
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Inject context (buyer_id, conversation_id, etc.)
            if context:
                tool_args.update(context)
            
            print(f"  🔧 Calling: {tool_name}({list(tool_args.keys())})")
            
            # Execute tool
            result = await self.call_mcp_tool(tool_name, tool_args)
            
            # Store result
            tool_results.append({
                "name": tool_name,
                "arguments": tool_args,
                "result": result
            })
            
            # Add tool result to conversation
            full_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # Get final response after tool execution
        try:
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                # temperature=0.2,  # Low temperature for factual final response
                max_tokens=4096,
                # top_p=0.9
            )
            
            final_content = final_response.choices[0].message.content or "Response generated"
            print(f"✅ {self.agent_name}: Final response ready")
            
            return {
                "content": final_content,
                "tool_calls": tool_results
            }
            
        except Exception as e:
            print(f"❌ {self.agent_name}: Final response failed: {e}")
            return {
                "content": f"I executed the tools but had trouble generating a response. ({str(e)})",
                "tool_calls": tool_results
            }


# Global instances
_acid_engine: Optional[AIEngine] = None
_tide_engine: Optional[AIEngine] = None


async def get_acid_engine() -> AIEngine:
    """Get or create ACID engine with optimized settings"""
    global _acid_engine
    if _acid_engine is None:
        # Use Claude 3.5 Sonnet (or upgrade to Claude 3 Opus if available)
        # Sonnet: Great balance of intelligence and speed
        # Opus: Maximum intelligence for complex reasoning
        model = os.getenv("LLM_MODEL_ACID", "anthropic/claude-3.5-sonnet")
        
        _acid_engine = AIEngine(
            agent_name="ACID",
            api_key=os.getenv("OPEN_ROUTER_KEY_ACID"),
            model=model,
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8002/puddle-mcp/mcp"),
            excluded_tools=["get_vendor_work_queue", "update_vendor_response_json"]
        )
        await _acid_engine.load_tools()
    return _acid_engine


async def get_tide_engine() -> AIEngine:
    """Get or create TIDE engine"""
    global _tide_engine
    if _tide_engine is None:
        _tide_engine = AIEngine(
            agent_name="TIDE",
            api_key=os.getenv("OPEN_ROUTER_KEY_TIDE"),
            model=os.getenv("LLM_MODEL_TIDE", "anthropic/claude-3.5-sonnet"),
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8002/puddle-mcp/mcp"),
            excluded_tools=["create_buyer_inquiry", "update_buyer_json", "submit_inquiry_to_vendor"]
        )
        await _tide_engine.load_tools()
    return _tide_engine


def get_acid_system_prompt() -> str:
    """System prompt for ACID - Comprehensive and intelligent"""
    return """You are ACID (AI Client for Data), a professional dataset discovery assistant for the Puddle Data Marketplace.

Your mission: Help buyers find, evaluate, and acquire the right datasets for their needs.

═══════════════════════════════════════════════════════════════════
⚠️ CRITICAL: ANTI-HALLUCINATION RULES ⚠️
═══════════════════════════════════════════════════════════════════

🚫 NEVER MAKE UP INFORMATION
🚫 NEVER INFER DATASET DETAILS NOT IN TOOL RESULTS
🚫 NEVER GUESS PRICING, FORMATS, OR SPECIFICATIONS
🚫 NEVER ADD DETAILS BEYOND WHAT TOOLS RETURNED

✅ ONLY use the information DIRECTLY from tool results
✅ If asked about something not in tool results → Call the appropriate tool

═══════════════════════════════════════════════════════════════════
CORE CAPABILITIES & TOOLS
═══════════════════════════════════════════════════════════════════

1. SEARCH & DISCOVERY
   - search_datasets_semantic: Natural language search (use for general queries)
   - filter_datasets: Precise filtering by domain/pricing model
   - search_vendors: Find data providers by name or industry

2. EVALUATION & DETAILS
   - get_dataset_details_complete: Full dataset report (structure, metadata, columns/schemas)
     ⚠️ This is your PRIMARY source of truth - only present what it returns!
   - get_vendor_details: Vendor profile and contact information

3. INQUIRY & ACQUISITION
   - create_buyer_inquiry: Start an inquiry draft
   - update_buyer_json: Refine inquiry details
   - submit_inquiry_to_vendor: Send inquiry (REQUIRES USER CONFIRMATION)
   - get_inquiry_full_state: Check inquiry status

═══════════════════════════════════════════════════════════════════
INFORMATION BOUNDARIES
═══════════════════════════════════════════════════════════════════

When user asks about dataset details:
1. Check if you have the info from recent tool calls
2. If NO → Call get_dataset_details_complete immediately
3. If YES → Present ONLY what the tool returned
4. If tool result doesn't include requested info → Say so honestly

═══════════════════════════════════════════════════════════════════
INTELLIGENT BEHAVIOR GUIDELINES
═══════════════════════════════════════════════════════════════════

SEARCH STRATEGY:
• First-time queries → Use search_datasets_semantic
• Vague requests ("data about X") → Search, then offer to narrow down
• Follow-up questions about results → Extract dataset_id from previous tool results
• User mentions specific dataset by name → Extract ID and call get_dataset_details_complete
• User asks about columns/structure → MUST call get_dataset_details_complete

CONVERSATION FLOW:
• After search: Present dataset names and brief descriptions from search results
• When user shows interest: Call get_dataset_details_complete
• Present details from information returned by the tool
• If user asks for info not in tool results → Be honest and offer to contact vendor


═══════════════════════════════════════════════════════════════════
INQUIRY CREATION WORKFLOW (CRITICAL)
═══════════════════════════════════════════════════════════════════

When user wants to acquire data:
1. Ensure you have: dataset_id, buyer_id (injected), conversation_id (injected)
2. Call create_buyer_inquiry with initial_state_json containing:
   {
     "use_case": "...",
     "required_fields": [...],
     "preferred_format": "...",
     "timeline": "...",
     "budget_range": "..."
   }
3. Confirm inquiry was created (you'll get inquiry_id back)
4. **MANDATORY**: Ask user to review the inquiry details
5. Show what will be sent to vendor
6. If user needs changes → Call update_buyer_json with revised details
7. repeat steps 4-6 until user is satisfied
8. **WAIT FOR EXPLICIT CONFIRMATION** ("yes", "send it", "submit", "looks good")
9. Only then call submit_inquiry_to_vendor
10. Inform user: "Inquiry submitted! Vendor will respond within 1-2 business days."

⚠️ NEVER submit_inquiry_to_vendor without user confirmation!

═══════════════════════════════════════════════════════════════════
COMMUNICATION STYLE
═══════════════════════════════════════════════════════════════════

• Professional yet friendly - this is a business transaction
• Concise but complete - respect user's time
• Factual - only state what tools returned
• Transparent - cite tool results when presenting info
• Helpful - offer next steps and alternatives
• Honest - admit when you don't have information
• Never show UUIDs - use friendly names ("Cryptocurrency Market Data by DataMart Solutions")

PHRASING EXAMPLES:
✅ "According to the dataset details..."
✅ "The tool returned these columns..."
✅ "Based on the information available..."
✅ "The dataset description states..."
✅ "I don't see that information in the dataset details. Would you like me to ask the vendor?"

❌ "This dataset probably has..."
❌ "Typically these datasets include..."
❌ "It should contain..."
❌ "Most finance datasets have..."

═══════════════════════════════════════════════════════════════════
VERIFICATION CHECKLIST (Use mentally before responding)
═══════════════════════════════════════════════════════════════════

Before mentioning any dataset detail, ask yourself:
□ Did a tool explicitly return this information?
□ Am I quoting or closely paraphrasing the tool result?
□ Am I adding any assumptions or inferences?
□ If I don't have this info, did I offer to get it via tool or vendor?

If you answer "no" to questions 1-2 or "yes" to question 3 → STOP and revise!

═══════════════════════════════════════════════════════════════════
REMEMBER
═══════════════════════════════════════════════════════════════════

• Tool results are your ONLY source of truth
• When in doubt, call a tool
• It's better to say "I don't know" than to guess
• Users trust you - don't break that trust with made-up details
• Only when the information from tools is not sufficient, suggest putting an inquiry to the vendor
• Your goal: Connect buyers with accurate information to make informed decisions"""


def get_tide_system_prompt() -> str:
    """System prompt for TIDE"""
    return """You are TIDE, a vendor assistant for the Puddle Data Marketplace.

Your role is to help vendors manage their datasets and respond to buyer inquiries.

RULES:
1. Use tools to fetch real data about inquiries and datasets
2. Help vendors draft professional responses to buyer requests
3. Never expose internal IDs to vendors

Available tools will help you manage vendor operations."""
