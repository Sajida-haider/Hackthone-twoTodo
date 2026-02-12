# Quickstart Guide: Memory-Based Console Todo App

## Prerequisites
- Python 3.13+ installed on your system
- Basic familiarity with command-line interfaces

## Setup
1. Clone or download the project repository
2. Navigate to the project directory
3. Ensure Python 3.13+ is available: `python --version`

## Running the Application
1. From the project root directory, run: `python main.py`
2. The application will start with a welcome message and main menu

## Basic Usage
Once the application starts, you'll see a menu with the following options:
- **Add Task**: Enter '1' or 'add' to create a new task
- **View Tasks**: Enter '2' or 'view' to see all tasks with their status
- **Update Task**: Enter '3' or 'update' to modify an existing task description
- **Delete Task**: Enter '4' or 'delete' to remove a task
- **Mark Complete**: Enter '5' or 'complete' to mark a task as done
- **Exit**: Enter '6' or 'exit' to quit the application

## Example Workflow
1. Select 'Add Task' and enter your task description
2. Use 'View Tasks' to see your task list
3. Use 'Mark Complete' to update task status
4. Continue managing your tasks as needed
5. Exit when finished (note: tasks will be lost upon exit)

## Error Handling
- Invalid inputs will result in helpful error messages
- Attempting operations on non-existent tasks will display appropriate warnings
- Empty input for task descriptions will be rejected

## Important Notes
- All data is stored in memory only - tasks are lost when the program exits
- Maximum 100 tasks can be managed simultaneously
- The application follows a simple menu-driven interface for ease of use