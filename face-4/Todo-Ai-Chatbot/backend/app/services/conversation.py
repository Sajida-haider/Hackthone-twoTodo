"""Conversation service for managing chat history."""
from typing import List, Dict, Optional
from sqlmodel import Session, select
from datetime import datetime

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.database import get_session


class ConversationService:
    """Service for managing conversations and messages."""

    @staticmethod
    def create_conversation(user_id: str, session: Session) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(conversation_id: int, user_id: str, session: Session) -> Optional[Conversation]:
        """Get a conversation by ID, ensuring it belongs to the user."""
        return session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

    @staticmethod
    def load_history(conversation_id: int, user_id: str, session: Session, limit: int = 50) -> List[Dict[str, str]]:
        """
        Load conversation history for context.

        Returns list of messages in OpenAI format: [{"role": "user", "content": "..."}]
        """
        messages = session.exec(
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        ).all()

        # Reverse to get chronological order (oldest first)
        messages = list(reversed(messages))

        # Convert to OpenAI format
        history = []
        for msg in messages:
            history.append({
                "role": msg.role.value,
                "content": msg.content
            })

        return history

    @staticmethod
    def save_message(
        conversation_id: int,
        user_id: str,
        role: MessageRole,
        content: str,
        session: Session
    ) -> Message:
        """Save a message to the conversation."""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        session.add(message)

        # Update conversation's updated_at timestamp
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)

        session.commit()
        session.refresh(message)
        return message
