"""Integration tests for chat API endpoint."""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "response": "I've added the task for you!",
        "tool_calls": [
            {
                "tool": "add_task",
                "parameters": {"title": "Buy groceries"},
                "result": "success",
                "error_message": None
            }
        ]
    }


@pytest.fixture
def auth_client(client: TestClient, test_user_id: str):
    """Create authenticated test client for chat API."""
    from app.api.deps import get_current_user_id
    from app.main import app

    def get_user_override():
        return test_user_id

    app.dependency_overrides[get_current_user_id] = get_user_override
    yield client
    app.dependency_overrides.clear()


def test_chat_endpoint_requires_auth(client: TestClient):
    """Test chat endpoint requires authentication."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 403


@patch("app.agent.todo_agent.TodoAgent.process_message")
@pytest.mark.asyncio
async def test_chat_create_new_conversation(
    mock_process,
    auth_client: TestClient,
    test_user_id: str,
    mock_openai_response
):
    """Test chat creates new conversation when none provided."""
    mock_process.return_value = mock_openai_response

    response = auth_client.post(
        "/api/v1/chat",
        json={"message": "Add a task to buy groceries"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["conversation_id"] is not None
    assert "response" in data
    assert "tool_calls" in data


@patch("app.agent.todo_agent.TodoAgent.process_message")
@pytest.mark.asyncio
async def test_chat_continue_conversation(
    mock_process,
    auth_client: TestClient,
    test_user_id: str,
    mock_openai_response
):
    """Test chat continues existing conversation."""
    mock_process.return_value = mock_openai_response

    # First message - creates conversation
    response1 = auth_client.post(
        "/api/v1/chat",
        json={"message": "First message"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Second message - continues conversation
    response2 = auth_client.post(
        "/api/v1/chat",
        json={
            "message": "Second message",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 200
    data = response2.json()
    assert data["conversation_id"] == conversation_id


def test_chat_invalid_conversation_id(
    auth_client: TestClient,
    test_user_id: str
):
    """Test chat with non-existent conversation ID."""
    response = auth_client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "conversation_id": 99999
        }
    )

    assert response.status_code == 404


def test_chat_empty_message(
    auth_client: TestClient,
    test_user_id: str
):
    """Test chat with empty message."""
    response = auth_client.post(
        "/api/v1/chat",
        json={"message": ""}
    )

    assert response.status_code == 422  # Validation error


def test_chat_message_too_long(
    auth_client: TestClient,
    test_user_id: str
):
    """Test chat with message exceeding max length."""
    long_message = "A" * 2001  # Max is 2000

    response = auth_client.post(
        "/api/v1/chat",
        json={"message": long_message}
    )

    assert response.status_code == 422  # Validation error


@patch("app.agent.todo_agent.TodoAgent.process_message")
@pytest.mark.asyncio
async def test_chat_saves_messages(
    mock_process,
    auth_client: TestClient,
    test_user_id: str,
    test_db,
    mock_openai_response
):
    """Test chat saves user and assistant messages."""
    mock_process.return_value = mock_openai_response

    response = auth_client.post(
        "/api/v1/chat",
        json={"message": "Test message"}
    )

    assert response.status_code == 200

    # Verify messages were saved
    from app.models.message import Message
    from sqlmodel import select

    messages = test_db.exec(select(Message)).all()
    assert len(messages) == 2  # User message + assistant response

    user_msg = messages[0]
    assert user_msg.role.value == "user"
    assert user_msg.content == "Test message"

    assistant_msg = messages[1]
    assert assistant_msg.role.value == "assistant"
    assert assistant_msg.content == mock_openai_response["response"]


@patch("app.agent.todo_agent.TodoAgent.process_message")
@pytest.mark.asyncio
async def test_chat_loads_history(
    mock_process,
    auth_client: TestClient,
    test_user_id: str,
    mock_openai_response
):
    """Test chat loads conversation history for context."""
    mock_process.return_value = mock_openai_response

    # First message
    response1 = auth_client.post(
        "/api/v1/chat",
        json={"message": "First message"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Second message
    auth_client.post(
        "/api/v1/chat",
        json={
            "message": "Second message",
            "conversation_id": conversation_id
        }
    )

    # Verify process_message was called with history
    assert mock_process.call_count == 2
    second_call_args = mock_process.call_args_list[1]
    history = second_call_args[1]["conversation_history"]

    # History should contain first user message and assistant response
    assert len(history) >= 2


@patch("app.agent.todo_agent.TodoAgent.process_message")
@pytest.mark.asyncio
async def test_chat_user_isolation(
    mock_process,
    client: TestClient,
    test_db,
    mock_openai_response
):
    """Test users cannot access other users' conversations."""
    from app.api.deps import get_current_user_id
    from app.main import app

    mock_process.return_value = mock_openai_response

    # Create conversation for user 1
    def get_user1():
        return "user_1"

    app.dependency_overrides[get_current_user_id] = get_user1
    response1 = client.post(
        "/api/v1/chat",
        json={"message": "User 1 message"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Try to access with user 2
    def get_user2():
        return "user_2"

    app.dependency_overrides[get_current_user_id] = get_user2
    response2 = client.post(
        "/api/v1/chat",
        json={
            "message": "User 2 trying to access user 1 conversation",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 404

    app.dependency_overrides.clear()
