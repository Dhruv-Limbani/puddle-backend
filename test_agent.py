"""
Interactive ACID & TIDE Chat Tester
===================================

This script lets you:
(a) Test if backend routes are working
(b) Chat with ACID (buyer agent) and TIDE (vendor agent) interactively
(c) See changes reflected between both agents

Usage:
    python interactive_chat_test.py

Requirements:
    pip install httpx
"""

import httpx
import asyncio
import json
import os
from typing import Optional

# ==========================================
# CONFIGURATION - UPDATE THESE!
# ==========================================

BASE_URL = "http://localhost:8000/api/v1"

# Update these with your test credentials
BUYER_EMAIL = "buyer1@research.edu"
BUYER_PASSWORD = "password123"

VENDOR_EMAIL = "vendor1@datamart.com"
VENDOR_PASSWORD = "password123"

# ==========================================
# GLOBAL STATE
# ==========================================

class TestState:
    buyer_token: Optional[str] = None
    vendor_token: Optional[str] = None
    buyer_user_id: Optional[str] = None
    vendor_user_id: Optional[str] = None
    buyer_id: Optional[str] = None
    vendor_id: Optional[str] = None
    acid_conversation_id: Optional[str] = None
    tide_conversation_id: Optional[str] = None
    current_inquiry_id: Optional[str] = None

