"""
Tests for Todo App CLI
Tests for console interface functionality
"""
import unittest
import io
import sys
from unittest.mock import patch, MagicMock
from src.todo_app.cli.interface import TodoAppCLI


class TestTodoAppCLI(unittest.TestCase):
    """
    Test cases for the TodoAppCLI class
    """

    def setUp(self):
        """
        Set up a TodoAppCLI instance for testing
        """
        self.cli = TodoAppCLI()

    @patch('builtins.input', side_effect=['exit'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_run_exit_command(self, mock_stdout, mock_input):
        """
        Test running the CLI and exiting
        """
        # We'll just test that no exception is raised when running with exit command
        self.cli.running = True
        self.cli.handle_exit()

        self.assertFalse(self.cli.running)

    @patch('builtins.input', side_effect=['add', 'Test task', 'exit'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_handle_add_task_success(self, mock_stdout, mock_input):
        """
        Test adding a task through CLI
        """
        # Mock the input to simulate user interaction
        with patch.object(self.cli, 'service') as mock_service:
            mock_service.add_task.return_value = 1

            self.cli.handle_add_task()

            # Verify the service method was called
            mock_service.add_task.assert_called_once_with('Test task')

    @patch('builtins.input', side_effect=['view', 'exit'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_handle_view_tasks(self, mock_stdout, mock_input):
        """
        Test viewing tasks through CLI
        """
        # Mock the service to return some tasks
        with patch.object(self.cli, 'service') as mock_service:
            mock_service.get_all_tasks.return_value = []

            self.cli.handle_view_tasks()

            # Verify the service method was called
            mock_service.get_all_tasks.assert_called_once()

    @patch('builtins.input', side_effect=['update', '1', 'Updated task', 'exit'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_handle_update_task(self, mock_stdout, mock_input):
        """
        Test updating a task through CLI
        """
        with patch.object(self.cli, 'service') as mock_service:
            mock_service.task_exists.return_value = True

            self.cli.handle_update_task()

            # Verify the service method was called
            mock_service.update_task.assert_called_once()

    @patch('builtins.input', side_effect=['delete', '1', 'exit'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_handle_delete_task(self, mock_stdout, mock_input):
        """
        Test deleting a task through CLI
        """
        with patch.object(self.cli, 'service') as mock_service:
            mock_service.task_exists.return_value = True

            self.cli.handle_delete_task()

            # Verify the service method was called
            mock_service.delete_task.assert_called_once()

    @patch('builtins.input', side_effect=['complete', '1', 'exit'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_handle_mark_complete(self, mock_stdout, mock_input):
        """
        Test marking a task as complete through CLI
        """
        with patch.object(self.cli, 'service') as mock_service:
            mock_service.task_exists.return_value = True

            self.cli.handle_mark_complete()

            # Verify the service method was called
            mock_service.mark_task_complete.assert_called_once()


if __name__ == '__main__':
    unittest.main()