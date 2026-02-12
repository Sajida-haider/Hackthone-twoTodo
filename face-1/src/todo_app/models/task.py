"""
Task Model Module
Contains Task entity and TodoList collection for in-memory storage
"""
from typing import List, Optional, Dict


class TodoException(Exception):
    """Base exception class for Todo App"""
    pass


class TaskNotFoundException(TodoException):
    """Raised when a requested task is not found"""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class TaskLimitReachedException(TodoException):
    """Raised when the maximum number of tasks is reached"""
    def __init__(self, max_tasks: int):
        self.max_tasks = max_tasks
        super().__init__(f"Maximum task limit reached ({max_tasks})")


class InvalidTaskDescriptionException(TodoException):
    """Raised when a task description is invalid (empty or whitespace only)"""
    def __init__(self):
        super().__init__("Task description cannot be empty")


class Task:
    """Represents a single todo item in the application"""

    def __init__(self, task_id: int, description: str, completed: bool = False):
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("Task ID must be a positive integer")

        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")

        # Check for very long descriptions (limit to 500 characters)
        if len(description) > 500:
            raise ValueError("Task description is too long (maximum 500 characters)")

        if not isinstance(completed, bool):
            raise ValueError("Completed status must be a boolean")

        self.id = task_id
        self.description = description.strip()
        self.completed = completed

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.id}: {self.description}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed
        }


class TodoList:
    """Container for managing multiple Task entities"""

    def __init__(self, max_tasks: int = 100):
        self._tasks: List[Task] = []
        self._task_ids: Dict[int, Task] = {}
        self._max_tasks = max_tasks
        self._next_id = 1

    def add_task(self, description: str) -> int:
        if len(self._tasks) >= self._max_tasks:
            raise ValueError(f"Maximum task limit reached ({self._max_tasks})")

        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")

        task_id = self._generate_next_id()
        task = Task(task_id, description)

        self._tasks.append(task)
        self._task_ids[task_id] = task

        return task_id

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        return self._task_ids.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        return self._tasks.copy()  # Return a copy to prevent external modification

    def update_task(self, task_id: int, new_description: str) -> bool:
        if not new_description or not new_description.strip():
            raise ValueError("Task description cannot be empty")

        # Check for very long descriptions (limit to 500 characters)
        if len(new_description) > 500:
            raise ValueError("Task description is too long (maximum 500 characters)")

        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task.description = new_description.strip()
        return True

    def mark_task_complete(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task.completed = True
        return True

    def mark_task_incomplete(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task.completed = False
        return True

    def delete_task(self, task_id: int) -> bool:
        if task_id not in self._task_ids:
            return False

        task = self._task_ids[task_id]
        self._tasks.remove(task)
        del self._task_ids[task_id]

        return True

    def task_exists(self, task_id: int) -> bool:
        return task_id in self._task_ids

    def _generate_next_id(self) -> int:
        while self._next_id in self._task_ids:
            self._next_id += 1

        next_id = self._next_id
        self._next_id += 1
        return next_id

    @property
    def count(self) -> int:
        return len(self._tasks)

    @property
    def max_capacity(self) -> int:
        return self._max_tasks