state = TestState()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def api_call(client: httpx.AsyncClient, method: str, endpoint: str, 
                   token: str = None, json_data: dict = None, form_data: dict = None):
    """Make API call and return response"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            if form_data:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = await client.post(url, data=form_data, headers=headers)
            else:
                response = await client.post(url, json=json_data, headers=headers)
        elif method == "PATCH":
            response = await client.patch(url, json=json_data, headers=headers)
        else:
            return None, f"Unknown method: {method}"
        
        return response, None
    except Exception as e:
        return None, str(e)


def print_response(data: dict, label: str = "Response"):
    """Pretty print response data"""
    print(f"\n{'─'*50}")
    print(f"📋 {label}")
    print('─'*50)
    formatted = json.dumps(data, indent=2, default=str)
    # Truncate if too long
    if len(formatted) > 2000:
        print(formatted[:2000])
        print("... (truncated)")
    else:
        print(formatted)


# ==========================================
# TEST FUNCTIONS
# ==========================================

async def test_routes(client: httpx.AsyncClient):
    """Test (a): Check if backend routes are working"""
    
    print("\n" + "="*60)
    print("🔍 TEST A: BACKEND ROUTES CHECK")
    print("="*60)
    
    # Get OpenAPI spec
    response = await client.get(f"{BASE_URL.replace('/api/v1', '')}/openapi.json")
    
    if response.status_code != 200:
        print("❌ Could not fetch API schema")
        return False
    
    paths = response.json().get("paths", {})
    
    # Check ACID routes
    acid_routes = [p for p in paths if "/acid/" in p]
    print(f"\n✅ ACID Routes: {len(acid_routes)}")
    for r in sorted(acid_routes)[:5]:
        print(f"   {r}")
    if len(acid_routes) > 5:
        print(f"   ... and {len(acid_routes) - 5} more")
    
    # Check TIDE routes
    tide_routes = [p for p in paths if "/tide/" in p]
    print(f"\n✅ TIDE Routes: {len(tide_routes)}")
    for r in sorted(tide_routes)[:5]:
        print(f"   {r}")
    if len(tide_routes) > 5:
        print(f"   ... and {len(tide_routes) - 5} more")
    
    # Quick endpoint tests
    print("\n📡 Testing key endpoints...")
    
    tests = [
        ("GET", "/datasets", "Datasets endpoint"),
        ("POST", "/auth/login", "Auth endpoint"),
    ]
    
    for method, endpoint, name in tests:
        try:
            if method == "GET":
                resp = await client.get(f"{BASE_URL}{endpoint}")
            else:
                resp = await client.post(f"{BASE_URL}{endpoint}", data={"username": "test", "password": "test"})
            
            # We just check it responds (even 401/422 is fine - means endpoint exists)
            if resp.status_code < 500:
                print(f"   ✅ {name}: OK (status {resp.status_code})")
            else:
                print(f"   ❌ {name}: Server error {resp.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    return True


async def login_users(client: httpx.AsyncClient):
    """Login both buyer and vendor"""
    
    print("\n" + "="*60)
    print("🔐 LOGGING IN USERS")
    print("="*60)
    
    # Login buyer
    print(f"\n1. Logging in buyer: {BUYER_EMAIL}")
    response, error = await api_call(
        client, "POST", "/auth/login",
        form_data={"username": BUYER_EMAIL, "password": BUYER_PASSWORD}
    )
    
    if error or response.status_code != 200:
        print(f"   ❌ Buyer login failed: {error or response.text}")
        return False
    
    state.buyer_token = response.json().get("access_token")
    print("   ✅ Buyer logged in!")
    
    # Get buyer info
    response, _ = await api_call(client, "GET", "/auth/me", token=state.buyer_token)
    if response and response.status_code == 200:
        user_data = response.json()
        state.buyer_user_id = user_data.get("id")
        print(f"   User ID: {state.buyer_user_id}")
    
    # Get buyer profile
    response, _ = await api_call(client, "GET", "/buyers/me", token=state.buyer_token)
    if response and response.status_code == 200:
        state.buyer_id = response.json().get("id")
        print(f"   Buyer ID: {state.buyer_id}")
    
    # Login vendor
    print(f"\n2. Logging in vendor: {VENDOR_EMAIL}")
    response, error = await api_call(
        client, "POST", "/auth/login",
        form_data={"username": VENDOR_EMAIL, "password": VENDOR_PASSWORD}
    )
    
    if error or response.status_code != 200:
        print(f"   ❌ Vendor login failed: {error or response.text}")
        return False
    
    state.vendor_token = response.json().get("access_token")
    print("   ✅ Vendor logged in!")
    
    # Get vendor info
    response, _ = await api_call(client, "GET", "/auth/me", token=state.vendor_token)
    if response and response.status_code == 200:
        user_data = response.json()
        state.vendor_user_id = user_data.get("id")
        print(f"   User ID: {state.vendor_user_id}")
    
    # Get vendor profile
    response, _ = await api_call(client, "GET", "/vendors/me", token=state.vendor_token)
    if response and response.status_code == 200:
        state.vendor_id = response.json().get("id")
        print(f"   Vendor ID: {state.vendor_id}")
    
    return True


async def setup_conversations(client: httpx.AsyncClient):
    """Create conversations for both agents"""
    
    print("\n" + "="*60)
    print("💬 SETTING UP CONVERSATIONS")
    print("="*60)
    
    # Create ACID conversation
    print("\n1. Creating ACID conversation...")
    response, error = await api_call(
        client, "POST", "/acid/conversations",
        token=state.buyer_token,
        json_data={"user_id": state.buyer_user_id, "title": "Dataset Search Test"}
    )
    
    if response and response.status_code == 201:
        state.acid_conversation_id = response.json().get("id")
        print(f"   ✅ ACID Conversation: {state.acid_conversation_id}")
    else:
        print(f"   ❌ Failed: {error or response.text if response else 'No response'}")
    
    # Create TIDE conversation
    print("\n2. Creating TIDE conversation...")
    response, error = await api_call(
        client, "POST", "/tide/conversations",
        token=state.vendor_token,
        json_data={"user_id": state.vendor_user_id, "title": "Inquiry Management Test"}
    )
    
    if response and response.status_code == 201:
        state.tide_conversation_id = response.json().get("id")
        print(f"   ✅ TIDE Conversation: {state.tide_conversation_id}")
    else:
        print(f"   ❌ Failed: {error or response.text if response else 'No response'}")
    
    return state.acid_conversation_id and state.tide_conversation_id


async def chat_with_acid(client: httpx.AsyncClient, message: str):
    """Send message to ACID and get response"""
    
    print(f"\n👤 BUYER: {message}")
    print("   (Waiting for ACID response...)")
    
    response, error = await api_call(
        client, "POST", f"/acid/conversations/{state.acid_conversation_id}/messages",
        token=state.buyer_token,
        json_data={"content": message}
    )
    
    if response and response.status_code == 200:
        data = response.json()
        ai_message = data.get("ai_message", {})
        content = ai_message.get("content", "No response")
        tool_calls = ai_message.get("tool_call")
        
        print(f"\n🤖 ACID: {content}")
        
        if tool_calls:
            print(f"\n   📦 Tools used: {json.dumps(tool_calls, indent=2)[:500]}")
        
        return data
    else:
        print(f"   ❌ Error: {error or response.text if response else 'No response'}")
        return None


async def chat_with_tide(client: httpx.AsyncClient, message: str):
    """Send message to TIDE and get response"""
    
    print(f"\n👤 VENDOR: {message}")
    print("   (Waiting for TIDE response...)")
    
    response, error = await api_call(
        client, "POST", f"/tide/conversations/{state.tide_conversation_id}/messages",
        token=state.vendor_token,
        json_data={"content": message}
    )
    
    if response and response.status_code == 200:
        data = response.json()
        ai_message = data.get("ai_message", {})
        content = ai_message.get("content", "No response")
        tool_calls = ai_message.get("tool_call")
        
        print(f"\n🤖 TIDE: {content}")
        
        if tool_calls:
            print(f"\n   📦 Tools used: {json.dumps(tool_calls, indent=2)[:500]}")
        
        return data
    else:
        print(f"   ❌ Error: {error or response.text if response else 'No response'}")
        return None


async def interactive_mode(client: httpx.AsyncClient):
    """Interactive chat mode"""
    
    print("\n" + "="*60)
    print("🎮 INTERACTIVE CHAT MODE")
    print("="*60)
    print("""
