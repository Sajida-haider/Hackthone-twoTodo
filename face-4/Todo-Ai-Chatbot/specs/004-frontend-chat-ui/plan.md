# Implementation Plan: Frontend Chat UI for AI Todo Assistant

**Branch**: `004-frontend-chat-ui` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-frontend-chat-ui/spec.md`

## Summary

Build a conversational UI using ChatKit that enables users to interact with an AI assistant for managing todos through natural language. The frontend is thin and stateless - all intelligence comes from the backend AI agent. The UI sends user messages to the backend chat API, displays responses, and maintains conversation continuity using conversation_id.

**Key Approach**:
- Use ChatKit library for chat interface components
- Implement centralized API client with JWT authentication
- Store conversation_id in component state (not persistent storage)
- Display user messages, AI responses, and action confirmations
- Handle errors gracefully with retry mechanisms
- Support responsive design for mobile and desktop

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router)
**Primary Dependencies**:
- ChatKit (OpenAI chat UI library)
- Next.js 16+ (App Router)
- React 18+
- Tailwind CSS 3.x
- Better Auth (JWT authentication)

**Storage**: No persistent storage on frontend (conversation state loaded from backend)
**Testing**: Jest + React Testing Library for component tests
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge - last 2 versions), responsive for mobile and desktop
**Project Type**: Web application (frontend only)
**Performance Goals**:
- Initial page load < 1 second
- Message send/receive cycle < 3 seconds
- Smooth scrolling for 100+ message conversations

**Constraints**:
- No AI logic on frontend
- No task state stored on frontend
- All intelligence from backend
- JWT token required for all API calls
- Must work on mobile and desktop

**Scale/Scope**:
- Single chat interface page
- Support for multiple conversations per user
- Handle conversations with 100+ messages
- ~5-10 React components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Phase III Scope (Principle II)
- **Status**: PASS
- **Check**: Feature is within Phase III AI Chatbot scope
- **Evidence**: Frontend chat UI is explicitly part of SPEC-3C

### ✅ Separation of Concerns (Principle III)
- **Status**: PASS
- **Check**: Frontend code in `/frontend`, no business logic, no AI logic
- **Evidence**: Spec clearly states "no AI logic on frontend", "backend is source of truth"

### ✅ Next.js App Router (Principle XIII)
- **Status**: PASS
- **Check**: Must use App Router, Server Components by default
- **Evidence**: Will use App Router structure, Client Components only for interactive chat UI

### ✅ API Client Centralization (Principle XIV)
- **Status**: PASS
- **Check**: All backend calls through centralized client with JWT
- **Evidence**: Plan includes centralized API client with automatic JWT attachment

### ✅ Responsive Design (Principle XV)
- **Status**: PASS
- **Check**: Tailwind CSS only, works on mobile and desktop
- **Evidence**: Spec requires responsive design, success criteria include mobile/desktop support

### ✅ Stateless Frontend (Principle XXVII)
- **Status**: PASS
- **Check**: No conversation state stored on frontend
- **Evidence**: Conversation history loaded from backend on each page load

### ✅ Spec-First Development (Principle I)
- **Status**: PASS
- **Check**: Specification exists and approved before implementation
- **Evidence**: spec.md created and validated

**Overall Gate Status**: ✅ PASSED - All constitution checks satisfied

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-chat-ui/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── chat-api.yaml    # Backend chat API contract
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   └── chat/
│   │   │       └── page.tsx          # Main chat page (Client Component)
│   │   └── layout.tsx                # Root layout
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx     # Main chat container (Client Component)
│   │   │   ├── MessageList.tsx       # Message display (Client Component)
│   │   │   ├── MessageInput.tsx      # Input field and send button (Client Component)
│   │   │   ├── MessageBubble.tsx     # Individual message display
│   │   │   ├── TypingIndicator.tsx   # Loading state indicator
│   │   │   ├── ErrorMessage.tsx      # Error display component
│   │   │   └── ConversationList.tsx  # List of conversations (optional P3)
│   │   └── ui/
│   │       └── (shared UI components)
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts             # Centralized API client
│   │   │   └── chat.ts               # Chat-specific API methods
│   │   └── types/
│   │       └── chat.ts               # TypeScript types for chat
│   └── hooks/
│       ├── useChat.ts                # Chat state management hook
│       └── useConversation.ts        # Conversation management hook
└── tests/
    └── components/
        └── chat/
            ├── ChatInterface.test.tsx
            ├── MessageList.test.tsx
            └── MessageInput.test.tsx
```

**Structure Decision**: Web application structure with frontend-only code. Chat components organized under `components/chat/` for clear separation. API client centralized in `lib/api/` for consistent backend communication. Custom hooks in `hooks/` for reusable chat logic.

## Complexity Tracking

> **No violations detected** - All constitution checks passed without requiring justification.

## Phase 0: Research & Technology Decisions

### Research Topics

1. **ChatKit Integration**
   - How to integrate ChatKit with Next.js App Router
   - ChatKit component API and customization options
   - Message rendering patterns
   - Styling ChatKit components with Tailwind CSS

2. **Real-time Message Handling**
   - Polling vs WebSocket for message updates (start with polling for MVP)
   - Optimistic UI updates for better UX
   - Message retry mechanisms
   - Handling concurrent message sends

