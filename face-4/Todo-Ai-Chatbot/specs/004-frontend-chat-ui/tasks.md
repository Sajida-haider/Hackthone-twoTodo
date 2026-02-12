---
description: "Implementation tasks for Frontend Chat UI"
---

# Tasks: Frontend Chat UI for AI Todo Assistant

**Input**: Design documents from `/specs/004-frontend-chat-ui/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`, `frontend/tests/`
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Install ChatKit dependency: `npm install @chatkit/react` in frontend/
- [ ] T002 [P] Create TypeScript types file: frontend/src/lib/types/chat.ts with Message, MessageRole, ToolCall, ChatRequest, ChatResponse, ChatState interfaces
- [ ] T003 [P] Create API client for chat: frontend/src/lib/api/chat.ts with sendMessage() function
- [ ] T004 [P] Create chat components directory structure: frontend/src/components/chat/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Verify existing API client (frontend/src/lib/api/client.ts) supports JWT token attachment from Phase II
- [ ] T006 [P] Create useChat custom hook skeleton in frontend/src/hooks/useChat.ts with state management structure
- [ ] T007 [P] Create base MessageBubble component in frontend/src/components/chat/MessageBubble.tsx (displays single message)
- [ ] T008 [P] Create TypingIndicator component in frontend/src/components/chat/TypingIndicator.tsx (loading state)
- [ ] T009 [P] Create ErrorMessage component in frontend/src/components/chat/ErrorMessage.tsx (error display)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Send Message to AI Assistant (Priority: P1) 🎯 MVP

**Goal**: Users can type natural language messages and receive AI responses with action confirmations

**Independent Test**: User can open chat page, type "Add a task to buy groceries", send message, and receive confirmation response. Conversation persists for follow-up messages.

### Implementation for User Story 1

- [ ] T010 [P] [US1] Implement sendMessage API method in frontend/src/lib/api/chat.ts (POST /api/v1/chat with JWT)
- [ ] T011 [P] [US1] Implement useChat hook message sending logic in frontend/src/hooks/useChat.ts (handleSendMessage function)
- [ ] T012 [P] [US1] Create MessageInput component in frontend/src/components/chat/MessageInput.tsx (input field + send button)
- [ ] T013 [US1] Implement input validation in MessageInput (max 2000 chars, not empty, disable send when empty)
- [ ] T014 [US1] Add keyboard shortcuts to MessageInput (Enter to send, Shift+Enter for new line)
- [ ] T015 [P] [US1] Create MessageList component in frontend/src/components/chat/MessageList.tsx (renders array of messages)
- [ ] T016 [US1] Implement auto-scroll to bottom in MessageList when new message arrives
- [ ] T017 [US1] Add message role styling in MessageBubble (different styles for user vs assistant)
- [ ] T018 [US1] Display tool_calls in MessageBubble (show action confirmations like "Task added: Buy groceries")
- [ ] T019 [US1] Create ChatInterface container component in frontend/src/components/chat/ChatInterface.tsx (combines MessageList + MessageInput)
- [ ] T020 [US1] Integrate useChat hook with ChatInterface (connect state to UI)
- [ ] T021 [US1] Show TypingIndicator while isLoading is true
- [ ] T022 [US1] Create chat page in frontend/src/app/(dashboard)/chat/page.tsx (renders ChatInterface)
- [ ] T023 [US1] Add conversation_id state management in useChat (store after first message, include in subsequent requests)
- [ ] T024 [US1] Implement optimistic UI update (show user message immediately, then add assistant response)
- [ ] T025 [US1] Add timestamps to messages in MessageBubble (format: "10:30 AM")

### Tests for User Story 1

- [ ] T026 [P] [US1] Unit test for MessageBubble component in frontend/tests/components/chat/MessageBubble.test.tsx
- [ ] T027 [P] [US1] Unit test for MessageInput component in frontend/tests/components/chat/MessageInput.test.tsx (validation, keyboard shortcuts)
- [ ] T028 [P] [US1] Unit test for MessageList component in frontend/tests/components/chat/MessageList.test.tsx (rendering, auto-scroll)
- [ ] T029 [P] [US1] Unit test for useChat hook in frontend/tests/hooks/useChat.test.ts (message sending, state updates)
- [ ] T030 [US1] Integration test for ChatInterface in frontend/tests/components/chat/ChatInterface.test.tsx (full message flow)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can send messages and receive responses

---

## Phase 4: User Story 4 - Handle Errors Gracefully (Priority: P2)

**Goal**: Users receive clear, actionable error messages when something goes wrong

**Independent Test**: Simulate network failure or backend error, verify user sees helpful error message with retry option

**Note**: Implementing error handling (US4) before conversation history (US2) because error handling is needed for all features

### Implementation for User Story 4

