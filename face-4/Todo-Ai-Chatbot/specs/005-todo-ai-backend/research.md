# Research: Todo AI Chatbot Backend

**Feature**: Todo AI Chatbot Backend
**Date**: 2026-02-10
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures research findings and technology decisions for implementing the Todo AI Chatbot Backend. All unknowns from the Technical Context have been investigated, and decisions have been made with clear rationale.

---

## Research Topic 1: OpenAI Agents SDK Integration

### Question
How to initialize, configure, and use the OpenAI Agents SDK for building TodoAgent with natural language understanding and MCP tool integration?

### Research Findings

**Agent Initialization**:
- OpenAI Agents SDK provides `Agent` class for creating AI agents
- Agents are configured with system prompts, tools, and behavior settings
- Supports streaming and non-streaming responses
- Built-in conversation context management

**Skill Attachment**:
- Skills are logical groupings of related tools
- Defined using `@skill` decorator or Skill class
- Can include multiple tools under one skill
- Skills help organize agent capabilities

**MCP Tool Registration**:
- Tools are registered with agent using `@tool` decorator
- Tool functions must have clear docstrings (used by AI for understanding)
- Parameters are automatically extracted from function signatures
- Return values should be structured (dict/Pydantic models)

**Conversation Context**:
- Agent maintains conversation history internally
- Can pass previous messages as context
- Supports system messages, user messages, assistant messages
- Context window management handled automatically

**Error Handling**:
- SDK provides error types for different failure modes
- Timeout handling built-in
- Rate limit errors can be caught and retried
- Network errors should be handled at application level

### Decision

**Use OpenAI Agents SDK with the following configuration**:
- Initialize Agent with system prompt defining TodoAgent behavior
- Attach two skills: TaskManagementSkill and InteractionSkill
- Register 5 MCP tools under TaskManagementSkill
- Pass conversation history from database as context on each request
- Implement 10-second timeout for agent execution
- Handle rate limits with exponential backoff

### Rationale

OpenAI Agents SDK provides production-ready natural language understanding with minimal custom code. The skill-based organization aligns with our architecture (Task Management + Interaction skills). Built-in context management simplifies conversation handling.

### Alternatives Considered

- **Custom LLM Integration**: More control but requires implementing conversation management, tool calling protocol, and error handling from scratch
- **LangChain**: More features (chains, memory, agents) but heavier dependency and more complex than needed for our use case

---

## Research Topic 2: MCP Server Setup

### Question
How to set up MCP server using Official MCP SDK, define stateless tools, and integrate with OpenAI Agents SDK?

### Research Findings

**MCP SDK Installation**:
- Official MCP SDK available via pip: `mcp-sdk`
- Provides `MCPServer` class for server initialization
- Supports both stdio and HTTP transport
- Tools are Python functions with decorators

**Tool Definition Patterns**:
- Use `@mcp.tool()` decorator to register tools
- Function signature defines parameters (type hints required)
- Docstring describes tool purpose (used by AI)
- Return structured data (dict or Pydantic model)
- Raise exceptions for errors (caught by framework)

**Stateless Implementation**:
- Tools should not maintain internal state
- All required data passed as parameters
- Database operations within tool function
- No global variables or class instance state

**Agent Integration**:
- MCP server can be embedded in FastAPI application
- Tools registered with OpenAI Agent via tool registry
- Agent calls tools by name with extracted parameters
- Tool results returned to agent for response generation

**Error Handling**:
- Tools should raise descriptive exceptions
- MCP framework catches exceptions and formats errors
- Error messages passed back to agent
- Agent can retry or ask for clarification

### Decision

**Use Official MCP SDK with embedded server**:
- Initialize MCP server in FastAPI application startup
- Define 5 tools with `@mcp.tool()` decorator
- Each tool accepts user_id as first parameter
- Tools perform database operations using SQLModel
- Return structured results with success/error status
- Raise exceptions with user-friendly messages

### Rationale

Official MCP SDK provides standard protocol for AI-tool communication. Embedded server approach simplifies deployment (no separate process). Stateless tools enable horizontal scaling and align with architecture requirements.

### Alternatives Considered

- **Custom Tool Protocol**: Would require implementing tool calling protocol, parameter extraction, and error handling
- **REST API Tools**: Less efficient for agent communication, adds network overhead, more complex error handling

---

## Research Topic 3: Stateless Architecture Patterns

