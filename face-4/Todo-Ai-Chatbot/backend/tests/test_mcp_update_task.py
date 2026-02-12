"""Unit tests for MCP update_task tool."""
import pytest
from unittest.mock import patch
from tests.conftest import create_test_task


@pytest.mark.asyncio
async def test_update_task_title(test_db, test_user):
    """Test updating task title."""
    task = create_test_task(test_db, test_user["id"], "Old Title")

    with patch('app.mcp.tools.update_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.update_task import update_task

        result = await update_task(
            user_id=test_user["id"],
            task_id=task.id,
            title="New Title"
        )

        assert result["result"] == "success"
        assert result["task_id"] == task.id
        assert result["title"] == "New Title"
        assert result["error_message"] is None


@pytest.mark.asyncio
async def test_update_task_description(test_db, test_user):
    """Test updating task description."""
    from app.models.task import Task
    from sqlmodel import select

    task = create_test_task(test_db, test_user["id"], "Task", "Old description")

    with patch('app.mcp.tools.update_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.update_task import update_task

        result = await update_task(
            user_id=test_user["id"],
            task_id=task.id,
            description="New description"
        )

        assert result["result"] == "success"

        # Verify description was updated in database
        updated_task = test_db.exec(select(Task).where(Task.id == task.id)).first()
        assert updated_task.description == "New description"


@pytest.mark.asyncio
async def test_update_task_both_fields(test_db, test_user):
    """Test updating both title and description."""
    from app.models.task import Task
    from sqlmodel import select

    task = create_test_task(test_db, test_user["id"], "Old Title", "Old description")

    with patch('app.mcp.tools.update_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.update_task import update_task

        result = await update_task(
            user_id=test_user["id"],
            task_id=task.id,
            title="New Title",
            description="New description"
        )

        assert result["result"] == "success"
        assert result["title"] == "New Title"

        # Verify description was updated in database
        updated_task = test_db.exec(select(Task).where(Task.id == task.id)).first()
        assert updated_task.description == "New description"


@pytest.mark.asyncio
async def test_update_task_not_found(test_db, test_user):
    """Test updating non-existent task."""
    with patch('app.mcp.tools.update_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.update_task import update_task

        result = await update_task(
            user_id=test_user["id"],
            task_id=99999,
            title="New Title"
        )

        assert result["result"] == "error"
        assert "not found" in result["error_message"].lower()


@pytest.mark.asyncio
async def test_update_task_wrong_user(test_db, test_user):
    """Test user cannot update another user's task."""
    other_user_id = "other_user_123"
    task = create_test_task(test_db, other_user_id, "Other user's task")

    with patch('app.mcp.tools.update_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.update_task import update_task

        result = await update_task(
            user_id=test_user["id"],
            task_id=task.id,
            title="Trying to update"
        )

        assert result["result"] == "error"
        assert "not found" in result["error_message"].lower()


@pytest.mark.asyncio
async def test_update_task_no_changes(test_db, test_user):
    """Test updating task with no actual changes."""
    task = create_test_task(test_db, test_user["id"], "Task Title")

    with patch('app.mcp.tools.update_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.update_task import update_task

        result = await update_task(
            user_id=test_user["id"],
            task_id=task.id
        )

        # Should succeed even with no changes
        assert result["result"] == "success"