- [ ] T031 [P] [US4] Create ApiError class in frontend/src/lib/api/client.ts (extends Error with status code)
- [ ] T032 [US4] Implement error handling in sendMessage API method (catch and throw ApiError)
- [ ] T033 [US4] Add error state management to useChat hook (error message, clearError function)
- [ ] T034 [US4] Implement error categorization in useChat (401 → redirect to login, 400 → show validation error, 500 → show retry)
- [ ] T035 [US4] Display error message in ChatInterface using ErrorMessage component
- [ ] T036 [US4] Add retry button to ErrorMessage component (calls handleSendMessage again)
- [ ] T037 [US4] Implement network error detection (catch fetch errors, show "Connection lost" message)
- [ ] T038 [US4] Add error clearing on successful message send
- [ ] T039 [US4] Show user-friendly error messages (map technical errors to readable text)
- [ ] T040 [US4] Add timeout handling for API requests (30 second timeout)

### Tests for User Story 4

- [ ] T041 [P] [US4] Unit test for ApiError class in frontend/tests/lib/api/client.test.ts
- [ ] T042 [P] [US4] Unit test for ErrorMessage component in frontend/tests/components/chat/ErrorMessage.test.tsx
- [ ] T043 [US4] Integration test for error handling in useChat hook (401, 400, 500, network errors)
- [ ] T044 [US4] Integration test for retry functionality in ChatInterface

**Checkpoint**: At this point, User Stories 1 AND 4 work together - users can send messages and handle errors

---

## Phase 5: User Story 2 - View Conversation History (Priority: P2)

**Goal**: Users can see their complete conversation history with the AI assistant

**Independent Test**: User sends multiple messages, scrolls up to see history, refreshes page, and history is restored from backend

### Implementation for User Story 2

- [ ] T045 [P] [US2] Create loadConversationHistory API method in frontend/src/lib/api/chat.ts (GET /api/v1/conversations/{id}/messages)
- [ ] T046 [US2] Add conversation history loading to useChat hook (useEffect on conversationId change)
- [ ] T047 [US2] Implement scroll position management in MessageList (preserve scroll when loading history)
- [ ] T048 [US2] Add loading state for conversation history (show skeleton or spinner)
- [ ] T049 [US2] Handle empty conversation state (show welcome message when no messages)
- [ ] T050 [US2] Implement message deduplication (prevent duplicate messages when loading history)
- [ ] T051 [US2] Add conversation persistence across page refreshes (load from backend on mount if conversationId in URL)
- [ ] T052 [US2] Format message timestamps with relative time (e.g., "2 minutes ago", "Yesterday")
- [ ] T053 [US2] Add visual separator for different days in conversation history

### Tests for User Story 2

- [ ] T054 [P] [US2] Unit test for loadConversationHistory API method
- [ ] T055 [US2] Integration test for conversation history loading in useChat hook
- [ ] T056 [US2] Integration test for scroll position management in MessageList
- [ ] T057 [US2] Integration test for page refresh persistence

**Checkpoint**: At this point, User Stories 1, 2, AND 4 work together - full conversation history with error handling

---

## Phase 6: User Story 3 - Start New Conversation (Priority: P3)

**Goal**: Users can start a new conversation thread while preserving previous conversations

**Independent Test**: User clicks "New Conversation" button, starts fresh chat, and can later access previous conversations from a list

### Implementation for User Story 3

- [ ] T058 [P] [US3] Create fetchConversations API method in frontend/src/lib/api/chat.ts (GET /api/v1/conversations)
- [ ] T059 [P] [US3] Create ConversationList component in frontend/src/components/chat/ConversationList.tsx
- [ ] T060 [P] [US3] Create useConversation custom hook in frontend/src/hooks/useConversation.ts (manage conversation list state)
- [ ] T061 [US3] Add "New Conversation" button to ChatInterface header
- [ ] T062 [US3] Implement new conversation logic in useChat (reset conversationId to null, clear messages)
- [ ] T063 [US3] Display conversation list in sidebar or dropdown
- [ ] T064 [US3] Implement conversation switching (load selected conversation's messages)
- [ ] T065 [US3] Show conversation preview text in ConversationList (first 50 chars of first message)
- [ ] T066 [US3] Add conversation timestamps to ConversationList (show last updated time)
- [ ] T067 [US3] Highlight active conversation in ConversationList
- [ ] T068 [US3] Add loading state for conversation list
- [ ] T069 [US3] Handle empty conversation list (show "No conversations yet" message)

### Tests for User Story 3

- [ ] T070 [P] [US3] Unit test for ConversationList component
- [ ] T071 [P] [US3] Unit test for useConversation hook
- [ ] T072 [US3] Integration test for new conversation creation
- [ ] T073 [US3] Integration test for conversation switching

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T074 [P] Add responsive design to ChatInterface (mobile and desktop layouts)
- [ ] T075 [P] Implement React.memo for MessageBubble component (performance optimization)
- [ ] T076 [P] Add character counter to MessageInput (show "X/2000" when typing)
- [ ] T077 [P] Implement debouncing for input validation (avoid excessive re-renders)
- [ ] T078 [P] Add accessibility attributes to all components (ARIA labels, keyboard navigation)
- [ ] T079 [P] Style components with Tailwind CSS (consistent design system)
- [ ] T080 [P] Add focus management (auto-focus input after sending message)
- [ ] T081 [P] Implement smooth animations for message appearance (fade in)
- [ ] T082 [P] Add empty state illustrations (when no messages or conversations)
- [ ] T083 [P] Create loading skeletons for message list (better perceived performance)
- [ ] T084 [P] Add copy-to-clipboard button for assistant messages
- [ ] T085 [P] Implement message grouping (group consecutive messages from same sender)
- [ ] T086 [P] Add visual feedback for send button (disable while sending, show checkmark on success)
- [ ] T087 [P] Create comprehensive error boundary for ChatInterface (catch React errors)
- [ ] T088 [P] Add analytics tracking for message sends (optional, if analytics in place)
- [ ] T089 Run full test suite: `npm test` in frontend/
- [ ] T090 Run type checking: `npm run type-check` in frontend/
- [ ] T091 Run linting: `npm run lint` in frontend/
- [ ] T092 Test on mobile devices (iOS Safari, Android Chrome)
- [ ] T093 Test on desktop browsers (Chrome, Firefox, Safari, Edge)
- [ ] T094 Verify all success criteria from spec.md (response time, error handling, persistence)
- [ ] T095 Create demo video or screenshots for documentation
- [ ] T096 Update quickstart.md with any implementation-specific details discovered during development

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (Send Message): Can start after Foundational
  - User Story 4 (Error Handling): Can start after US1 (needs message sending to test errors)
  - User Story 2 (View History): Can start after US1 (needs messages to view)
  - User Story 3 (New Conversation): Can start after US2 (needs conversation concept)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Send Message)**: No dependencies on other stories - fully independent