### Question
How to implement stateless backend that loads conversation history efficiently while supporting horizontal scaling?

### Research Findings

**Conversation History Loading**:
- Load messages from database on each request
- Filter by conversation_id and order by created_at
- Limit to recent N messages (e.g., last 50) for performance
- Use database indexes on conversation_id and created_at

**Database Connection Management**:
- Use connection pooling (SQLModel/SQLAlchemy built-in)
- Configure pool size based on expected concurrency
- Set connection timeout to prevent hanging
- Close connections properly after each request

**Horizontal Scaling**:
- Stateless design allows multiple server instances
- Load balancer distributes requests across instances
- No shared state between instances
- Database is single source of truth

**Session Management**:
- No server-side sessions (stateless)
- User identity from JWT token (stateless auth)
- Conversation_id in request identifies conversation
- No sticky sessions required

**Performance Optimization**:
- Database query optimization (indexes, query planning)
- Limit conversation history to recent messages
- Use database connection pooling
- Consider read replicas for high load

### Decision

**Implement fully stateless architecture**:
- Load conversation history from database on each request
- Use SQLModel connection pooling (default 5-10 connections)
- Limit conversation history to last 50 messages
- Add database indexes on conversation_id and created_at
- No in-memory caching (violates stateless principle)
- Support horizontal scaling with load balancer

### Rationale

Stateless architecture enables horizontal scaling, simplifies deployment, and ensures consistency across server instances. Database persistence provides durability and conversation continuity. Connection pooling provides adequate performance for expected load.

### Alternatives Considered

- **Redis Cache**: Would improve performance but adds complexity, requires cache invalidation, and introduces state
- **In-Memory State**: Violates stateless principle, prevents horizontal scaling, loses data on restart

---

## Research Topic 4: Natural Language Processing

### Question
How to extract intent and parameters from user messages, handle ambiguity, and maintain context awareness?

### Research Findings

**Intent Extraction**:
- OpenAI Agents SDK handles intent extraction automatically
- Agent analyzes user message and selects appropriate tool
- System prompt guides intent mapping
- Tool docstrings help agent understand tool purposes

**Parameter Parsing**:
- Agent extracts parameters from natural language
- Converts to tool function parameter types
- Handles variations in phrasing
- Can ask for missing required parameters

**Ambiguity Detection**:
- Agent can detect when intent is unclear
- Can ask clarifying questions before tool invocation
- System prompt should encourage clarification
- Multiple tool matches trigger clarification

**Context Awareness**:
- Agent receives full conversation history
- Can reference previous messages
- Understands pronouns and references (e.g., "that task")
- Maintains conversation flow

**Error Recovery**:
- Agent can explain errors in user-friendly language
- Can suggest corrections or alternatives
- Can guide users to successful completion
- Learns from conversation context

### Decision

**Rely on OpenAI Agents SDK for NLP**:
- Use system prompt to define TodoAgent behavior
- Provide clear tool docstrings for intent mapping
- Pass full conversation history for context
- Configure agent to ask for clarification when ambiguous
- Implement user-friendly error messages in tool responses

### Rationale

OpenAI Agents SDK provides robust NLP capabilities out of the box. Custom NLP implementation would be complex and error-prone. Agent's built-in context awareness handles references and pronouns effectively.

### Alternatives Considered

- **Custom Intent Classification**: Would require training models, maintaining training data, and handling edge cases
- **Rule-Based Parsing**: Brittle, doesn't handle variations well, requires extensive pattern matching

---

## Research Topic 5: Database Schema Design

### Question
How to design Conversation and Message models, optimize queries, and integrate with existing Task model?

### Research Findings

**Model Relationships**:
- User → Conversations (one-to-many)
- Conversation → Messages (one-to-many)
- User → Tasks (one-to-many, existing from Phase III-A)
- No direct relationship between Conversation and Task

**Efficient Querying**:
- Index on conversation_id for message lookups
- Index on user_id for conversation lookups
- Composite index on (conversation_id, created_at) for ordered message retrieval
- Use LIMIT clause to restrict message count

**Schema Design**:
- Conversation: id (PK), user_id (FK), created_at, updated_at
- Message: id (PK), conversation_id (FK), role (enum), content (text), tool_calls (JSON), created_at
- Task: existing model, no changes needed

**Integration Strategy**:
- Conversation and Message models in same database as Task
- Use same SQLModel session for all operations
- Foreign key constraints ensure referential integrity
- Migrations managed with Alembic

