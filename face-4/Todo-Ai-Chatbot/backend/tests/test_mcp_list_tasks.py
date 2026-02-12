"""Unit tests for MCP list_tasks tool."""
import pytest
from unittest.mock import patch
from tests.conftest import create_test_task


@pytest.mark.asyncio
async def test_list_tasks_empty(test_db, test_user):
    """Test listing tasks when user has no tasks."""
    with patch('app.mcp.tools.list_tasks.get_session', return_value=iter([test_db])):
        from app.mcp.tools.list_tasks import list_tasks

        result = await list_tasks(user_id=test_user["id"])

        assert result["result"] == "success"
        assert result["tasks"] == []
        assert result["count"] == 0


@pytest.mark.asyncio
async def test_list_tasks_multiple(test_db, test_user):
    """Test listing multiple tasks."""
    # Create test tasks
    create_test_task(test_db, test_user["id"], "Task 1")
    create_test_task(test_db, test_user["id"], "Task 2")
    create_test_task(test_db, test_user["id"], "Task 3")

    with patch('app.mcp.tools.list_tasks.get_session', return_value=iter([test_db])):
        from app.mcp.tools.list_tasks import list_tasks

        result = await list_tasks(user_id=test_user["id"])

        assert result["result"] == "success"
        assert result["count"] == 3
        assert len(result["tasks"]) == 3


@pytest.mark.asyncio
async def test_list_tasks_filter_pending(test_db, test_user):
    """Test listing only pending tasks."""
    create_test_task(test_db, test_user["id"], "Pending Task", completed=False)
    create_test_task(test_db, test_user["id"], "Completed Task", completed=True)

    with patch('app.mcp.tools.list_tasks.get_session', return_value=iter([test_db])):
        from app.mcp.tools.list_tasks import list_tasks

        result = await list_tasks(user_id=test_user["id"], status="pending")

        assert result["result"] == "success"
        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "Pending Task"


@pytest.mark.asyncio
async def test_list_tasks_filter_completed(test_db, test_user):
    """Test listing only completed tasks."""
    create_test_task(test_db, test_user["id"], "Pending Task", completed=False)
    create_test_task(test_db, test_user["id"], "Completed Task", completed=True)

    with patch('app.mcp.tools.list_tasks.get_session', return_value=iter([test_db])):
        from app.mcp.tools.list_tasks import list_tasks

        result = await list_tasks(user_id=test_user["id"], status="completed")

        assert result["result"] == "success"
        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "Completed Task"


@pytest.mark.asyncio
async def test_list_tasks_user_isolation(test_db, test_user):
    """Test that users only see their own tasks."""
    # Create tasks for test user
    create_test_task(test_db, test_user["id"], "My Task")

    # Create task for different user
    other_user_id = "other_user_123"
    create_test_task(test_db, other_user_id, "Other User Task")

    with patch('app.mcp.tools.list_tasks.get_session', return_value=iter([test_db])):
        from app.mcp.tools.list_tasks import list_tasks

        result = await list_tasks(user_id=test_user["id"])

        assert result["result"] == "success"
        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "My Task"
