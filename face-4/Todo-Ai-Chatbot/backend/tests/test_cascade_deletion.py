"""Integration tests for cascade deletion (Phase III)."""
import pytest
from sqlmodel import Session, select

from app.models import Conversation, Message, MessageRole


def test_cascade_delete_conversation_deletes_messages(session: Session, test_user_id: str):
    """Test that deleting a conversation cascades to delete all its messages."""
    # Create conversation
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    conversation_id = conversation.id

    # Create multiple messages
    message1 = Message(
        user_id=test_user_id,
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content="First message"
    )
    message2 = Message(
        user_id=test_user_id,
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content="Second message"
    )
    message3 = Message(
        user_id=test_user_id,
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content="Third message"
    )

    session.add_all([message1, message2, message3])
    session.commit()

    message_ids = [message1.id, message2.id, message3.id]

    # Verify messages exist
    messages_before = session.exec(
        select(Message).where(Message.conversation_id == conversation_id)
    ).all()
    assert len(messages_before) == 3

    # Delete the conversation
    session.delete(conversation)
    session.commit()

    # Verify conversation is deleted
    deleted_conversation = session.get(Conversation, conversation_id)
    assert deleted_conversation is None

    # Verify all messages are also deleted (cascade)
    for message_id in message_ids:
        deleted_message = session.get(Message, message_id)
        assert deleted_message is None

    # Verify no orphaned messages remain
    orphaned_messages = session.exec(
        select(Message).where(Message.conversation_id == conversation_id)
    ).all()
    assert len(orphaned_messages) == 0


def test_cascade_delete_multiple_conversations(session: Session, test_user_id: str):
    """Test cascade deletion works correctly with multiple conversations."""
    # Create two conversations
    conv1 = Conversation(user_id=test_user_id)
    conv2 = Conversation(user_id=test_user_id)
    session.add_all([conv1, conv2])
    session.commit()
    session.refresh(conv1)
    session.refresh(conv2)

    # Add messages to both conversations
    msg1_conv1 = Message(
        user_id=test_user_id,
        conversation_id=conv1.id,
        role=MessageRole.USER,
        content="Conv1 Message1"
    )
    msg2_conv1 = Message(
        user_id=test_user_id,
        conversation_id=conv1.id,
        role=MessageRole.ASSISTANT,
        content="Conv1 Message2"
    )
    msg1_conv2 = Message(
        user_id=test_user_id,
        conversation_id=conv2.id,
        role=MessageRole.USER,
        content="Conv2 Message1"
    )
    msg2_conv2 = Message(
        user_id=test_user_id,
        conversation_id=conv2.id,
        role=MessageRole.ASSISTANT,
        content="Conv2 Message2"
    )

    session.add_all([msg1_conv1, msg2_conv1, msg1_conv2, msg2_conv2])
    session.commit()

    conv1_id = conv1.id
    conv2_id = conv2.id

    # Delete only conv1
    session.delete(conv1)
    session.commit()

    # Verify conv1 and its messages are deleted
    assert session.get(Conversation, conv1_id) is None
    conv1_messages = session.exec(
        select(Message).where(Message.conversation_id == conv1_id)
    ).all()
    assert len(conv1_messages) == 0

    # Verify conv2 and its messages still exist
    assert session.get(Conversation, conv2_id) is not None
    conv2_messages = session.exec(
        select(Message).where(Message.conversation_id == conv2_id)
    ).all()
    assert len(conv2_messages) == 2


def test_cascade_delete_empty_conversation(session: Session, test_user_id: str):
    """Test that deleting a conversation with no messages works correctly."""
    # Create conversation without messages
    conversation = Conversation(user_id=test_user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    conversation_id = conversation.id

    # Delete the conversation
    session.delete(conversation)
    session.commit()

    # Verify conversation is deleted
    deleted_conversation = session.get(Conversation, conversation_id)
    assert deleted_conversation is None


def test_message_cannot_exist_without_conversation(session: Session, test_user_id: str):
    """Test that messages require a valid conversation_id (foreign key constraint)."""
    # Attempt to create a message with non-existent conversation_id
    message = Message(
        user_id=test_user_id,
        conversation_id=99999,  # Non-existent conversation
        role=MessageRole.USER,
        content="Orphaned message"
    )
    session.add(message)

    # This should raise an integrity error
    with pytest.raises(Exception):  # SQLAlchemy IntegrityError
        session.commit()

    session.rollback()
