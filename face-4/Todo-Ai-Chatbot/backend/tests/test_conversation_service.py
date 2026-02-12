"""Unit tests for conversation service."""
import pytest
from app.services.conversation import ConversationService
from app.models.message import MessageRole


def test_create_conversation(test_db, test_user):
    """Test creating a new conversation."""
    conversation = ConversationService.create_conversation(
        test_user["id"],
        test_db
    )

    assert conversation.id is not None
    assert conversation.user_id == test_user["id"]
    assert conversation.created_at is not None
    assert conversation.updated_at is not None


def test_get_conversation(test_db, test_user):
    """Test retrieving a conversation."""
    # Create conversation
    conversation = ConversationService.create_conversation(
        test_user["id"],
        test_db
    )

    # Retrieve it
    retrieved = ConversationService.get_conversation(
        conversation.id,
        test_user["id"],
        test_db
    )

    assert retrieved is not None
    assert retrieved.id == conversation.id
    assert retrieved.user_id == test_user["id"]


def test_get_conversation_wrong_user(test_db, test_user):
    """Test user cannot access another user's conversation."""
    # Create conversation for test user
    conversation = ConversationService.create_conversation(
        test_user["id"],
        test_db
    )

    # Try to retrieve with different user_id
    retrieved = ConversationService.get_conversation(
        conversation.id,
        "other_user_123",
        test_db
    )

    assert retrieved is None


def test_save_message(test_db, test_user):
    """Test saving a message to conversation."""
    conversation = ConversationService.create_conversation(
        test_user["id"],
        test_db
    )

    message = ConversationService.save_message(
        conversation.id,
        test_user["id"],
        MessageRole.USER,
        "Hello, AI!",
        test_db
    )

    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.user_id == test_user["id"]
    assert message.role == MessageRole.USER
    assert message.content == "Hello, AI!"


def test_load_history_empty(test_db, test_user):
    """Test loading history from empty conversation."""
    conversation = ConversationService.create_conversation(
        test_user["id"],
        test_db
    )

    history = ConversationService.load_history(
        conversation.id,
        test_user["id"],
        test_db
    )

    assert history == []


def test_load_history_multiple_messages(test_db, test_user):
    """Test loading conversation history with multiple messages."""
    import time

    conversation = ConversationService.create_conversation(
        test_user["id"],
        test_db
    )

    # Save messages with slight delays to ensure proper ordering
    ConversationService.save_message(
        conversation.id,
        test_user["id"],
        MessageRole.USER,
        "First message",
        test_db
    )
    time.sleep(0.01)

    ConversationService.save_message(
        conversation.id,
        test_user["id"],
        MessageRole.ASSISTANT,
        "First response",
        test_db
    )
    time.sleep(0.01)

    ConversationService.save_message(
        conversation.id,
        test_user["id"],
        MessageRole.USER,
        "Second message",
        test_db
    )

    history = ConversationService.load_history(
        conversation.id,
        test_user["id"],
        test_db
    )

    assert len(history) == 3
    # Messages should be in chronological order (oldest first)
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "First message"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "First response"
    assert history[2]["role"] == "user"
    assert history[2]["content"] == "Second message"


def test_load_history_limit(test_db, test_user):
    """Test loading history with limit."""
    import time

    conversation = ConversationService.create_conversation(
        test_user["id"],
        test_db
    )

    # Save 5 messages with delays to ensure proper ordering
    for i in range(5):
        ConversationService.save_message(
            conversation.id,
            test_user["id"],
            MessageRole.USER,
            f"Message {i}",
            test_db
        )
        time.sleep(0.01)

    # Load with limit of 3
    history = ConversationService.load_history(
        conversation.id,
        test_user["id"],
        test_db,
        limit=3
    )

    assert len(history) == 3
    # Should get the most recent 3 messages in chronological order (oldest of the 3 first)
    assert history[0]["content"] == "Message 2"
    assert history[1]["content"] == "Message 3"
    assert history[2]["content"] == "Message 4"


def test_load_history_user_isolation(test_db, test_user):
    """Test user can only load their own conversation history."""
    conversation = ConversationService.create_conversation(
        test_user["id"],
        test_db
    )

    ConversationService.save_message(
        conversation.id,
        test_user["id"],
        MessageRole.USER,
        "My message",
        test_db
    )

    # Try to load with different user_id
    history = ConversationService.load_history(
        conversation.id,
        "other_user_123",
        test_db
    )

    assert history == []