- **User Story 4 (Error Handling)**: Depends on US1 (needs message sending functionality)
- **User Story 2 (View History)**: Depends on US1 (needs messages to display)
- **User Story 3 (New Conversation)**: Depends on US1 and US2 (needs conversation management)

### Critical Path

The minimum viable product (MVP) requires:
1. Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1: Send Message)

This delivers core chat functionality. US4, US2, and US3 are enhancements.

### Parallel Execution Opportunities

Tasks marked with [P] can be executed in parallel:
- Phase 1: T002, T003, T004 can run in parallel
- Phase 2: T006, T007, T008, T009 can run in parallel
- Phase 3: T010, T011, T012, T015 can run in parallel initially
- Tests: All test tasks within a phase can run in parallel

---

## Task Estimates

**Phase 1 (Setup)**: ~2 hours
**Phase 2 (Foundational)**: ~4 hours
**Phase 3 (US1 - Send Message)**: ~8 hours
**Phase 4 (US4 - Error Handling)**: ~4 hours
**Phase 5 (US2 - View History)**: ~6 hours
**Phase 6 (US3 - New Conversation)**: ~6 hours
**Phase 7 (Polish)**: ~8 hours

**Total Estimated Time**: ~38 hours

**MVP Time** (Phase 1 + 2 + 3): ~14 hours

---

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock API calls and hooks
- Verify component rendering and user interactions
- Target: 80%+ code coverage

### Integration Tests
- Test component interactions
- Test hook behavior with real state management
- Verify API integration (with mocked backend)
- Target: All user flows covered

### Manual Testing
- Test on multiple browsers and devices
- Verify responsive design
- Test error scenarios
- Verify accessibility

---

## Success Criteria Verification

After completing all tasks, verify these success criteria from spec.md:

- [ ] **SC-001**: Users can send message and receive response in < 3 seconds (95th percentile)
- [ ] **SC-002**: Chat interface loads and displays history in < 1 second
- [ ] **SC-003**: 95% of users successfully send first message without errors
- [ ] **SC-004**: Users can complete 5-message conversation without UI issues
- [ ] **SC-005**: Error messages clear enough that 90% of users can resolve issues
- [ ] **SC-006**: Works correctly on mobile and desktop browsers
- [ ] **SC-007**: Conversation history persists across 100% of page refreshes
- [ ] **SC-008**: Can scroll through 100+ messages without performance degradation
- [ ] **SC-009**: 90% of users find interface intuitive (user testing)
- [ ] **SC-010**: Zero data loss - all sent messages stored and retrievable

---

## Notes

### Implementation Order Recommendation

1. **Start with MVP** (Phases 1-3): Get basic chat working first
2. **Add Error Handling** (Phase 4): Essential for good UX
3. **Add History** (Phase 5): Improves user experience
4. **Add Conversations** (Phase 6): Nice-to-have feature
5. **Polish** (Phase 7): Final touches

### Code Review Checkpoints

- After Phase 2: Review foundational components
- After Phase 3: Review MVP functionality
- After Phase 4: Review error handling
- After Phase 7: Final review before deployment

### Performance Considerations

- Use React.memo for MessageBubble (T075)
- Implement virtual scrolling only if 100+ messages cause lag
- Debounce input validation (T077)
- Optimize re-renders with proper dependency arrays

### Accessibility Requirements

- All interactive elements must be keyboard accessible
- ARIA labels for screen readers
- Proper focus management
- Color contrast ratios meet WCAG AA standards
