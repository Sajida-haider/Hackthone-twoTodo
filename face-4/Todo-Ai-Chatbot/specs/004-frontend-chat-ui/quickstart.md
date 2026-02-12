# Quick Start Guide: Frontend Chat UI

**Feature**: Frontend Chat UI for AI Todo Assistant
**Date**: 2026-02-10
**Audience**: Developers implementing the chat interface

## Overview

This guide helps you set up and develop the frontend chat UI for the Todo AI Chatbot. Follow these steps to get the development environment running and start implementing the chat interface.

---

## Prerequisites

Before starting, ensure you have:

- **Node.js**: Version 20.x or higher
- **npm**: Version 10.x or higher (comes with Node.js)
- **Git**: For version control
- **Code Editor**: VS Code recommended (with TypeScript support)
- **Backend API**: Backend chat endpoint must be running (see SPEC-3B)
- **Database**: Phase III-A database models must be deployed

**Check Prerequisites**:
```bash
node --version    # Should be v20.x or higher
npm --version     # Should be v10.x or higher
git --version     # Any recent version
```

---

## Initial Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

This installs:
- Next.js 16+
- React 18+
- TypeScript 5.x
- ChatKit library
- Tailwind CSS
- Testing libraries

### 3. Configure Environment Variables

Create `.env.local` file in the `frontend/` directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth configuration (should already exist from Phase II)
BETTER_AUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

**Important**:
- `NEXT_PUBLIC_API_URL` must point to your running backend server
- `BETTER_AUTH_SECRET` must match the backend secret
- Never commit `.env.local` to version control

### 4. Verify Existing Setup

The frontend should already have from Phase II:
- ✅ Next.js App Router configured
- ✅ Tailwind CSS set up
- ✅ Better Auth integration
- ✅ API client structure

**Verify**:
```bash
# Check if Next.js runs
npm run dev

# Should start on http://localhost:3000
```

---

## Development Workflow

### Running the Development Server

```bash
npm run dev
```

Access the application at: `http://localhost:3000`

**Hot Reload**: Changes to code automatically refresh the browser.

### Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   └── chat/
│   │   │       └── page.tsx          # Chat page (to be created)
│   │   └── layout.tsx
│   ├── components/
│   │   └── chat/                     # Chat components (to be created)
│   │       ├── ChatInterface.tsx
│   │       ├── MessageList.tsx
│   │       ├── MessageInput.tsx
│   │       └── MessageBubble.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts             # API client (exists from Phase II)
│   │   │   └── chat.ts               # Chat API methods (to be created)
│   │   └── types/
│   │       └── chat.ts               # TypeScript types (to be created)
│   └── hooks/
│       └── useChat.ts                # Chat hook (to be created)
└── tests/
    └── components/
        └── chat/                     # Tests (to be created)
```

### Creating New Files

Follow this order for implementation:

1. **Types First**: `src/lib/types/chat.ts`
   - Define TypeScript interfaces
   - See `data-model.md` for complete type definitions

2. **API Client**: `src/lib/api/chat.ts`
   - Implement chat API methods
   - Use existing API client from Phase II

3. **Custom Hook**: `src/hooks/useChat.ts`
   - Manage chat state
   - Handle message sending/receiving

4. **Components**: `src/components/chat/`
   - Start with MessageBubble (simplest)
   - Then MessageList
   - Then MessageInput
   - Finally ChatInterface (container)

5. **Page**: `src/app/(dashboard)/chat/page.tsx`
   - Integrate ChatInterface component

6. **Tests**: `tests/components/chat/`
   - Write tests for each component

---

## Implementation Steps

### Step 1: Create TypeScript Types

Create `src/lib/types/chat.ts`:

```typescript
export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
}

export interface Message {
  id: number;
  role: MessageRole;
  content: string;
  created_at: string;
  tool_calls?: ToolCall[];
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result: 'success' | 'error';
  error_message?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}

export interface ChatState {
  conversationId: number | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  inputValue: string;
}
```

See `data-model.md` for complete type definitions.

### Step 2: Create Chat API Client

Create `src/lib/api/chat.ts`:

```typescript
import { apiClient } from './client'; // Existing from Phase II
import { ChatRequest, ChatResponse } from '@/lib/types/chat';

export async function sendMessage(
  message: string,
  conversationId?: number
): Promise<ChatResponse> {
  const request: ChatRequest = {
    message,
    ...(conversationId && { conversation_id: conversationId }),
  };

  return apiClient.post<ChatResponse>('/api/v1/chat', request);
}
```

### Step 3: Create useChat Hook

Create `src/hooks/useChat.ts`:

```typescript
'use client';

import { useState } from 'react';
import { sendMessage } from '@/lib/api/chat';
import { ChatState, Message, MessageRole } from '@/lib/types/chat';

