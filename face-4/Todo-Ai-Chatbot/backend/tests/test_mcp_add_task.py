"""Unit tests for MCP add_task tool."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch


@pytest.mark.asyncio
async def test_add_task_success(test_db, test_user):
    """Test successful task creation."""
    with patch('app.mcp.tools.add_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.add_task import add_task

        result = await add_task(
            user_id=test_user["id"],
            title="Buy groceries",
            description="Get milk and eggs"
        )

        assert result["result"] == "success"
        assert result["task_id"] is not None
        assert result["title"] == "Buy groceries"
        assert result["error_message"] is None


@pytest.mark.asyncio
async def test_add_task_with_description(test_db, test_user):
    """Test task creation with description."""
    with patch('app.mcp.tools.add_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.add_task import add_task

        result = await add_task(
            user_id=test_user["id"],
            title="Submit report",
            description="Quarterly report"
        )

        assert result["result"] == "success"
        assert result["task_id"] is not None
        assert result["title"] == "Submit report"


@pytest.mark.asyncio
async def test_add_task_minimal(test_db, test_user):
    """Test task creation with only required fields."""
    with patch('app.mcp.tools.add_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.add_task import add_task

        result = await add_task(
            user_id=test_user["id"],
            title="Quick task"
        )

        assert result["result"] == "success"
        assert result["task_id"] is not None
        assert result["title"] == "Quick task"


@pytest.mark.asyncio
async def test_add_task_empty_title(test_db, test_user):
    """Test task creation with empty title (currently allowed)."""
    with patch('app.mcp.tools.add_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.add_task import add_task

        result = await add_task(
            user_id=test_user["id"],
            title=""
        )

        # Currently no validation, so empty title is allowed
        assert result["result"] == "success"


@pytest.mark.asyncio
async def test_add_task_long_title(test_db, test_user):
    """Test task creation with very long title."""
    with patch('app.mcp.tools.add_task.get_session', return_value=iter([test_db])):
        from app.mcp.tools.add_task import add_task

        long_title = "A" * 500

        result = await add_task(
            user_id=test_user["id"],
            title=long_title
        )

        # Should either succeed or fail gracefully
        assert result["result"] in ["success", "error"]
