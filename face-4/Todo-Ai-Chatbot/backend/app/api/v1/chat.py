"""Chat API endpoint for AI assistant."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.schemas.chat import ChatRequest, ChatResponse, ToolCallSchema
from app.api.deps import get_current_user_id
from app.database import get_session
from app.services.conversation import ConversationService
from app.models.message import MessageRole
from app.agent.todo_agent import get_agent


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Send a message to the AI assistant and receive a response.

    This endpoint:
    1. Creates a new conversation or continues an existing one
    2. Saves the user's message
    3. Loads conversation history for context
    4. Executes the AI agent with MCP tools
    5. Saves the assistant's response
    6. Returns the response with tool call details
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = ConversationService.get_conversation(
                request.conversation_id,
                user_id,
                session
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            conversation = ConversationService.create_conversation(user_id, session)

        # Save user message
        ConversationService.save_message(
            conversation.id,
            user_id,
            MessageRole.USER,
            request.message,
            session
        )

        # Load conversation history for context
        history = ConversationService.load_history(
            conversation.id,
            user_id,
            session,
            limit=50
        )

        # Process message with AI agent
        agent = get_agent()
        result = await agent.process_message(
            user_id=user_id,
            message=request.message,
            conversation_history=history[:-1]  # Exclude the message we just added
        )

        # Save assistant response
        ConversationService.save_message(
            conversation.id,
            user_id,
            MessageRole.ASSISTANT,
            result["response"],
            session
        )

        # Format tool calls
        tool_calls = [
            ToolCallSchema(**tc) for tc in result.get("tool_calls", [])
        ]

        return ChatResponse(
            conversation_id=conversation.id,
            response=result["response"],
            tool_calls=tool_calls
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )
