/**
 * MessageInput Component
 * Input field with send button, validation, and keyboard shortcuts
 */
'use client';

import React, { useState, KeyboardEvent, ChangeEvent } from 'react';
import { MAX_MESSAGE_LENGTH } from '@/lib/types/chat';

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({
  value,
  onChange,
  onSend,
  disabled = false,
  placeholder = 'Type your message...',
}: MessageInputProps) {
  const [isFocused, setIsFocused] = useState(false);

  // Check if send button should be disabled
  const isSendDisabled = disabled || !value.trim() || value.length > MAX_MESSAGE_LENGTH;

  // Handle keyboard shortcuts
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter to send (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isSendDisabled) {
        onSend();
      }
    }
    // Shift+Enter for new line (default behavior, no action needed)
  };

  // Handle input change
  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  // Handle send button click
  const handleSendClick = () => {
    if (!isSendDisabled) {
      onSend();
    }
  };

  // Calculate character count
  const charCount = value.length;
  const isOverLimit = charCount > MAX_MESSAGE_LENGTH;

  return (
    <div className="border-t border-gray-700 bg-gray-800 p-4">
      <div className="flex flex-col space-y-2">
        {/* Input field */}
        <div
          className={`flex items-end space-x-2 border rounded-lg ${
            isFocused ? 'border-blue-500 ring-1 ring-blue-500' : 'border-gray-600'
          } ${isOverLimit ? 'border-red-500 ring-1 ring-red-500' : ''}`}
        >
          <textarea
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={disabled}
            rows={3}
            className="flex-1 resize-none border-0 focus:ring-0 focus:outline-none p-3 rounded-lg bg-gray-900 text-white placeholder-gray-400 disabled:bg-gray-800 disabled:text-gray-500"
            aria-label="Message input"
          />

          {/* Send button */}
          <button
            onClick={handleSendClick}
            disabled={isSendDisabled}
            className={`mb-2 mr-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              isSendDisabled
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
            }`}
            aria-label="Send message"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>

        {/* Character counter */}
        <div className="flex justify-between items-center text-xs">
          <span className="text-gray-400">
            Press Enter to send, Shift+Enter for new line
          </span>
          <span
            className={`${
              isOverLimit ? 'text-red-400 font-medium' : 'text-gray-400'
            }`}
          >
            {charCount} / {MAX_MESSAGE_LENGTH}
          </span>
        </div>
      </div>
    </div>
  );
}
