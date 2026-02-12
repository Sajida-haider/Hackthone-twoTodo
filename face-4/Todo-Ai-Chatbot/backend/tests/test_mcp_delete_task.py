"""Unit tests for MCP delete_task tool."""
import pytest
from unittest.mock import patch
from tests.conftest import create_test_task


@pytest.mark.asyncio
async def test_delete_task_success(test_db, test_user):
    """Test successfully deleting a task."""
    task = create_test_task(test_db, test_user["id"], "Task to delete")

    with patch('app.mcp.tools.delete_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.delete_task import delete_task

        result = await delete_task(
            user_id=test_user["id"],
            task_id=task.id
        )

        assert result["result"] == "success"
        assert result["task_id"] == task.id
        assert result["title"] == "Task to delete"
        assert result["error_message"] is None


@pytest.mark.asyncio
async def test_delete_task_not_found(test_db, test_user):
    """Test deleting non-existent task."""
    with patch('app.mcp.tools.delete_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.delete_task import delete_task

        result = await delete_task(
            user_id=test_user["id"],
            task_id=99999
        )

        assert result["result"] == "error"
        assert "not found" in result["error_message"].lower()


@pytest.mark.asyncio
async def test_delete_task_wrong_user(test_db, test_user):
    """Test user cannot delete another user's task."""
    other_user_id = "other_user_123"
    task = create_test_task(test_db, other_user_id, "Other user's task")

    with patch('app.mcp.tools.delete_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.delete_task import delete_task

        result = await delete_task(
            user_id=test_user["id"],
            task_id=task.id
        )

        assert result["result"] == "error"
        assert "not found" in result["error_message"].lower()


@pytest.mark.asyncio
async def test_delete_task_actually_removed(test_db, test_user):
    """Test that deleted task is actually removed from database."""
    from app.models.task import Task
    from sqlmodel import select

    task = create_test_task(test_db, test_user["id"], "Task to delete")
    task_id = task.id

    with patch('app.mcp.tools.delete_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.delete_task import delete_task

        # Delete the task
        result = await delete_task(
            user_id=test_user["id"],
            task_id=task_id
        )

        assert result["result"] == "success"

    # Verify it's gone from database
    deleted_task = test_db.exec(
        select(Task).where(Task.id == task_id)
    ).first()

    assert deleted_task is None
