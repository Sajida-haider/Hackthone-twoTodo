"""Unit tests for Message model (Phase III)."""
import pytest
from datetime import datetime
from sqlmodel import Session, select

from app.models import Conversation, Message, MessageRole


def test_message_creation_user_role(session: Session, test_user_id: str):
    """Test creating a message with USER role."""
    # Create conversation first
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create user message
    message = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Hello, how can you help me?"
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    assert message.id is not None
    assert message.user_id == test_user_id
    assert message.conversation_id == conversation.id
    assert message.role == MessageRole.USER
    assert message.content == "Hello, how can you help me?"
    assert isinstance(message.created_at, datetime)


def test_message_creation_assistant_role(session: Session, test_user_id: str):
    """Test creating a message with ASSISTANT role."""
    # Create conversation first
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create assistant message
    message = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content="I can help you manage your tasks!"
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    assert message.id is not None
    assert message.role == MessageRole.ASSISTANT
    assert message.content == "I can help you manage your tasks!"


def test_message_role_enum_values(session: Session, test_user_id: str):
    """Test that MessageRole enum has correct values."""
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"


def test_message_content_max_length(session: Session, test_user_id: str):
    """Test message content respects max length of 10000 characters."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    long_content = "A" * 10000
    message = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=long_content
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    assert len(message.content) == 10000
    assert message.content == long_content


def test_message_timestamp_auto_set(session: Session, test_user_id: str):
    """Test that created_at timestamp is automatically set."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    before_creation = datetime.utcnow()

    message = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Test message"
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    after_creation = datetime.utcnow()

    assert before_creation <= message.created_at <= after_creation


def test_message_conversation_relationship(session: Session, test_user_id: str):
    """Test message relationship with conversation."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    message = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Test relationship"
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    # Access conversation through relationship
    assert message.conversation is not None
    assert message.conversation.id == conversation.id
    assert message.conversation.user_id == test_user_id


def test_message_query_by_conversation(session: Session, test_user_id: str):
    """Test querying all messages for a conversation."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create multiple messages
    message1 = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="First message"
    )
    message2 = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content="Second message"
    )
    message3 = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Third message"
    )

    session.add_all([message1, message2, message3])
    session.commit()

    # Query messages for conversation
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    ).all()

    assert len(messages) == 3
    assert messages[0].content == "First message"
    assert messages[1].content == "Second message"
    assert messages[2].content == "Third message"


def test_message_query_by_user(session: Session, test_user_id: str, test_user_id_2: str):
    """Test that messages are isolated by user_id."""
    # Create conversations for two users
    conv1 = Conversation(user_id=test_user_id)
    conv2 = Conversation(user_id=test_user_id_2)
    session.add_all([conv1, conv2])
    session.commit()

    # Create messages for each user
    msg1 = Message(
        user_id=test_user_id,
        conversation_id=conv1.id,
        role=MessageRole.USER,
        content="User 1 message"
    )
    msg2 = Message(
        user_id=test_user_id_2,
        conversation_id=conv2.id,
        role=MessageRole.USER,
        content="User 2 message"
    )
    session.add_all([msg1, msg2])
    session.commit()

    # Query messages for user 1
    user1_messages = session.exec(
        select(Message).where(Message.user_id == test_user_id)
    ).all()

    # Query messages for user 2
    user2_messages = session.exec(
        select(Message).where(Message.user_id == test_user_id_2)
    ).all()

    assert len(user1_messages) == 1
    assert len(user2_messages) == 1
    assert user1_messages[0].content == "User 1 message"
    assert user2_messages[0].content == "User 2 message"


def test_message_ordering_by_created_at(session: Session, test_user_id: str):
    """Test ordering messages by creation time."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create messages in sequence
    msg1 = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="First"
    )
    session.add(msg1)
    session.commit()

    msg2 = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content="Second"
    )
    session.add(msg2)
    session.commit()

    msg3 = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Third"
    )
    session.add(msg3)
    session.commit()

    # Query messages ordered by created_at
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    ).all()

    assert len(messages) == 3
    assert messages[0].content == "First"
    assert messages[1].content == "Second"
    assert messages[2].content == "Third"
    assert messages[0].created_at <= messages[1].created_at <= messages[2].created_at


def test_message_deletion(session: Session, test_user_id: str):
    """Test deleting a message."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    message = Message(
        user_id=test_user_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Message to delete"
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    message_id = message.id

    # Delete the message
    session.delete(message)
    session.commit()

    # Verify message is deleted
    deleted_msg = session.get(Message, message_id)
    assert deleted_msg is None


def test_message_conversation_history(session: Session, test_user_id: str):
    """Test retrieving conversation history with alternating roles."""
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create a conversation history
    messages_data = [
        (MessageRole.USER, "Hello!"),
        (MessageRole.ASSISTANT, "Hi! How can I help you?"),
        (MessageRole.USER, "I need to add a task"),
        (MessageRole.ASSISTANT, "Sure! What's the task title?"),
        (MessageRole.USER, "Buy groceries"),
        (MessageRole.ASSISTANT, "Task 'Buy groceries' has been added!"),
    ]

    for role, content in messages_data:
        message = Message(
            user_id=test_user_id,
            conversation_id=conversation.id,
            role=role,
            content=content
        )
        session.add(message)

    session.commit()

    # Retrieve conversation history
    history = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    ).all()

    assert len(history) == 6
    assert history[0].role == MessageRole.USER
    assert history[1].role == MessageRole.ASSISTANT
    assert history[2].role == MessageRole.USER
    assert history[3].role == MessageRole.ASSISTANT
    assert history[4].role == MessageRole.USER
    assert history[5].role == MessageRole.ASSISTANT
