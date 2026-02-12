"""
Tests for Todo App Models
Tests for Task model and TodoList collection
"""
import unittest
from src.todo_app.models.task import Task, TodoList


class TestTask(unittest.TestCase):
    """
    Test cases for the Task class
    """

    def test_task_creation_valid(self):
        """
        Test creating a valid task
        """
        task = Task(1, "Test task")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.description, "Test task")
        self.assertFalse(task.completed)

    def test_task_creation_with_completion_status(self):
        """
        Test creating a task with completion status
        """
        task = Task(1, "Test task", True)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.description, "Test task")
        self.assertTrue(task.completed)

    def test_task_creation_invalid_id(self):
        """
        Test creating a task with invalid ID
        """
        with self.assertRaises(ValueError):
            Task(0, "Test task")

        with self.assertRaises(ValueError):
            Task(-1, "Test task")

    def test_task_creation_invalid_description(self):
        """
        Test creating a task with invalid description
        """
        with self.assertRaises(ValueError):
            Task(1, "")

        with self.assertRaises(ValueError):
            Task(1, "   ")

        with self.assertRaises(ValueError):
            Task(1, "x" * 501)  # Too long description

    def test_task_creation_invalid_completed(self):
        """
        Test creating a task with invalid completed status
        """
        with self.assertRaises(ValueError):
            Task(1, "Test task", "invalid")

    def test_task_repr(self):
        """
        Test string representation of a task
        """
        task = Task(1, "Test task", False)
        repr_str = repr(task)
        self.assertIn("○", repr_str)  # Pending status

        task.completed = True
        repr_str = repr(task)
        self.assertIn("✓", repr_str)  # Completed status


class TestTodoList(unittest.TestCase):
    """
    Test cases for the TodoList class
    """

    def setUp(self):
        """
        Set up a TodoList instance for testing
        """
        self.todo_list = TodoList(max_tasks=10)

    def test_add_task_success(self):
        """
        Test adding a task successfully
        """
        task_id = self.todo_list.add_task("Test task")
        self.assertEqual(task_id, 1)
        self.assertEqual(len(self.todo_list.get_all_tasks()), 1)

    def test_add_task_empty_description(self):
        """
        Test adding a task with empty description
        """
        with self.assertRaises(ValueError):
            self.todo_list.add_task("")

    def test_add_task_whitespace_description(self):
        """
        Test adding a task with whitespace-only description
        """
        with self.assertRaises(ValueError):
            self.todo_list.add_task("   ")

    def test_add_task_too_long_description(self):
        """
        Test adding a task with too long description
        """
        with self.assertRaises(ValueError):
            self.todo_list.add_task("x" * 501)

    def test_get_task_by_id(self):
        """
        Test getting a task by ID
        """
        task_id = self.todo_list.add_task("Test task")
        task = self.todo_list.get_task_by_id(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.id, task_id)
        self.assertEqual(task.description, "Test task")

    def test_get_task_by_nonexistent_id(self):
        """
        Test getting a task by nonexistent ID
        """
        task = self.todo_list.get_task_by_id(999)
        self.assertIsNone(task)

    def test_get_all_tasks(self):
        """
        Test getting all tasks
        """
        self.todo_list.add_task("Task 1")
        self.todo_list.add_task("Task 2")

        tasks = self.todo_list.get_all_tasks()
        self.assertEqual(len(tasks), 2)

    def test_update_task_success(self):
        """
        Test updating a task successfully
        """
        task_id = self.todo_list.add_task("Old description")
        result = self.todo_list.update_task(task_id, "New description")

        self.assertTrue(result)
        task = self.todo_list.get_task_by_id(task_id)
        self.assertEqual(task.description, "New description")

    def test_update_task_nonexistent(self):
        """
        Test updating a nonexistent task
        """
        result = self.todo_list.update_task(999, "New description")
        self.assertFalse(result)

    def test_update_task_empty_description(self):
        """
        Test updating a task with empty description
        """
        task_id = self.todo_list.add_task("Test task")

        with self.assertRaises(ValueError):
            self.todo_list.update_task(task_id, "")

    def test_update_task_too_long_description(self):
        """
        Test updating a task with too long description
        """
        task_id = self.todo_list.add_task("Test task")

        with self.assertRaises(ValueError):
            self.todo_list.update_task(task_id, "x" * 501)

    def test_mark_task_complete(self):
        """
        Test marking a task as complete
        """
        task_id = self.todo_list.add_task("Test task")
        result = self.todo_list.mark_task_complete(task_id)

        self.assertTrue(result)
        task = self.todo_list.get_task_by_id(task_id)
        self.assertTrue(task.completed)

    def test_mark_task_incomplete(self):
        """
        Test marking a task as incomplete
        """
        task_id = self.todo_list.add_task("Test task")
        self.todo_list.mark_task_complete(task_id)

        result = self.todo_list.mark_task_incomplete(task_id)
        self.assertTrue(result)

        task = self.todo_list.get_task_by_id(task_id)
        self.assertFalse(task.completed)

    def test_delete_task(self):
        """
        Test deleting a task
        """
        task_id = self.todo_list.add_task("Test task")
        result = self.todo_list.delete_task(task_id)

        self.assertTrue(result)
        self.assertIsNone(self.todo_list.get_task_by_id(task_id))
        self.assertEqual(len(self.todo_list.get_all_tasks()), 0)

    def test_delete_nonexistent_task(self):
        """
        Test deleting a nonexistent task
        """
        result = self.todo_list.delete_task(999)
        self.assertFalse(result)

    def test_task_exists(self):
        """
        Test checking if a task exists
        """
        task_id = self.todo_list.add_task("Test task")

        self.assertTrue(self.todo_list.task_exists(task_id))
        self.assertFalse(self.todo_list.task_exists(999))

    def test_max_tasks_limit(self):
        """
        Test reaching the maximum tasks limit
        """
        limited_list = TodoList(max_tasks=2)

        limited_list.add_task("Task 1")
        limited_list.add_task("Task 2")

        with self.assertRaises(ValueError):
            limited_list.add_task("Task 3")


if __name__ == '__main__':
    unittest.main()