export function useChat() {
  const [state, setState] = useState<ChatState>({
    conversationId: null,
    messages: [],
    isLoading: false,
    error: null,
    inputValue: '',
  });

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await sendMessage(message, state.conversationId);

      const userMessage: Message = {
        id: Date.now(), // Temporary ID
        role: MessageRole.USER,
        content: message,
        created_at: new Date().toISOString(),
      };

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: MessageRole.ASSISTANT,
        content: response.response,
        created_at: new Date().toISOString(),
        tool_calls: response.tool_calls,
      };

      setState(prev => ({
        ...prev,
        conversationId: response.conversation_id,
        messages: [...prev.messages, userMessage, assistantMessage],
        isLoading: false,
        inputValue: '',
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      }));
    }
  };

  return {
    ...state,
    sendMessage: handleSendMessage,
    setInputValue: (value: string) =>
      setState(prev => ({ ...prev, inputValue: value })),
  };
}
```

### Step 4: Create Chat Components

See `tasks.md` (generated by `/sp.tasks`) for detailed component implementation tasks.

### Step 5: Create Chat Page

Create `src/app/(dashboard)/chat/page.tsx`:

```typescript
import { ChatInterface } from '@/components/chat/ChatInterface';

export default function ChatPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">AI Todo Assistant</h1>
      <ChatInterface />
    </div>
  );
}
```

---

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### Writing Tests

Example test for MessageBubble component:

```typescript
import { render, screen } from '@testing-library/react';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { MessageRole } from '@/lib/types/chat';

describe('MessageBubble', () => {
  it('renders user message correctly', () => {
    const message = {
      id: 1,
      role: MessageRole.USER,
      content: 'Hello',
      created_at: '2026-02-10T10:00:00Z',
    };

    render(<MessageBubble message={message} />);

    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

---

## Debugging

### Common Issues

**Issue 1: API Connection Failed**
- **Symptom**: "Connection lost" error
- **Solution**: Verify backend is running on correct port
- **Check**: `NEXT_PUBLIC_API_URL` in `.env.local`

**Issue 2: Authentication Error**
- **Symptom**: 401 Unauthorized
- **Solution**: Ensure JWT token is valid and not expired
- **Check**: Login again to get fresh token

**Issue 3: CORS Error**
- **Symptom**: "CORS policy" error in browser console
- **Solution**: Backend must allow frontend origin
- **Check**: Backend CORS configuration

**Issue 4: ChatKit Not Rendering**
- **Symptom**: Blank chat interface
- **Solution**: Ensure 'use client' directive on ChatKit components
- **Check**: Component has `'use client';` at top

### Debug Tools

**React DevTools**:
```bash
# Install browser extension
# Chrome: React Developer Tools
# Firefox: React Developer Tools
```

**Network Tab**:
- Open browser DevTools (F12)
- Go to Network tab
- Filter by "Fetch/XHR"
- Inspect API requests/responses

**Console Logging**:
```typescript
console.log('Chat state:', state);
console.log('Sending message:', message);
console.log('API response:', response);
```

---

## Code Style

### TypeScript

- Use strict mode
- Define explicit types (avoid `any`)
- Use interfaces for objects
- Use enums for constants

### React

- Prefer functional components
- Use hooks for state management
- Extract reusable logic into custom hooks
- Keep components small and focused

### Naming Conventions

- Components: PascalCase (`MessageBubble.tsx`)
- Hooks: camelCase with `use` prefix (`useChat.ts`)
- Types: PascalCase (`ChatState`)
- Functions: camelCase (`sendMessage`)
- Constants: UPPER_SNAKE_CASE (`MAX_MESSAGE_LENGTH`)

---

## Performance Tips

### Optimization Strategies

1. **Memoize Components**:
```typescript
const MessageBubble = React.memo(({ message }) => {
  // Component code
});
```

2. **Debounce Input**:
```typescript
const debouncedSend = useMemo(
  () => debounce(handleSendMessage, 300),
  []
);
```

3. **Virtual Scrolling** (if needed):
```typescript
// Only if conversation has 100+ messages
import { FixedSizeList } from 'react-window';
```

---

## Deployment

### Build for Production

```bash
npm run build
```

### Environment Variables

Production `.env.production`:
```bash
NEXT_PUBLIC_API_URL=https://api.todo-chatbot.example.com
BETTER_AUTH_SECRET=production-secret-key
NEXT_PUBLIC_BETTER_AUTH_URL=https://todo-chatbot.example.com
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

---

## Resources

### Documentation

- **Next.js**: https://nextjs.org/docs
- **React**: https://react.dev
- **TypeScript**: https://www.typescriptlang.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **ChatKit**: (Check official documentation)

### Project Documentation

- **Specification**: `specs/004-frontend-chat-ui/spec.md`
- **Implementation Plan**: `specs/004-frontend-chat-ui/plan.md`
- **Data Model**: `specs/004-frontend-chat-ui/data-model.md`
- **API Contract**: `specs/004-frontend-chat-ui/contracts/chat-api.yaml`
- **Research**: `specs/004-frontend-chat-ui/research.md`

### Getting Help

- Check existing Phase II code for patterns
- Review constitution for project principles
- Consult API contract for endpoint details
- Run tests to verify functionality

---

## Next Steps

1. ✅ Complete this quickstart setup
2. ⏭️ Run `/sp.tasks` to generate detailed implementation tasks
3. ⏭️ Implement components in priority order
4. ⏭️ Write tests for each component
5. ⏭️ Test integration with backend
6. ⏭️ Deploy to staging for user testing

---

**Ready to Start**: You now have everything needed to begin implementing the frontend chat UI. Run `/sp.tasks` to generate the detailed task breakdown.
