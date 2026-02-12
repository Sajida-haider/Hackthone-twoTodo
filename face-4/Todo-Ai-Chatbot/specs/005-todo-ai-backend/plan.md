# Implementation Plan: Todo AI Chatbot Backend

**Branch**: `005-todo-ai-backend` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-todo-ai-backend/spec.md`

## Summary

Build a stateless AI-powered chatbot backend that enables users to manage their todo tasks through natural language conversations. The backend uses an AI agent to interpret user messages, invoke appropriate task management operations through MCP tools, and maintain conversation history in a persistent database. All state is stored in the database, enabling horizontal scaling and conversation continuity across server restarts.

**Key Approach**:
- Stateless FastAPI backend with no in-memory state
- AI agent (TodoAgent) for natural language understanding
- MCP tools for all task operations (add, list, update, complete, delete)
- Neon PostgreSQL for persistent storage of tasks, conversations, and messages
- JWT authentication for user identity and authorization
- Conversation history loaded from database on each request

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.100+, OpenAI Agents SDK, Official MCP SDK, SQLModel 0.0.14+, Pydantic 2.0+
**Storage**: Neon Serverless PostgreSQL (persistent database for tasks, conversations, messages)
**Testing**: pytest for unit and integration tests, contract tests for API endpoints
**Target Platform**: Linux server (containerized deployment with Docker)
**Project Type**: Web API backend (stateless microservice)
**Performance Goals**:
- API response time < 3 seconds (95th percentile)
- Database queries < 100ms for typical operations
- Support 100 concurrent users without degradation
**Constraints**:
- Stateless architecture (no in-memory state)
- All state persisted in database
- Conversation context loaded on each request
- AI service calls with 10-second timeout
**Scale/Scope**:
- Expected users: 100-1000 concurrent
- Typical conversation length: 5-20 messages
- Typical task volume per user: 10-100 tasks
- ~10-15 Python modules (API routes, models, services, MCP tools, agent)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Phase III Scope (Principle II)
- **Status**: PASS
- **Check**: Feature is within Phase III AI Chatbot scope
- **Evidence**: Backend chat API and AI agent integration is explicitly SPEC-3B in constitution

### ✅ Separation of Concerns (Principle III)
- **Status**: PASS
- **Check**: Backend code in `/backend`, no frontend code, clear layer separation
- **Evidence**: Plan specifies backend-only implementation with separate AI agent, MCP tools, and API layers

### ✅ Authentication & Authorization (Principles IV-VII)
- **Status**: PASS
- **Check**: JWT authentication required, user isolation enforced, shared secret management
- **Evidence**: Spec requires JWT validation on all endpoints (FR-040, FR-041), user_id extraction from token (FR-042, FR-043)

### ✅ RESTful API Standards (Principle VIII)
- **Status**: PASS
- **Check**: API routes prefixed with `/api/`, RESTful design, JSON responses
- **Evidence**: Chat endpoint is POST /api/v1/chat with JSON request/response

### ✅ Database Technology (Principles X-XII)
- **Status**: PASS
- **Check**: Neon PostgreSQL, SQLModel ORM, schema compliance
- **Evidence**: Spec requires persistent database (FR-028), SQLModel for ORM, schema matching Phase III-A models

### ✅ MCP Tool Design (Principle XXVI)
- **Status**: PASS
- **Check**: Stateless MCP tools, user_id parameter, single-purpose operations
- **Evidence**: Spec defines 5 MCP tools (FR-016 to FR-020), all stateless (FR-022), user_id required (FR-021)

### ✅ Stateless Agent Architecture (Principle XXVII)
- **Status**: PASS
- **Check**: AI agent is stateless, conversation context loaded from database
- **Evidence**: Spec requires no in-memory state (FR-035, FR-036), load history from DB (FR-004)

### ✅ Conversation Persistence (Principle XXVIII)
- **Status**: PASS
- **Check**: All messages persisted in database before returning
- **Evidence**: Spec requires storing user messages and assistant responses (FR-005, FR-029)

### ✅ Natural Language Intent Mapping (Principle XXIX)
- **Status**: PASS
- **Check**: AI agent maps natural language to MCP tools, handles ambiguity
- **Evidence**: Spec requires understanding natural language (FR-010), deciding which tool to invoke (FR-011), asking for clarification (FR-026)

### ✅ AI Agent Behavior (Principle XXX)
- **Status**: PASS
- **Check**: Consistent behavior rules, confirmations, error handling
- **Evidence**: Spec requires friendly responses (FR-012), error handling (FR-013, FR-025), action confirmations (FR-024)

**Overall Gate Status**: ✅ PASSED - All constitution checks satisfied

## Project Structure

### Documentation (this feature)

```text
specs/005-todo-ai-backend/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── chat.py          # POST /api/v1/chat endpoint
│   │   └── dependencies.py      # JWT validation, user extraction
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py              # Task SQLModel (from Phase III-A)
│   │   ├── conversation.py      # Conversation SQLModel
│   │   └── message.py           # Message SQLModel
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py          # Database connection and session management
│   │   └── conversation.py      # Conversation history loading/saving
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── todo_agent.py        # TodoAgent definition and configuration
│   │   └── skills.py            # Task Management and Interaction skills
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py            # MCP server initialization
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── add_task.py      # add_task MCP tool
│   │       ├── list_tasks.py    # list_tasks MCP tool
│   │       ├── update_task.py   # update_task MCP tool
│   │       ├── complete_task.py # complete_task MCP tool
│   │       └── delete_task.py   # delete_task MCP tool
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py              # Pydantic schemas for chat API
│   │   └── task.py              # Pydantic schemas for task operations
│   ├── config.py                # Configuration (env vars, settings)
│   └── main.py                  # FastAPI application entry point
└── tests/
    ├── unit/
    │   ├── test_mcp_tools.py    # Unit tests for MCP tools
    │   ├── test_agent.py        # Unit tests for TodoAgent
    │   └── test_services.py     # Unit tests for services
    ├── integration/
    │   ├── test_chat_api.py     # Integration tests for chat endpoint
    │   └── test_conversation.py # Integration tests for conversation flow
    └── conftest.py              # pytest fixtures and configuration