3. **State Management**
   - Where to store conversation_id (component state vs URL params)
   - Managing message history in React state
   - Handling conversation switching
   - Persisting scroll position

4. **Error Handling**
   - Network error recovery strategies
   - Token expiration handling
   - Backend error message display
   - Retry logic patterns

5. **Performance Optimization**
   - Virtual scrolling for long conversations
   - Message list rendering optimization
   - Debouncing user input
   - Code splitting strategies

### Technology Decisions

**Decision 1: ChatKit vs Custom Components**
- **Decision**: Use ChatKit library
- **Rationale**: Provides pre-built, accessible chat UI components; reduces development time; follows OpenAI best practices
- **Alternatives**: Custom components (more control but more work)

**Decision 2: State Management**
- **Decision**: React hooks (useState, useEffect) with custom hooks
- **Rationale**: Simple, built-in, sufficient for chat UI; no need for Redux/Zustand
- **Alternatives**: Redux (overkill), Zustand (unnecessary complexity)

**Decision 3: API Communication**
- **Decision**: Fetch API with centralized client
- **Rationale**: Native, well-supported, easy to add JWT headers
- **Alternatives**: Axios (extra dependency), SWR (not needed for chat)

**Decision 4: Message Updates**
- **Decision**: Manual refresh for MVP (polling in future)
- **Rationale**: Simpler implementation, sufficient for initial release
- **Alternatives**: WebSocket (more complex), Server-Sent Events (overkill)

**Decision 5: Conversation Storage**
- **Decision**: Component state only (load from backend on mount)
- **Rationale**: Follows stateless principle, ensures fresh data
- **Alternatives**: LocalStorage (violates stateless principle)

## Phase 1: Design Artifacts

### Data Model (Frontend Perspective)

See [data-model.md](./data-model.md) for complete entity definitions.

**Key Entities**:
- **Message**: Local representation of chat messages
- **Conversation**: Local representation of conversation metadata
- **ChatState**: Component state structure

### API Contracts

See [contracts/chat-api.yaml](./contracts/chat-api.yaml) for OpenAPI specification.

**Key Endpoints**:
- `POST /api/v1/chat` - Send message and receive response

### Quick Start Guide

See [quickstart.md](./quickstart.md) for development setup instructions.

## Implementation Phases

### Phase 2: Component Development (via /sp.tasks)

**Note**: Detailed tasks will be generated by `/sp.tasks` command. High-level phases:

1. **Setup & Configuration**
   - Install ChatKit dependency
   - Configure API client with JWT
   - Set up TypeScript types

2. **Core Chat Components**
   - ChatInterface container
   - MessageList display
   - MessageInput field
   - MessageBubble rendering

3. **State Management**
   - useChat hook for message handling
   - useConversation hook for conversation management
   - Error state handling

4. **API Integration**
   - Chat API client methods
   - Request/response handling
   - Error handling and retry logic

5. **UI Polish**
   - Loading indicators
   - Error messages
   - Responsive design
   - Accessibility

6. **Testing**
   - Component unit tests
   - Integration tests
   - Error scenario tests

## Dependencies

### External Dependencies
- **Backend Chat API**: Requires `POST /api/v1/chat` endpoint (SPEC-3B)
- **Authentication**: Requires Better Auth JWT tokens (Phase II)
- **Database Models**: Requires Conversation and Message models (SPEC-3A)

### Internal Dependencies
- **Phase II Auth**: JWT authentication must be functional
- **Phase III-A Models**: Database schema must be deployed
- **API Client**: HTTP client with JWT headers

### NPM Dependencies
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@chatkit/react": "^1.0.0",
    "tailwindcss": "^3.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "jest": "^29.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  }
}
```

## Risk Assessment

### High Risk
- **ChatKit Compatibility**: ChatKit may not integrate smoothly with Next.js App Router
  - **Mitigation**: Research ChatKit + Next.js patterns early; have fallback to custom components

### Medium Risk
- **Performance with Long Conversations**: Rendering 100+ messages may cause lag
  - **Mitigation**: Implement virtual scrolling if needed; test with large datasets

- **Error Handling Complexity**: Many error scenarios to handle gracefully
  - **Mitigation**: Create comprehensive error handling utilities; test all error paths

### Low Risk
- **Mobile Responsiveness**: Tailwind CSS makes responsive design straightforward
  - **Mitigation**: Test on multiple devices; use Tailwind responsive utilities

## Success Metrics

From spec.md Success Criteria:

- **SC-001**: Users can send message and receive response in < 3 seconds (95th percentile)
- **SC-002**: Chat interface loads and displays history in < 1 second
- **SC-003**: 95% of users successfully send first message without errors
- **SC-006**: Works correctly on mobile and desktop browsers
- **SC-007**: Conversation history persists across 100% of page refreshes
- **SC-009**: 90% of users find interface intuitive (user testing)

## Next Steps

1. ✅ **Phase 0 Complete**: Research documented in research.md
2. ✅ **Phase 1 Complete**: Data model, contracts, and quickstart created
3. ⏭️ **Phase 2**: Run `/sp.tasks` to generate detailed implementation tasks
4. ⏭️ **Implementation**: Execute tasks in priority order
5. ⏭️ **Testing**: Verify all success criteria met
6. ⏭️ **Deployment**: Deploy to staging for user testing

---

**Plan Status**: ✅ COMPLETE - Ready for `/sp.tasks` command
