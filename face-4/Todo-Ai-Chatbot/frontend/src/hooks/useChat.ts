/**
 * useChat Hook
 * Custom hook for managing chat state and interactions
 */
'use client';

import { useState, useCallback } from 'react';
import {
  Message,
  MessageRole,
  ChatState,
  ApiError,
} from '@/lib/types/chat';
import { sendMessage as sendMessageApi } from '@/lib/api/chat';

interface UseChatReturn {
  // State
  conversationId: number | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  inputValue: string;

  // Actions
  setInputValue: (value: string) => void;
  handleSendMessage: () => Promise<void>;
  clearError: () => void;
  resetConversation: () => void;
}

/**
 * Custom hook for chat functionality
 * Manages conversation state, message sending, and error handling
 */
export function useChat(): UseChatReturn {
  const [state, setState] = useState<ChatState>({
    conversationId: null,
    messages: [],
    isLoading: false,
    error: null,
    inputValue: '',
  });

  /**
   * Update input value
   */
  const setInputValue = useCallback((value: string) => {
    setState((prev) => ({ ...prev, inputValue: value }));
  }, []);

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  /**
   * Reset conversation (start new conversation)
   */
  const resetConversation = useCallback(() => {
    setState({
      conversationId: null,
      messages: [],
      isLoading: false,
      error: null,
      inputValue: '',
    });
  }, []);

  /**
   * Send message to AI assistant
   */
  const handleSendMessage = useCallback(async () => {
    const messageText = state.inputValue.trim();

    // Validate input
    if (!messageText) {
      return;
    }

    // Clear error and set loading state
    setState((prev) => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    // Create optimistic user message
    const userMessage: Message = {
      id: Date.now(), // Temporary ID
      role: MessageRole.USER,
      content: messageText,
      created_at: new Date().toISOString(),
    };

    // Add user message to UI immediately (optimistic update)
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      inputValue: '', // Clear input field
    }));

    try {
      // Send message to backend
      const response = await sendMessageApi(messageText, state.conversationId);

      // Create assistant message from response
      const assistantMessage: Message = {
        id: Date.now() + 1, // Temporary ID
        role: MessageRole.ASSISTANT,
        content: response.response,
        created_at: new Date().toISOString(),
        tool_calls: response.tool_calls,
      };

      // Update state with response
      setState((prev) => ({
        ...prev,
        conversationId: response.conversation_id,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));
    } catch (error) {
      // Handle errors
      let errorMessage = 'Failed to send message. Please try again.';

      if (error instanceof ApiError) {
        if (error.status === 401) {
          errorMessage = 'Your session has expired. Please log in again.';
        } else if (error.status === 400) {
          errorMessage = error.message || 'Invalid message. Please check your input.';
        } else if (error.status === 500) {
          errorMessage = 'Server error. Please try again later.';
        } else if (error.status === 0) {
          errorMessage = 'Network error. Please check your connection.';
        } else {
          errorMessage = error.message || errorMessage;
        }
      }

      // Remove optimistic user message on error
      setState((prev) => ({
        ...prev,
        messages: prev.messages.slice(0, -1),
        isLoading: false,
        error: errorMessage,
        inputValue: messageText, // Restore input value for retry
      }));
    }
  }, [state.inputValue, state.conversationId]);

  return {
    conversationId: state.conversationId,
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    inputValue: state.inputValue,
    setInputValue,
    handleSendMessage,
    clearError,
    resetConversation,
  };
}
