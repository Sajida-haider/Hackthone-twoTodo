"""
Tests for Todo App Services
Tests for TodoService functionality
"""
import unittest
from src.todo_app.services.todo_service import TodoService


class TestTodoService(unittest.TestCase):
    """
    Test cases for the TodoService class
    """

    def setUp(self):
        """
        Set up a TodoService instance for testing
        """
        self.service = TodoService(max_tasks=10)

    def test_add_task_success(self):
        """
        Test adding a task successfully
        """
        task_id = self.service.add_task("Test task")
        self.assertEqual(task_id, 1)
        self.assertEqual(self.service.count, 1)

    def test_add_task_empty_description(self):
        """
        Test adding a task with empty description
        """
        with self.assertRaises(ValueError):
            self.service.add_task("")

    def test_add_task_too_long_description(self):
        """
        Test adding a task with too long description
        """
        with self.assertRaises(ValueError):
            self.service.add_task("x" * 501)

    def test_get_task_by_id(self):
        """
        Test getting a task by ID
        """
        task_id = self.service.add_task("Test task")
        task = self.service.get_task_by_id(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.id, task_id)
        self.assertEqual(task.description, "Test task")

    def test_get_task_by_nonexistent_id(self):
        """
        Test getting a task by nonexistent ID
        """
        task = self.service.get_task_by_id(999)
        self.assertIsNone(task)

    def test_get_all_tasks(self):
        """
        Test getting all tasks
        """
        self.service.add_task("Task 1")
        self.service.add_task("Task 2")

        tasks = self.service.get_all_tasks()
        self.assertEqual(len(tasks), 2)

    def test_update_task_success(self):
        """
        Test updating a task successfully
        """
        task_id = self.service.add_task("Old description")
        result = self.service.update_task(task_id, "New description")

        self.assertTrue(result)
        task = self.service.get_task_by_id(task_id)
        self.assertEqual(task.description, "New description")

    def test_update_task_nonexistent(self):
        """
        Test updating a nonexistent task
        """
        with self.assertRaises(ValueError):
            self.service.update_task(999, "New description")

    def test_update_task_empty_description(self):
        """
        Test updating a task with empty description
        """
        task_id = self.service.add_task("Test task")

        with self.assertRaises(ValueError):
            self.service.update_task(task_id, "")

    def test_update_task_too_long_description(self):
        """
        Test updating a task with too long description
        """
        task_id = self.service.add_task("Test task")

        with self.assertRaises(ValueError):
            self.service.update_task(task_id, "x" * 501)

    def test_mark_task_complete(self):
        """
        Test marking a task as complete
        """
        task_id = self.service.add_task("Test task")
        result = self.service.mark_task_complete(task_id)

        self.assertTrue(result)
        task = self.service.get_task_by_id(task_id)
        self.assertTrue(task.completed)

    def test_mark_task_complete_nonexistent(self):
        """
        Test marking a nonexistent task as complete
        """
        from src.todo_app.models.task import TaskNotFoundException
        with self.assertRaises(TaskNotFoundException):
            self.service.mark_task_complete(999)

    def test_mark_task_incomplete(self):
        """
        Test marking a task as incomplete
        """
        task_id = self.service.add_task("Test task")
        self.service.mark_task_complete(task_id)

        result = self.service.mark_task_incomplete(task_id)
        self.assertTrue(result)

        task = self.service.get_task_by_id(task_id)
        self.assertFalse(task.completed)

    def test_mark_task_incomplete_nonexistent(self):
        """
        Test marking a nonexistent task as incomplete
        """
        from src.todo_app.models.task import TaskNotFoundException
        with self.assertRaises(TaskNotFoundException):
            self.service.mark_task_incomplete(999)

    def test_delete_task(self):
        """
        Test deleting a task
        """
        task_id = self.service.add_task("Test task")
        result = self.service.delete_task(task_id)

        self.assertTrue(result)
        self.assertIsNone(self.service.get_task_by_id(task_id))
        self.assertEqual(self.service.count, 0)

    def test_delete_nonexistent_task(self):
        """
        Test deleting a nonexistent task
        """
        from src.todo_app.models.task import TaskNotFoundException
        with self.assertRaises(TaskNotFoundException):
            self.service.delete_task(999)

    def test_task_exists(self):
        """
        Test checking if a task exists
        """
        task_id = self.service.add_task("Test task")

        self.assertTrue(self.service.task_exists(task_id))
        self.assertFalse(self.service.task_exists(999))

    def test_max_tasks_limit(self):
        """
        Test reaching the maximum tasks limit
        """
        limited_service = TodoService(max_tasks=2)

        limited_service.add_task("Task 1")
        limited_service.add_task("Task 2")

        with self.assertRaises(ValueError):
            limited_service.add_task("Task 3")


if __name__ == '__main__':
    unittest.main()