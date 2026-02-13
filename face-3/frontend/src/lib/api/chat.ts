/**
 * Chat API client for AI Todo Assistant
 * Handles communication with backend chat endpoints
 */
import { apiClient } from './client';
import {
  ChatRequest,
  ChatResponse,
  Message,
  Conversation,
  isChatResponse,
  validateMessageInput,
  sanitizeMessageInput,
  ApiError,
} from '../types/chat';

/**
 * Send a message to the AI assistant and receive a response
 *
 * @param message - User's message text
 * @param conversationId - Optional conversation ID for existing conversations
 * @returns ChatResponse with conversation_id, response text, and tool_calls
 * @throws ApiError if request fails or validation fails
 */
export async function sendMessage(
  message: string,
  conversationId?: number | null
): Promise<ChatResponse> {
  // Validate input
  const validationError = validateMessageInput(message);
  if (validationError) {
    throw new ApiError(400, validationError);
  }

  // Sanitize input
  const sanitizedMessage = sanitizeMessageInput(message);

  // Build request payload
  const requestData: ChatRequest = {
    message: sanitizedMessage,
  };

  // Include conversation_id if provided (for existing conversations)
  if (conversationId !== null && conversationId !== undefined) {
    requestData.conversation_id = conversationId;
  }

  try {
    // Send POST request to chat endpoint
    const response = await apiClient.post<ChatResponse>(
      '/api/v1/chat',
      requestData
    );

    // Validate response structure
    if (!isChatResponse(response)) {
      throw new ApiError(
        500,
        'Invalid response format from server',
        response
      );
    }

    return response;
  } catch (error: any) {
    // Re-throw ApiError instances
    if (error instanceof ApiError) {
      throw error;
    }

    // Handle other errors
    throw new ApiError(
      error.status || 500,
      error.message || 'Failed to send message',
      error
    );
  }
}

/**
 * Load conversation history (messages) for a specific conversation
 *
 * @param conversationId - ID of the conversation to load
 * @returns Array of messages in chronological order
 * @throws ApiError if request fails
 */
export async function loadConversationHistory(
  conversationId: number
): Promise<Message[]> {
  try {
    const response = await apiClient.get<{ messages: Message[] }>(
      `/api/v1/conversations/${conversationId}/messages`
    );

    return response.messages || [];
  } catch (error: any) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new ApiError(
      error.status || 500,
      error.message || 'Failed to load conversation history',
      error
    );
  }
}

/**
 * Fetch list of user's conversations
 *
 * @returns Array of conversations with metadata
 * @throws ApiError if request fails
 */
export async function fetchConversations(): Promise<Conversation[]> {
  try {
    const response = await apiClient.get<{ conversations: Conversation[] }>(
      '/api/v1/conversations'
    );

    return response.conversations || [];
  } catch (error: any) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new ApiError(
      error.status || 500,
      error.message || 'Failed to fetch conversations',
      error
    );
  }
}

/**
 * Delete a conversation
 *
 * @param conversationId - ID of the conversation to delete
 * @throws ApiError if request fails
 */
export async function deleteConversation(
  conversationId: number
): Promise<void> {
  try {
    await apiClient.delete(`/api/v1/conversations/${conversationId}`);
  } catch (error: any) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new ApiError(
      error.status || 500,
      error.message || 'Failed to delete conversation',
      error
    );
  }
}
