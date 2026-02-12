/**
 * MessageBubble Component
 * Displays a single message in the chat interface with role-based styling
 */
'use client';

import React from 'react';
import { Message, MessageRole, ToolCall } from '@/lib/types/chat';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === MessageRole.USER;
  const isAssistant = message.role === MessageRole.ASSISTANT;

  // Format timestamp to readable format
  const formatTime = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      });
    } catch {
      return '';
    }
  };

  // Render tool call information
  const renderToolCalls = (toolCalls?: ToolCall[]) => {
    if (!toolCalls || toolCalls.length === 0) return null;

    return (
      <div className="mt-2 space-y-1">
        {toolCalls.map((toolCall, index) => (
          <div
            key={index}
            className={`text-xs px-2 py-1 rounded ${
              toolCall.result === 'success'
                ? 'bg-green-100 text-green-800 border border-green-200'
                : 'bg-red-100 text-red-800 border border-red-200'
            }`}
          >
            <span className="font-medium">
              {toolCall.result === 'success' ? '✓' : '✗'} {toolCall.tool}
            </span>
            {toolCall.error_message && (
              <span className="ml-2">- {toolCall.error_message}</span>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900 border border-gray-200'
        }`}
      >
        {/* Message content */}
        <div className="whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* Tool calls (only for assistant messages) */}
        {isAssistant && renderToolCalls(message.tool_calls)}

        {/* Timestamp */}
        <div
          className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-500'
          }`}
        >
          {formatTime(message.created_at)}
        </div>
      </div>
    </div>
  );
}
