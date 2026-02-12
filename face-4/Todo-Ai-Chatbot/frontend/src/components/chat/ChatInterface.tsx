/**
 * ChatInterface Component
 * Main chat container that combines MessageList and MessageInput
 */
'use client';

import React from 'react';
import { useChat } from '@/hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ErrorMessage } from './ErrorMessage';

export function ChatInterface() {
  const {
    messages,
    isLoading,
    error,
    inputValue,
    setInputValue,
    handleSendMessage,
    clearError,
    resetConversation,
  } = useChat();

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-gray-800">
        <div>
          <h2 className="text-lg font-semibold text-white">
            AI Todo Assistant
          </h2>
          <p className="text-sm text-gray-400">
            Manage your tasks with natural language
          </p>
        </div>

        {/* New conversation button */}
        {messages.length > 0 && (
          <button
            onClick={resetConversation}
            className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 border border-gray-600 rounded-lg hover:bg-gray-600 transition-colors"
            aria-label="Start new conversation"
          >
            <svg
              className="w-5 h-5 inline-block mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            New Chat
          </button>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="px-4 pt-4">
          <ErrorMessage
            message={error}
            onRetry={handleSendMessage}
            onDismiss={clearError}
          />
        </div>
      )}

      {/* Message list */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Message input */}
      <MessageInput
        value={inputValue}
        onChange={setInputValue}
        onSend={handleSendMessage}
        disabled={isLoading}
        placeholder="Ask me to add tasks, show todos, or anything else..."
      />
    </div>
  );
}
