# Research: Frontend Chat UI Implementation

**Feature**: Frontend Chat UI for AI Todo Assistant
**Date**: 2026-02-10
**Status**: Complete

## Overview

This document consolidates research findings for implementing a ChatKit-based conversational UI for the Todo AI Chatbot. All technical decisions and unknowns from the planning phase have been resolved.

---

## Research Topic 1: ChatKit Integration with Next.js

### Question
How to integrate ChatKit library with Next.js App Router and ensure compatibility with Server/Client Components?

### Findings

**ChatKit Overview**:
- OpenAI's official React chat UI library
- Provides pre-built components: ChatContainer, MessageList, MessageInput, Message
- Supports customization via props and Tailwind CSS
- Handles accessibility and keyboard navigation

**Next.js App Router Integration**:
- ChatKit components require client-side interactivity (event handlers, state)
- Must use `'use client'` directive for all ChatKit components
- Can wrap ChatKit in custom Client Components
- Server Components can pass initial data as props

**Implementation Pattern**:
```typescript
// app/(dashboard)/chat/page.tsx (Server Component)
export default function ChatPage() {
  return <ChatInterface />; // Client Component
}

// components/chat/ChatInterface.tsx (Client Component)
'use client';
import { ChatContainer } from '@chatkit/react';

export function ChatInterface() {
  // ChatKit components here
}
```

### Decision
Use ChatKit with Client Components for interactive chat UI. Server Components only for page layout and initial data fetching.

### Rationale
- ChatKit requires client-side state and event handlers
- Clear separation between Server and Client Components
- Follows Next.js App Router best practices

---

## Research Topic 2: State Management Strategy

### Question
Where to store conversation_id and message history? Component state vs URL params vs localStorage?

### Findings

**Option 1: Component State (useState)**
- Pros: Simple, follows React patterns, no persistence issues
- Cons: Lost on page refresh, requires reload from backend

**Option 2: URL Parameters**
- Pros: Shareable URLs, browser back/forward support
- Cons: Exposes conversation_id in URL, more complex routing

**Option 3: LocalStorage**
- Pros: Persists across refreshes
- Cons: Violates stateless principle, can become stale

**Option 4: Session Storage**
- Pros: Persists during session, cleared on tab close
- Cons: Still violates stateless principle

### Decision
Use component state (useState) with backend reload on mount. Store conversation_id in state after first message.

### Rationale
- Follows constitution principle of stateless frontend
- Ensures fresh data from backend
- Simple implementation
- No stale data issues

### Implementation
```typescript
const [conversationId, setConversationId] = useState<number | null>(null);
const [messages, setMessages] = useState<Message[]>([]);

useEffect(() => {
  // Load conversation history from backend on mount
  if (conversationId) {
    loadConversationHistory(conversationId);
  }
}, [conversationId]);
```

---

## Research Topic 3: API Communication Pattern

### Question
How to structure API client for chat endpoint with JWT authentication and error handling?

### Findings

**Centralized API Client Pattern**:
```typescript
// lib/api/client.ts
class ApiClient {
  private baseURL = process.env.NEXT_PUBLIC_API_URL;

  async request(endpoint: string, options: RequestInit) {
    const token = getAuthToken(); // From Better Auth

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new ApiError(response.status, await response.json());
    }

    return response.json();
  }
}
```

**Chat-Specific Methods**:
```typescript
// lib/api/chat.ts
export async function sendMessage(
  message: string,
  conversationId?: number
): Promise<ChatResponse> {
  return apiClient.request('/api/v1/chat', {
    method: 'POST',
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
}
```

### Decision
Implement centralized API client with automatic JWT attachment and typed methods for chat operations.

### Rationale
- Consistent error handling across all API calls
- Automatic token management
- Type safety with TypeScript
- Easy to add retry logic or logging

---

## Research Topic 4: Error Handling Strategy

### Question
How to handle various error scenarios (network, auth, backend errors) gracefully?

### Findings

**Error Categories**:
1. **Network Errors**: Connection lost, timeout
2. **Authentication Errors**: 401 (token expired/invalid)
3. **Authorization Errors**: 403 (insufficient permissions)
4. **Validation Errors**: 400 (invalid input)
5. **Server Errors**: 500 (backend failure)

**Error Handling Pattern**:
```typescript
try {
  const response = await sendMessage(message, conversationId);
  // Handle success
} catch (error) {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        // Redirect to login
        router.push('/login');
        break;
      case 400:
        // Show validation error
        setError(error.message);
        break;
      case 500:
        // Show retry option
        setError('Something went wrong. Please try again.');
        break;
      default:
        setError('An unexpected error occurred.');
    }
  } else {
    // Network error
    setError('Connection lost. Please check your internet.');
  }
}
```

### Decision
Implement custom ApiError class with status codes and user-friendly error messages. Provide retry mechanism for recoverable errors.

### Rationale
- Clear error categorization
- User-friendly error messages
- Automatic retry for network errors
- Proper auth error handling (redirect to login)

---

## Research Topic 5: Performance Optimization

### Question
How to handle rendering performance for conversations with 100+ messages?

### Findings

**Performance Concerns**:
- Rendering 100+ message components can cause lag
- Scroll position management with dynamic content
- Re-renders on new messages

**Optimization Strategies**:

1. **Virtual Scrolling** (react-window, react-virtualized)
   - Only render visible messages
   - Significant performance improvement for long lists
   - Complexity: Medium

