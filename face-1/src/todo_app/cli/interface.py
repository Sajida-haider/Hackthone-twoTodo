"""
Console Interface Module
Contains functions for console-based user interaction
"""
from typing import Optional
from src.todo_app.services.todo_service import TodoService
from src.todo_app.models.task import TaskNotFoundException, TaskLimitReachedException, InvalidTaskDescriptionException


class TodoAppCLI:
    """
    Console interface for the Todo application
    """

    def __init__(self):
        """
        Initialize the CLI interface
        """
        self.service = TodoService()
        self.running = True

    def run(self):
        """
        Run the main application loop
        """
        print("Welcome to the Todo App!")
        print("Manage your tasks in memory. All data will be lost when you exit.")

        while self.running:
            self.display_menu()
            command = input("\nEnter your choice: ").strip().lower()

            if command in ['exit', 'quit', '6']:
                self.handle_exit()
            elif command in ['add', '1']:
                self.handle_add_task()
            elif command in ['view', '2']:
                self.handle_view_tasks()
            elif command in ['update', '3']:
                self.handle_update_task()
            elif command in ['delete', '4']:
                self.handle_delete_task()
            elif command in ['complete', '5']:
                self.handle_mark_complete()
            else:
                print("Invalid command. Please try again.")

    def display_menu(self):
        """
        Display the main menu options
        """
        print("\n" + "="*40)
        print("TODO APP MENU")
        print("="*40)
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Task Complete")
        print("6. Exit")
        print("="*40)

    def handle_add_task(self):
        """
        Handle adding a new task
        """
        try:
            description = input("Enter task description: ").strip()
            if not description:
                print("Error: Task description cannot be empty")
                return

            task_id = self.service.add_task(description)
            print(f"Task added successfully with ID: {task_id}")
        except (ValueError, TaskLimitReachedException, InvalidTaskDescriptionException) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def handle_view_tasks(self):
        """
        Handle viewing all tasks
        """
        try:
            tasks = self.service.get_all_tasks()

            if not tasks:
                print("No tasks found.")
                return

            print(f"\nYou have {len(tasks)} task(s):")
            print("-" * 50)
            for task in tasks:
                status = "✓ Completed" if task.completed else "○ Pending"
                print(f"{task.id}. [{status}] {task.description}")
            print("-" * 50)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def handle_update_task(self):
        """
        Handle updating a task
        """
        try:
            task_id_str = input("Enter task ID to update: ").strip()
            if not task_id_str.isdigit():
                print("Error: Task ID must be a number")
                return

            task_id = int(task_id_str)

            # Check if task exists before prompting for new description
            if not self.service.task_exists(task_id):
                print(f"Error: Task with ID {task_id} not found")
                return

            new_description = input("Enter new description: ").strip()
            if not new_description:
                print("Error: Task description cannot be empty")
                return

            success = self.service.update_task(task_id, new_description)
            if success:
                print(f"Task {task_id} updated successfully")
            else:
                print(f"Error: Failed to update task {task_id}")
        except (ValueError, TaskLimitReachedException, InvalidTaskDescriptionException) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def handle_delete_task(self):
        """
        Handle deleting a task
        """
        try:
            task_id_str = input("Enter task ID to delete: ").strip()
            if not task_id_str.isdigit():
                print("Error: Task ID must be a number")
                return

            task_id = int(task_id_str)

            # Check if task exists before deletion
            if not self.service.task_exists(task_id):
                print(f"Error: Task with ID {task_id} not found")
                return

            success = self.service.delete_task(task_id)
            if success:
                print(f"Task {task_id} deleted successfully")
            else:
                print(f"Error: Failed to delete task {task_id}")
        except (ValueError, TaskLimitReachedException, InvalidTaskDescriptionException) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def handle_mark_complete(self):
        """
        Handle marking a task as complete
        """
        try:
            task_id_str = input("Enter task ID to mark complete: ").strip()
            if not task_id_str.isdigit():
                print("Error: Task ID must be a number")
                return

            task_id = int(task_id_str)

            # Check if task exists before marking complete
            if not self.service.task_exists(task_id):
                print(f"Error: Task with ID {task_id} not found")
                return

            success = self.service.mark_task_complete(task_id)
            if success:
                print(f"Task {task_id} marked as complete")
            else:
                print(f"Error: Failed to mark task {task_id} as complete")
        except (ValueError, TaskLimitReachedException, InvalidTaskDescriptionException) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def handle_exit(self):
        """
        Handle exiting the application
        """
        print("Goodbye! Your tasks have been cleared.")
        self.running = False