**Performance Considerations**:
- Limit conversation history to recent messages (e.g., 50)
- Use pagination for very long conversations
- Consider archiving old conversations
- Monitor query performance with EXPLAIN

### Decision

**Implement Conversation and Message models**:
- Conversation: id, user_id, created_at, updated_at
- Message: id, conversation_id, role, content, tool_calls (JSONB), created_at
- Add indexes: conversation_id, user_id, (conversation_id, created_at)
- Limit queries to last 50 messages per conversation
- Use Alembic for migrations
- Store tool_calls as JSONB for flexibility

### Rationale

Simple schema design with clear relationships. Indexes optimize common queries (load conversation history, list user conversations). JSONB for tool_calls provides flexibility without complex schema. Limiting message count prevents performance issues.

### Alternatives Considered

- **Separate Tool Calls Table**: More normalized but adds query complexity and JOIN overhead
- **NoSQL Database**: Would require separate database, adds complexity, PostgreSQL JSONB provides similar flexibility

---

## Technology Stack Summary

### Confirmed Technologies

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Language | Python | 3.11+ | Modern Python features, async support, type hints |
| API Framework | FastAPI | 0.100+ | Async, automatic docs, Pydantic validation, high performance |
| AI Agent | OpenAI Agents SDK | 1.0+ | Production-ready NLP, tool calling, context management |
| MCP Framework | Official MCP SDK | 1.0+ | Standard protocol, stateless tools, agent integration |
| ORM | SQLModel | 0.0.14+ | Type-safe, Pydantic integration, prevents SQL injection |
| Database | Neon PostgreSQL | Latest | Serverless, auto-scaling, modern developer experience |
| Auth | JWT (python-jose) | 3.3+ | Stateless auth, integrates with Better Auth |
| Testing | pytest | 7.4+ | Standard Python testing, async support, fixtures |

### Development Dependencies

```python
# requirements.txt
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

## Architecture Decisions Summary

### Decision 1: Stateless Backend with Database Persistence
- **Chosen**: Load all state from database on each request
- **Rejected**: In-memory state, Redis cache
- **Reason**: Enables horizontal scaling, ensures consistency, simplifies deployment

### Decision 2: OpenAI Agents SDK for NLP
- **Chosen**: Use OpenAI Agents SDK for TodoAgent
- **Rejected**: Custom LLM integration, LangChain
- **Reason**: Production-ready, minimal code, robust NLP capabilities

### Decision 3: Embedded MCP Server
- **Chosen**: Embed MCP server in FastAPI application
- **Rejected**: Separate MCP server process, REST API tools
- **Reason**: Simplifies deployment, reduces latency, easier debugging

### Decision 4: SQLModel for Database Operations
- **Chosen**: SQLModel ORM for all database access
- **Rejected**: Raw SQL, SQLAlchemy Core
- **Reason**: Type-safe, prevents SQL injection, Pydantic integration

### Decision 5: JSONB for Tool Calls Storage
- **Chosen**: Store tool_calls as JSONB in Message model
- **Rejected**: Separate ToolCall table, JSON string
- **Reason**: Flexible schema, queryable, no JOIN overhead

---

## Open Questions Resolved

All NEEDS CLARIFICATION items from Technical Context have been resolved:

1. ✅ **Language/Version**: Python 3.11+ confirmed
2. ✅ **Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel confirmed
3. ✅ **Storage**: Neon PostgreSQL confirmed
4. ✅ **Testing**: pytest confirmed
5. ✅ **Target Platform**: Linux server (containerized) confirmed
6. ✅ **Performance Goals**: < 3s response time, < 100ms queries, 100 concurrent users confirmed
7. ✅ **Constraints**: Stateless architecture, database persistence confirmed
8. ✅ **Scale/Scope**: 100-1000 users, 5-20 message conversations, 10-100 tasks per user confirmed

---

## Next Steps

1. ✅ Research complete - All technology decisions documented
2. ⏭️ Phase 1: Create data-model.md with entity definitions
3. ⏭️ Phase 1: Create contracts/chat-api.yaml with OpenAPI spec
4. ⏭️ Phase 1: Create quickstart.md with setup instructions
5. ⏭️ Phase 2: Generate tasks.md with implementation tasks (via /sp.tasks)

---

**Research Status**: ✅ COMPLETE - All unknowns resolved, ready for Phase 1 design