```

**Structure Decision**: Backend-only web API structure with clear separation between API routes, database models, business services, AI agent logic, and MCP tools. This structure supports the stateless architecture by keeping concerns separated and making it easy to test each layer independently.

## Complexity Tracking

> **No violations detected** - All constitution checks passed without requiring justification.

## Phase 0: Research & Technology Decisions

### Research Topics

1. **OpenAI Agents SDK Integration**
   - How to initialize and configure an AI agent
   - How to attach skills to an agent
   - How to register MCP tools with the agent runner
   - How to pass conversation context to the agent
   - Error handling patterns for AI service failures

2. **MCP Server Setup**
   - Official MCP SDK installation and initialization
   - MCP tool definition patterns (parameters, return types)
   - Stateless tool implementation best practices
   - Tool registration with agent runtime
   - Error handling and result formatting

3. **Stateless Architecture Patterns**
   - Loading conversation history efficiently
   - Managing database connections in stateless services
   - Horizontal scaling considerations
   - Session management without in-memory state
   - Performance optimization for repeated database loads

4. **Natural Language Processing**
   - Intent extraction from user messages
   - Parameter parsing from natural language
   - Ambiguity detection and clarification strategies
   - Context awareness across conversation turns
   - Error recovery and user guidance

5. **Database Schema Design**
   - Conversation and Message model relationships
   - Efficient querying patterns for conversation history
   - Indexing strategies for performance
   - Integration with existing Task model from Phase III-A
   - Migration strategies

### Technology Decisions

**Decision 1: AI Service - OpenAI Agents SDK**
- **Decision**: Use OpenAI Agents SDK for TodoAgent implementation
- **Rationale**: Official SDK provides robust natural language understanding, built-in tool calling, conversation context management, and production-ready error handling
- **Alternatives**: Custom LLM integration (more control but higher complexity), LangChain (more features but heavier dependency)

**Decision 2: MCP Framework - Official MCP SDK**
- **Decision**: Use Official MCP SDK for tool implementation
- **Rationale**: Standard protocol for AI-tool communication, well-documented, supports stateless operations, integrates with OpenAI Agents SDK
- **Alternatives**: Custom tool protocol (reinventing the wheel), REST API tools (less efficient for agent communication)

**Decision 3: Database ORM - SQLModel**
- **Decision**: Use SQLModel for all database operations
- **Rationale**: Type-safe, Pydantic integration, prevents SQL injection, generates efficient queries, required by constitution (Principle XI)
- **Alternatives**: Raw SQL (security risk, no type safety), SQLAlchemy (more complex, less Pydantic integration)

**Decision 4: API Framework - FastAPI**
- **Decision**: Use FastAPI for REST API implementation
- **Rationale**: Async support, automatic OpenAPI docs, Pydantic validation, JWT middleware support, high performance
- **Alternatives**: Flask (synchronous, less modern), Django (too heavy for API-only service)

**Decision 5: Conversation Storage Strategy**
- **Decision**: Store full conversation history in database, load on each request
- **Rationale**: Enables stateless architecture, supports horizontal scaling, ensures conversation persistence across restarts
- **Alternatives**: In-memory cache (violates stateless principle), Redis session store (adds complexity, still requires DB backup)

**Decision 6: Authentication Strategy**
- **Decision**: JWT token validation using shared secret from Better Auth
- **Rationale**: Stateless authentication, integrates with Phase II auth system, user_id extraction from token claims
- **Alternatives**: Session-based auth (requires state), OAuth (overkill for internal API)

## Phase 1: Design Artifacts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

**Key Entities**:
- **Conversation**: Represents a chat session, contains conversation_id, user_id, created_at, updated_at
- **Message**: Represents a single message, contains message_id, conversation_id, role (user/assistant), content, tool_calls, created_at
- **Task**: Existing model from Phase III-A, contains task_id, user_id, title, description, status, due_date, created_at, updated_at

**Relationships**:
- User (1) → (many) Conversations
- Conversation (1) → (many) Messages
- User (1) → (many) Tasks

### API Contracts

See [contracts/chat-api.yaml](./contracts/chat-api.yaml) for OpenAPI specification.

**Key Endpoint**:
- `POST /api/v1/chat` - Send message to AI assistant and receive response

**Request Schema**:
```json
{
  "message": "string (required, max 2000 chars)",
  "conversation_id": "integer (optional, for continuing existing conversation)"
}
```

**Response Schema**:
```json
{
  "conversation_id": "integer (required)",
  "response": "string (required)",
  "tool_calls": [
    {
      "tool": "string (tool name)",
      "parameters": "object (tool parameters)",
      "result": "string (success/error)",
      "error_message": "string (optional)"
    }
  ]
}
```

### Quick Start Guide

See [quickstart.md](./quickstart.md) for development setup instructions.

## Implementation Phases

### Phase 2: Component Development (via /sp.tasks)

**Note**: Detailed tasks will be generated by `/sp.tasks` command. High-level phases:

1. **Database Setup**
   - Configure Neon PostgreSQL connection
   - Define Conversation and Message SQLModel models
   - Create database migrations
   - Set up database session management

2. **MCP Server & Tools**
   - Initialize MCP server using Official SDK
   - Implement add_task MCP tool
   - Implement list_tasks MCP tool
   - Implement update_task MCP tool
   - Implement complete_task MCP tool
   - Implement delete_task MCP tool
   - Ensure all tools are stateless and database-backed

3. **TodoAgent Implementation**
   - Create TodoAgent using OpenAI Agents SDK
   - Define Task Management Skill
   - Define Interaction Skill
   - Register MCP tools with agent runner
   - Configure agent behavior and prompts

4. **Chat API Development**
   - Implement POST /api/v1/chat endpoint
   - Add JWT authentication middleware
   - Implement conversation history loading
   - Implement user message storage
   - Integrate TodoAgent execution
   - Implement assistant response storage
   - Add error handling and validation

5. **Error Handling & Confirmations**
   - Handle task-not-found errors
   - Handle database connection errors
   - Handle AI service failures
   - Implement friendly error messages
   - Implement action confirmations
   - Add retry logic for transient failures

6. **Testing & Validation**
   - Unit tests for MCP tools
   - Unit tests for TodoAgent
   - Integration tests for chat API
   - Contract tests for API endpoints
   - End-to-end conversation flow tests
   - Performance testing (response time, concurrent users)

## Dependencies

### External Dependencies
- **OpenAI API**: Requires OpenAI API key for Agents SDK
- **Neon PostgreSQL**: Requires Neon database instance and connection string
- **Phase II Auth**: Requires Better Auth JWT secret for token validation
- **Phase III-A Models**: Requires Task model from database schema

### Internal Dependencies
- **Phase II Auth**: Must have JWT authentication working with user_id claims
- **Phase III-A Models**: Must have Task model deployed in database
- **Environment Variables**: Must have OPENAI_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET configured

### NPM/PyPI Dependencies
```python
# requirements.txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlmodel>=0.0.14
pydantic>=2.0.0
python-jose[cryptography]>=3.3.0  # JWT validation
openai-agents-sdk>=1.0.0  # AI agent
mcp-sdk>=1.0.0  # MCP tools
psycopg2-binary>=2.9.0  # PostgreSQL driver
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.24.0  # For testing
```

## Risk Assessment

### High Risk
- **OpenAI API Reliability**: AI service outages or rate limits could block all chat functionality
  - **Mitigation**: Implement timeout handling, retry logic with exponential backoff, graceful error messages to users

- **Stateless Performance**: Loading conversation history on every request may cause latency
  - **Mitigation**: Optimize database queries with proper indexing, implement pagination for very long conversations, monitor query performance

### Medium Risk
- **Natural Language Ambiguity**: AI may misinterpret user intent or extract wrong parameters
  - **Mitigation**: Implement clarification requests, provide examples in agent prompts, log misinterpretations for improvement

- **Database Connection Pool Exhaustion**: High concurrent load may exhaust database connections
  - **Mitigation**: Configure appropriate connection pool size, implement connection timeout handling, monitor connection usage

### Low Risk
- **JWT Token Expiration**: Users may experience authentication errors mid-conversation
  - **Mitigation**: Return clear 401 errors, frontend handles token refresh, document token lifetime expectations

## Success Metrics

From spec.md Success Criteria:

- **SC-001**: Users can create tasks using natural language with 95% success rate for common phrasings
- **SC-002**: System responds to user messages in under 3 seconds (95th percentile)
- **SC-003**: Conversations persist correctly across 100% of server restarts with no data loss
- **SC-004**: Users can complete a 5-message conversation (create, list, complete, list, delete) without errors
- **SC-005**: System correctly interprets user intent and invokes appropriate MCP tool in 90% of cases
- **SC-007**: System handles 100 concurrent users without performance degradation
- **SC-009**: Zero unauthorized access - users can only see and modify their own tasks

## Next Steps

1. ✅ **Phase 0 Complete**: Research documented in research.md
2. ✅ **Phase 1 Complete**: Data model, contracts, and quickstart created
3. ⏭️ **Phase 2**: Run `/sp.tasks` to generate detailed implementation tasks
4. ⏭️ **Implementation**: Execute tasks in priority order
5. ⏭️ **Testing**: Verify all success criteria met
6. ⏭️ **Deployment**: Deploy to staging for integration testing with frontend

---

**Plan Status**: ✅ COMPLETE - Ready for `/sp.tasks` command
