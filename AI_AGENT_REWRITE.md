# AI Agent Flow - Complete Rewrite

## What Changed

### Problem with Old Architecture
1. **Broken conversation history**: Tool call results were stored in database but not properly reconstructed when sending to LLM
2. **Format mismatch**: OpenAI expects specific message format with `tool_calls` and `tool` role messages, but we were injecting results as text
3. **Lost context**: LLM couldn't see dataset IDs from previous searches because tool results weren't in its context
4. **Over-complicated**: Multiple files (mcp_clients.py, agent_service.py, ai_manager.py) with scattered logic

### New Architecture

#### Core Files

**1. `app/core/ai_engine.py`** - Single AI engine class
- `AIEngine`: Main class that handles all AI conversations
- `load_tools()`: Fetches tools from MCP server once
- `call_mcp_tool()`: Executes individual tools via MCP
- `process_conversation()`: Main method - takes messages, calls LLM, handles tools, returns response
- `get_acid_engine()` / `get_tide_engine()`: Singleton instances
- System prompts: Simple, clear instructions

**2. `app/core/conversation_manager.py`** - History rebuilder
- `rebuild_conversation_history()`: Converts database messages to OpenAI format
- **Key innovation**: Reconstructs `tool_calls` arrays and `tool` role messages
- Preserves the exact conversation flow the LLM needs to see

**3. Updated routes** - `acid.py` and `tide.py`
- Much simpler: ~30 lines vs ~100 lines before
- Call `rebuild_conversation_history()` to get proper format
- Call `engine.process_conversation()` to get response
- Save response to database

## How It Works Now

### Message Flow

```
1. User sends message
   ↓
2. Save user message to DB
   ↓
3. Load all messages from DB
   ↓
4. REBUILD history properly:
   [
     {role: "user", content: "find finance data"},
     {role: "assistant", content: "Found 3 datasets...", tool_calls: [...]},
     {role: "tool", tool_call_id: "...", content: "DATASET: Crypto... ID: abc-123..."},
     {role: "user", content: "tell me more about crypto"}
   ]
   ↓
5. Send to AI engine
   ↓
6. LLM sees the dataset ID in tool result!
   ↓
7. LLM calls get_dataset_details_complete with ID: abc-123
   ↓
8. Return final response
```

### Key Improvements

1. **Proper OpenAI message format**: Messages include `tool_calls` arrays and `tool` role responses
2. **LLM has full context**: Can see dataset IDs, previous results, everything
3. **Cleaner code**: 1 engine file vs 4 scattered files
4. **Better debugging**: Clear print statements show what's happening
5. **Lower temperature**: 0.2 instead of 0.7 for more deterministic tool usage

## Files to Delete (obsolete)

- `app/core/mcp_clients.py` - Replaced by ai_engine.py
- `app/services/agent_service.py` - No longer used
- `app/services/ai_manager.py` - No longer used  
- `app/utils/mcp_client.py` - Replaced by ai_engine.py

## Testing

1. Restart backend: `uvicorn app.main:app --reload --port 8000`
2. Start new conversation in UI
3. Ask: "Can you tell me any datasets related to health"
4. ACID should call `search_datasets_semantic`
5. Then ask: "yes please" or "tell me more about patient outcomes"
6. ACID should now call `get_dataset_details_complete` with correct dataset_id

## Why This Works

The critical fix: **We now preserve the EXACT conversation structure OpenAI/Claude expects.**

Before:
```python
# BAD - LLM doesn't see tool results properly
[
  {role: "user", content: "find data"},
  {role: "assistant", content: "Found datasets"},
  {role: "user", content: "[Tool result: DATASET ID=123]"},  # Wrong!
  {role: "user", content: "tell me more"}
]
```

After:
```python
# GOOD - Proper OpenAI format
[
  {role: "user", content: "find data"},
  {role: "assistant", content: "Found datasets", tool_calls: [...]},
  {role: "tool", tool_call_id: "call_1", content: "DATASET ID=123"},  # Right!
  {role: "user", content: "tell me more"}
]
```

The LLM can now parse tool results correctly and extract IDs!