2. **Pagination** (Load more pattern)
   - Load messages in chunks (e.g., 20 at a time)
   - Simple implementation
   - Good UX for very long conversations

3. **React.memo** (Memoization)
   - Prevent unnecessary re-renders of message components
   - Simple to implement
   - Effective for moderate lists

4. **Windowing** (CSS-based)
   - Use CSS overflow and height constraints
   - Browser handles rendering optimization
   - Simplest approach

### Decision
Start with React.memo for message components and CSS-based scrolling. Add virtual scrolling only if performance issues arise.

### Rationale
- YAGNI principle - don't optimize prematurely
- React.memo is simple and effective
- Can add virtual scrolling later if needed
- Success criteria only requires 100 messages (manageable without virtualization)

### Implementation
```typescript
const MessageBubble = React.memo(({ message }: { message: Message }) => {
  return (
    <div className="message">
      {message.content}
    </div>
  );
});
```

---

## Research Topic 6: Message Update Strategy

### Question
How to handle real-time message updates? Polling vs WebSocket vs manual refresh?

### Findings

**Option 1: WebSocket**
- Pros: Real-time, efficient, bidirectional
- Cons: Complex setup, requires backend support, overkill for MVP

**Option 2: Polling**
- Pros: Simple, works with existing REST API
- Cons: Inefficient, delayed updates, unnecessary requests

**Option 3: Manual Refresh**
- Pros: Simplest, no background requests
- Cons: User must manually refresh, not real-time

**Option 4: Server-Sent Events (SSE)**
- Pros: Simpler than WebSocket, server-to-client only
- Cons: Still requires backend changes

### Decision
Manual refresh for MVP (user sends message, gets response). No automatic polling or WebSocket.

### Rationale
- Simplest implementation
- Sufficient for chat use case (user-initiated)
- Can add polling/WebSocket in future if needed
- Follows YAGNI principle

---

## Research Topic 7: Conversation Management

### Question
How to implement conversation switching and history loading?

### Findings

**Conversation List Pattern**:
- Show list of recent conversations (sidebar or dropdown)
- Display preview text and timestamp
- Click to load conversation

**Implementation Approach**:
```typescript
// Load conversation list
const conversations = await fetchConversations();

// Load specific conversation
const messages = await fetchConversationMessages(conversationId);

// Switch conversation
function switchConversation(id: number) {
  setConversationId(id);
  // useEffect will trigger reload
}
```

**Storage Strategy**:
- Conversation list loaded from backend
- Current conversation_id in component state
- Messages loaded on conversation switch

### Decision
Implement conversation list as separate component (P3 priority). Load messages from backend when conversation selected.

### Rationale
- Clear separation of concerns
- Backend is source of truth
- Simple state management
- Aligns with P3 user story priority

---

## Technology Stack Summary

### Confirmed Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16+ | App Router framework |
| React | 18+ | UI library |
| TypeScript | 5.x | Type safety |
| ChatKit | 1.x | Chat UI components |
| Tailwind CSS | 3.x | Styling |
| Better Auth | Latest | JWT authentication |
| Jest | 29+ | Testing framework |
| React Testing Library | 14+ | Component testing |

### NPM Dependencies

**Production**:
- `next@^16.0.0`
- `react@^18.0.0`
- `react-dom@^18.0.0`
- `@chatkit/react@^1.0.0`
- `tailwindcss@^3.0.0`

**Development**:
- `typescript@^5.0.0`
- `@types/react@^18.0.0`
- `@types/node@^20.0.0`
- `jest@^29.0.0`
- `@testing-library/react@^14.0.0`
- `@testing-library/jest-dom@^6.0.0`

---

## Architecture Decisions Summary

### AD-1: Client-Side Chat Components
**Decision**: Use Client Components for all ChatKit integration
**Rationale**: ChatKit requires client-side interactivity; clear separation from Server Components

### AD-2: Stateless Frontend
**Decision**: No persistent storage on frontend; reload from backend on mount
**Rationale**: Follows constitution principle; ensures fresh data; prevents stale state

### AD-3: Centralized API Client
**Decision**: Single API client with automatic JWT attachment
**Rationale**: Consistent error handling; automatic token management; type safety

### AD-4: Component State Management
**Decision**: useState for conversation_id and messages; no Redux/Zustand
**Rationale**: Simple, sufficient for chat UI; no complex state requirements

### AD-5: Manual Message Updates
**Decision**: No polling or WebSocket for MVP
**Rationale**: Simplest implementation; sufficient for user-initiated chat; YAGNI

### AD-6: Performance Strategy
**Decision**: React.memo + CSS scrolling; virtual scrolling only if needed
**Rationale**: Don't optimize prematurely; 100 messages manageable without virtualization

### AD-7: Error Handling
**Decision**: Custom ApiError class with user-friendly messages and retry
**Rationale**: Clear error categorization; good UX; proper auth handling

---

## Open Questions Resolved

All technical unknowns from the planning phase have been resolved:

✅ ChatKit integration pattern defined
✅ State management strategy decided
✅ API communication pattern established
✅ Error handling approach documented
✅ Performance optimization strategy chosen
✅ Message update mechanism selected
✅ Conversation management approach defined

---

## Next Steps

1. ✅ Research complete
2. ⏭️ Create data-model.md (Phase 1)
3. ⏭️ Create contracts/chat-api.yaml (Phase 1)
4. ⏭️ Create quickstart.md (Phase 1)
5. ⏭️ Run /sp.tasks to generate implementation tasks
