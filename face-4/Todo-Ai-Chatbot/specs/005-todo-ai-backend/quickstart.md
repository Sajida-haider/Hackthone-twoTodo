# Quick Start Guide: Todo AI Chatbot Backend

**Feature**: Todo AI Chatbot Backend
**Date**: 2026-02-10
**Audience**: Developers setting up local development environment

## Overview

This guide walks you through setting up the Todo AI Chatbot Backend for local development. You'll configure the database, install dependencies, set up environment variables, and run the development server.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **pip** package manager
- **Git** for version control
- **Neon PostgreSQL** account and database instance
- **OpenAI API** account and API key
- **Better Auth** JWT secret (from Phase II frontend setup)

---

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd Todo-Ai-Chatbot
git checkout 005-todo-ai-backend
```

---

## Step 2: Set Up Python Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

---

## Step 3: Install Dependencies

Install required Python packages:

```bash
cd backend
pip install -r requirements.txt
```

**requirements.txt** should contain:
```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlmodel>=0.0.14
pydantic>=2.0.0
python-jose[cryptography]>=3.3.0
openai-agents-sdk>=1.0.0
mcp-sdk>=1.0.0
psycopg2-binary>=2.9.0
alembic>=1.12.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

---

## Step 4: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env

# Database Configuration
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# OpenAI Configuration
OPENAI_API_KEY=sk-...your-api-key...

# Authentication Configuration
BETTER_AUTH_SECRET=your-shared-secret-from-phase-ii

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
```

**Important Notes**:
- `DATABASE_URL`: Get this from your Neon PostgreSQL dashboard
- `OPENAI_API_KEY`: Get this from OpenAI API dashboard
- `BETTER_AUTH_SECRET`: Must match the secret used in Phase II frontend (Better Auth)
- Never commit `.env` file to version control (add to `.gitignore`)

---

## Step 5: Set Up Database

### Initialize Alembic (First Time Only)

If Alembic is not yet initialized:

```bash
cd backend
alembic init alembic
```

### Configure Alembic

Edit `alembic/env.py` to use your SQLModel models:

```python
from src.models import *  # Import all models
from src.config import settings

# Set target metadata
target_metadata = SQLModel.metadata

# Set database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

### Create Migration

Generate migration for Conversation and Message models:

```bash
alembic revision --autogenerate -m "Add conversations and messages tables"
```

### Run Migration

Apply migration to database:

```bash
alembic upgrade head
```

### Verify Tables

Check that tables were created:

```bash
# Connect to your Neon database and verify:
# - conversations table exists
# - messages table exists
# - Foreign keys are set up correctly
# - Indexes are created
```

---

## Step 6: Run Development Server

Start the FastAPI development server:

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

**Server will start at**: `http://localhost:8001`

**API Documentation**: `http://localhost:8001/docs` (Swagger UI)

---

## Step 7: Verify Setup

### Check Health Endpoint

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Test Chat Endpoint (with JWT)

First, get a JWT token from the Phase II frontend (login as a user).

Then test the chat endpoint:

```bash
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Add a task to test the API"
  }'
```

Expected response:
```json
{
  "conversation_id": 1,
  "response": "I've added the task 'Test the API' to your list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "Test the API"},
      "result": "success",
      "error_message": null
    }
  ]
}
```

---

## Step 8: Run Tests

Run the test suite to verify everything is working:

```bash
cd backend
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

View coverage report:
```bash
# Open htmlcov/index.html in browser
```

---

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   └── chat.py          # Chat endpoint
│   │   └── dependencies.py      # JWT validation
│   ├── models/
│   │   ├── conversation.py      # Conversation model
│   │   ├── message.py           # Message model
│   │   └── task.py              # Task model (from Phase III-A)
│   ├── services/
│   │   ├── database.py          # Database connection
│   │   └── conversation.py      # Conversation service
│   ├── agent/
│   │   ├── todo_agent.py        # TodoAgent
│   │   └── skills.py            # Agent skills
│   ├── mcp/
│   │   ├── server.py            # MCP server
│   │   └── tools/               # MCP tools
│   ├── schemas/
│   │   └── chat.py              # Pydantic schemas
│   ├── config.py                # Configuration
│   └── main.py                  # FastAPI app
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── alembic/                     # Database migrations
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables (not in git)
```

---

## Common Issues & Solutions

### Issue: Database Connection Failed

**Symptom**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
- Verify `DATABASE_URL` in `.env` is correct
- Check Neon database is running and accessible
- Ensure SSL mode is set: `?sslmode=require`
- Check firewall/network settings

### Issue: JWT Token Invalid

**Symptom**: `401 Unauthorized` when calling chat endpoint

**Solution**:
- Verify `BETTER_AUTH_SECRET` matches Phase II frontend
- Check JWT token is not expired
- Ensure token is included in Authorization header: `Bearer <token>`
- Verify user_id claim exists in token

### Issue: OpenAI API Error

**Symptom**: `openai.error.AuthenticationError`

**Solution**:
- Verify `OPENAI_API_KEY` is correct
- Check API key has sufficient quota
- Ensure API key has access to required models
- Check OpenAI API status page

### Issue: Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check you're in the `backend/` directory
- Verify Python version is 3.11+

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit code in `backend/src/`

### 3. Run Tests

```bash
pytest
```

### 4. Run Linter

```bash
flake8 src/
black src/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: your feature description"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

---

## Useful Commands

### Database

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_mcp_tools.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

### Development Server

```bash
# Run with auto-reload
uvicorn src.main:app --reload

# Run on specific port
uvicorn src.main:app --port 8001

# Run with debug logging
uvicorn src.main:app --log-level debug
```

---

## Environment Variables Reference

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@host/db` | Yes |
| `OPENAI_API_KEY` | OpenAI API key for Agents SDK | `sk-...` | Yes |
| `BETTER_AUTH_SECRET` | Shared secret for JWT validation | `your-secret-key` | Yes |
| `APP_ENV` | Application environment | `development` or `production` | No |
| `LOG_LEVEL` | Logging level | `INFO`, `DEBUG`, `WARNING` | No |

---

## Next Steps

After completing setup:

1. ✅ Verify all tests pass
2. ✅ Test chat endpoint with JWT token
3. ✅ Review API documentation at `/docs`
4. ⏭️ Implement MCP tools (see tasks.md)
5. ⏭️ Implement TodoAgent (see tasks.md)
6. ⏭️ Integrate with Phase III-C frontend

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **OpenAI Agents SDK**: https://platform.openai.com/docs/agents
- **MCP SDK Documentation**: https://modelcontextprotocol.io/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/

---

## Support

For issues or questions:
- Check specification: `specs/005-todo-ai-backend/spec.md`
- Review implementation plan: `specs/005-todo-ai-backend/plan.md`
- Check data model: `specs/005-todo-ai-backend/data-model.md`
- Review API contract: `specs/005-todo-ai-backend/contracts/chat-api.yaml`

---

**Quick Start Status**: ✅ COMPLETE - Ready for development
