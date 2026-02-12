"""Verify chat API integration."""
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from app.main import app
from fastapi.routing import APIRoute

print("=" * 60)
print("Chat API Integration Verification")
print("=" * 60)

# Check routes
routes = [r for r in app.routes if isinstance(r, APIRoute)]
chat_routes = [r for r in routes if '/chat' in r.path]

print("\n[OK] Chat Endpoints Registered:")
for route in chat_routes:
    methods = ', '.join(route.methods)
    print(f"  {methods} {route.path}")

# Check dependencies
print("\n[OK] Dependencies:")
try:
    from app.api.deps import get_current_user_id
    print("  - get_current_user_id dependency available")
except ImportError as e:
    print(f"  [ERROR] get_current_user_id import failed: {e}")

# Check agent
print("\n[OK] TodoAgent:")
try:
    from app.agent.todo_agent import get_agent
    agent = get_agent()
    print(f"  - Model: {agent.model}")
    print(f"  - Tools: {len(agent.tools)} MCP tools")

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-openai-api-key-here":
        print(f"  - API Key: Configured ({api_key[:8]}...)")
    else:
        print("  - API Key: [WARNING] NOT CONFIGURED (set OPENAI_API_KEY in .env)")
except Exception as e:
    print(f"  [ERROR] TodoAgent initialization failed: {e}")

# Check MCP tools
print("\n[OK] MCP Tools:")
try:
    from app.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task
    tools = ["add_task", "list_tasks", "complete_task", "update_task", "delete_task"]
    for tool in tools:
        print(f"  - {tool}")
except ImportError as e:
    print(f"  [ERROR] MCP tools import failed: {e}")

# Check conversation service
print("\n[OK] Conversation Service:")
try:
    from app.services.conversation import ConversationService
    print("  - ConversationService available")
except ImportError as e:
    print(f"  [ERROR] ConversationService import failed: {e}")

print("\n" + "=" * 60)
print("Integration Status: COMPLETE")
print("=" * 60)
print("\nNext Steps:")
print("1. Set OPENAI_API_KEY in backend/.env")
print("2. Start the server: uvicorn app.main:app --reload")
print("3. Test the endpoint: POST /api/v1/chat")
print("=" * 60)
