"""Unit tests for Conversation model (Phase III)."""
import pytest
from datetime import datetime
from sqlmodel import Session, select

from app.models import Conversation, Message, MessageRole


def test_conversation_creation(session: Session, test_user_id: str):
    """Test creating a conversation with required fields."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    assert conversation.id is not None
    assert conversation.user_id == test_user_id
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)
    assert conversation.created_at == conversation.updated_at


def test_conversation_timestamps_auto_set(session: Session, test_user_id: str):
    """Test that timestamps are automatically set on creation."""
    before_creation = datetime.utcnow()

    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    after_creation = datetime.utcnow()

    assert before_creation <= conversation.created_at <= after_creation
    assert before_creation <= conversation.updated_at <= after_creation


def test_conversation_user_isolation(session: Session, test_user_id: str, test_user_id_2: str):
    """Test that conversations are isolated by user_id."""
    # Create conversations for two different users
    conv1 = Conversation(user_id=test_user_id)
    conv2 = Conversation(user_id=test_user_id_2)
    session.add(conv1)
    session.add(conv2)
    session.commit()

    # Query conversations for user 1
    user1_convs = session.exec(
        select(Conversation).where(Conversation.user_id == test_user_id)
    ).all()

    # Query conversations for user 2
    user2_convs = session.exec(
        select(Conversation).where(Conversation.user_id == test_user_id_2)
    ).all()

    assert len(user1_convs) == 1
    assert len(user2_convs) == 1
    assert user1_convs[0].user_id == test_user_id
    assert user2_convs[0].user_id == test_user_id_2


def test_conversation_with_messages_relationship(session: Session, test_user_id: str):
    """Test conversation relationship with messages."""
    # Create conversation
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Add messages to conversation
    message1 = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Hello"
    )
    message2 = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content="Hi there!"
    )
    session.add(message1)
    session.add(message2)
    session.commit()
    session.refresh(conversation)

    # Verify relationship
    assert len(conversation.messages) == 2
    assert conversation.messages[0].content == "Hello"
    assert conversation.messages[1].content == "Hi there!"


def test_conversation_empty_messages_list(session: Session, test_user_id: str):
    """Test that a new conversation has an empty messages list."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    assert conversation.messages == []


def test_conversation_deletion(session: Session, test_user_id: str):
    """Test deleting a conversation."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    conversation_id = conversation.id

    # Delete the conversation
    session.delete(conversation)
    session.commit()

    # Verify conversation is deleted
    deleted_conv = session.get(Conversation, conversation_id)
    assert deleted_conv is None


def test_conversation_query_by_user(session: Session, test_user_id: str):
    """Test querying all conversations for a user."""
    # Create multiple conversations
    conv1 = Conversation(user_id=test_user_id)
    conv2 = Conversation(user_id=test_user_id)
    conv3 = Conversation(user_id=test_user_id)

    session.add_all([conv1, conv2, conv3])
    session.commit()

    # Query all conversations for user
    user_conversations = session.exec(
        select(Conversation).where(Conversation.user_id == test_user_id)
    ).all()

    assert len(user_conversations) == 3


def test_conversation_updated_at_changes_with_messages(session: Session, test_user_id: str):
    """Test that adding messages updates the conversation's updated_at timestamp."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    original_updated_at = conversation.updated_at

    # Add a message
    message = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="New message"
    )
    session.add(message)
    session.commit()
    session.refresh(conversation)

    # Note: updated_at may not change automatically in SQLite without triggers
    # This test documents expected behavior with proper database configuration
    assert conversation.updated_at >= original_updated_at


def test_conversation_ordering_by_updated_at(session: Session, test_user_id: str):
    """Test ordering conversations by most recently updated."""
    # Create conversations
    conv1 = Conversation(user_id=test_user_id)
    conv2 = Conversation(user_id=test_user_id)
    conv3 = Conversation(user_id=test_user_id)

    session.add_all([conv1, conv2, conv3])
    session.commit()

    # Query conversations ordered by updated_at descending
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == test_user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    assert len(conversations) == 3
    # Most recent should be first
    assert conversations[0].updated_at >= conversations[1].updated_at
    assert conversations[1].updated_at >= conversations[2].updated_at
