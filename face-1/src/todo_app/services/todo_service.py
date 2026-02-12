from typing import List, Optional
from src.todo_app.models.task import TodoList, Task, TaskNotFoundException


class TodoService:
    def __init__(self, max_tasks: int = 100):
        self.todo_list = TodoList(max_tasks=max_tasks)

    def add_task(self, description: str) -> int:
        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")

        # Check for very long descriptions (limit to 500 characters)
        if len(description) > 500:
            raise ValueError("Task description is too long (maximum 500 characters)")

        return self.todo_list.add_task(description)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        return self.todo_list.get_task_by_id(task_id)

    def get_all_tasks(self) -> List[Task]:
        return self.todo_list.get_all_tasks()

    def update_task(self, task_id: int, new_description: str) -> bool:
        if not new_description or not new_description.strip():
            raise ValueError("Task description cannot be empty")

        # Check for very long descriptions (limit to 500 characters)
        if len(new_description) > 500:
            raise ValueError("Task description is too long (maximum 500 characters)")

        if not self.todo_list.task_exists(task_id):
            raise TaskNotFoundException(task_id)

        return self.todo_list.update_task(task_id, new_description)

    def mark_task_complete(self, task_id: int) -> bool:
        if not self.todo_list.task_exists(task_id):
            raise TaskNotFoundException(task_id)

        return self.todo_list.mark_task_complete(task_id)

    def mark_task_incomplete(self, task_id: int) -> bool:
        if not self.todo_list.task_exists(task_id):
            raise TaskNotFoundException(task_id)

        return self.todo_list.mark_task_incomplete(task_id)

    def delete_task(self, task_id: int) -> bool:
        if not self.todo_list.task_exists(task_id):
            raise TaskNotFoundException(task_id)

        return self.todo_list.delete_task(task_id)

    def task_exists(self, task_id: int) -> bool:
        return self.todo_list.task_exists(task_id)

    @property
    def count(self) -> int:
        return self.todo_list.count

    @property
    def max_capacity(self) -> int:
        return self.todo_list.max_capacity