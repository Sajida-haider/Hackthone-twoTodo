"""Unit tests for MCP complete_task tool."""
import pytest
from unittest.mock import patch
from tests.conftest import create_test_task


@pytest.mark.asyncio
async def test_complete_task_success(test_db, test_user):
    """Test successfully completing a task."""
    task = create_test_task(test_db, test_user["id"], "Task to complete")

    with patch('app.mcp.tools.complete_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.complete_task import complete_task

        result = await complete_task(
            user_id=test_user["id"],
            task_id=task.id
        )

        assert result["result"] == "success"
        assert result["task_id"] == task.id
        assert result["title"] == "Task to complete"
        assert result["error_message"] is None


@pytest.mark.asyncio
async def test_complete_task_not_found(test_db, test_user):
    """Test completing non-existent task."""
    with patch('app.mcp.tools.complete_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.complete_task import complete_task

        result = await complete_task(
            user_id=test_user["id"],
            task_id=99999
        )

        assert result["result"] == "error"
        assert "not found" in result["error_message"].lower()


@pytest.mark.asyncio
async def test_complete_task_wrong_user(test_db, test_user):
    """Test user cannot complete another user's task."""
    # Create task for different user
    other_user_id = "other_user_123"
    task = create_test_task(test_db, other_user_id, "Other user's task")

    with patch('app.mcp.tools.complete_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.complete_task import complete_task

        result = await complete_task(
            user_id=test_user["id"],
            task_id=task.id
        )

        assert result["result"] == "error"
        assert "not found" in result["error_message"].lower()


@pytest.mark.asyncio
async def test_complete_already_completed_task(test_db, test_user):
    """Test completing an already completed task."""
    task = create_test_task(test_db, test_user["id"], "Already done", completed=True)

    with patch('app.mcp.tools.complete_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.complete_task import complete_task

        result = await complete_task(
            user_id=test_user["id"],
            task_id=task.id
        )

        # Should still succeed (idempotent operation)
        assert result["result"] == "success"