Commands:
  acid <message>  - Chat with ACID (buyer agent)
  tide <message>  - Chat with TIDE (vendor agent)
  status          - Show current inquiry status
  pending         - Show vendor's pending inquiries
  quit            - Exit

Example:
  acid Find me financial datasets
  tide What inquiries need my attention?
""")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == "status":
                if state.current_inquiry_id:
                    response, _ = await api_call(
                        client, "GET", f"/acid/inquiries/{state.current_inquiry_id}",
                        token=state.buyer_token
                    )
                    if response and response.status_code == 200:
                        print_response(response.json(), "Current Inquiry Status")
                else:
                    print("No active inquiry. Create one by chatting with ACID.")
                continue
            
            if user_input.lower() == "pending":
                response, _ = await api_call(
                    client, "GET", "/tide/inquiries/pending",
                    token=state.vendor_token
                )
                if response and response.status_code == 200:
                    inquiries = response.json()
                    print(f"\n📥 Pending Inquiries: {len(inquiries)}")
                    for inq in inquiries:
                        print(f"   - {inq.get('id')}: {inq.get('status')}")
                continue
            
            if user_input.lower().startswith("acid "):
                message = user_input[5:]
                await chat_with_acid(client, message)
            
            elif user_input.lower().startswith("tide "):
                message = user_input[5:]
                await chat_with_tide(client, message)
            
            else:
                print("Unknown command. Use 'acid <message>' or 'tide <message>'")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


async def run_demo_flow(client: httpx.AsyncClient):
    """Run a complete demo flow"""
    
    print("\n" + "="*60)
    print("🎬 RUNNING DEMO FLOW")
    print("="*60)
    
    # Initialize dataset_id/vendor_id to avoid UnboundLocalError when no datasets found
    dataset_id = None
    vendor_id = None

    # Step 1: ACID searches for datasets
    print("\n--- Step 1: Buyer searches for datasets ---")
    await chat_with_acid(client, "I'm looking for financial market data for risk analysis")
    
    input("\nPress Enter to continue...")
    
    # Step 2: Get dataset list
    print("\n--- Step 2: List available datasets ---")
    response, _ = await api_call(client, "GET", "/datasets?limit=3", token=state.buyer_token)
    if response and response.status_code == 200:
        datasets = response.json()
        if datasets:
            print(f"\n📊 Found {len(datasets)} datasets:")
            for d in datasets:
                print(f"   - {d.get('title')} (ID: {d.get('id')[:8]}...)")
            
            # Use first dataset
            dataset_id = datasets[0].get("id")
            vendor_id = datasets[0].get("vendor_id")
    
    input("\nPress Enter to continue...")
    
    # Step 3: Create inquiry
    print("\n--- Step 3: Buyer creates inquiry ---")
    if state.buyer_id and dataset_id:
        response, _ = await api_call(
            client, "POST", "/acid/inquiries",
            token=state.buyer_token,
            json_data={
                "buyer_id": state.buyer_id,
                "vendor_id": vendor_id,
                "dataset_id": dataset_id,
                "conversation_id": state.acid_conversation_id,
                "buyer_inquiry": {
                    "questions": ["What is the update frequency?", "Can I get a sample?"],
                    "use_case": "Portfolio risk modeling",
                    "budget": "$5,000 - $10,000"
                },
                "status": "submitted"
            }
        )
        if response and response.status_code in [200, 201]:
            state.current_inquiry_id = response.json().get("id")
            print(f"   ✅ Inquiry created: {state.current_inquiry_id}")
    
    input("\nPress Enter to continue...")
    
    # Step 4: TIDE checks pending inquiries
    print("\n--- Step 4: Vendor checks TIDE ---")
    await chat_with_tide(client, "Do I have any new inquiries?")
    
    input("\nPress Enter to continue...")
    
    # Step 5: TIDE gets AI summary
    print("\n--- Step 5: Get AI summary of inquiry ---")
    if state.current_inquiry_id:
        response, _ = await api_call(
            client, "POST", f"/tide/inquiries/{state.current_inquiry_id}/summary",
            token=state.vendor_token
        )
        if response and response.status_code == 200:
            summary = response.json().get("summary", "No summary")
            print(f"\n📝 AI Summary:\n{summary}")
    
    input("\nPress Enter to continue...")
    
    # Step 6: Vendor responds
    print("\n--- Step 6: Vendor responds to inquiry ---")
    if state.current_inquiry_id:
        response, _ = await api_call(
            client, "PATCH", f"/tide/inquiries/{state.current_inquiry_id}/respond",
            token=state.vendor_token,
            json_data={
                "action": "approve",
                "final_price": 7500.00,
                "currency": "USD",
                "terms": "Annual license, includes API access",
                "notes": "We'd be happy to provide a 14-day trial!"
            }
        )
        if response and response.status_code == 200:
            print("   ✅ Vendor responded with pricing!")
            print_response(response.json(), "Vendor Response")
    
    input("\nPress Enter to continue...")
    
    # Step 7: Buyer checks status
    print("\n--- Step 7: Buyer checks inquiry status ---")
    await chat_with_acid(client, f"What's the status of my inquiry {state.current_inquiry_id}?")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE!")
    print("="*60)


async def main():
    """Main entrypoint supporting non-interactive CI/dev runs via env var.

    Set NON_INTERACTIVE=1 to automatically:
      - test routes
      - login users
      - create conversations
      - run the demo flow
    Skips all input() prompts so script can be used in automated diagnostics.
    """

    non_interactive = os.getenv("NON_INTERACTIVE", "0") == "1"

    print("\n" + "="*60)
    print("🧪 ACID & TIDE INTERACTIVE TESTER")
    print("="*60)

    async with httpx.AsyncClient(timeout=120.0) as client:
        routes_ok = await test_routes(client)
        if not routes_ok:
            print("\n❌ Routes check failed. Is your server running?")
            return

        if not non_interactive:
            input("\nPress Enter to continue with login...")

        login_ok = await login_users(client)
        if not login_ok:
            print("\n❌ Login failed. Check credentials and run seed_test_data.py first.")
            return

        conv_ok = await setup_conversations(client)
        if not conv_ok:
            print("\n⚠️ Could not create conversations, but continuing...")

        if non_interactive:
            print("\n🚀 NON_INTERACTIVE mode: running demo flow automatically")
            await run_demo_flow(client)
            return

        print("\n" + "="*60)
        print("What would you like to do?")
        print("="*60)
        print("  1. Run demo flow (automated)")
        print("  2. Interactive mode (manual)")
        print("  3. Exit")

        choice = input("\nSelect (1/2/3): ").strip()

        if choice == "1":
            await run_demo_flow(client)
        elif choice == "2":
            await interactive_mode(client)
        else:
            print("👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())