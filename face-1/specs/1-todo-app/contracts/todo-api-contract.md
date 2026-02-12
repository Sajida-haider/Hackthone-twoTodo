# Todo App API Contract

## Overview
This contract defines the interface for the Memory-Based Console Todo App. The application provides a command-line interface for managing tasks in memory.

## Core Operations

### Add Task
- **Command**: `add` or `1`
- **Input**: Task description (string)
- **Output**: Confirmation message with task ID
- **Success Response**: "Task added successfully with ID: {id}"
- **Error Responses**:
  - "Error: Task description cannot be empty"
  - "Error: Maximum task limit reached (100 tasks)"

### View Tasks
- **Command**: `view` or `2`
- **Input**: None
- **Output**: List of all tasks with ID, description, and completion status
- **Success Response**: Formatted list of tasks or "No tasks found"
- **Error Responses**: None

### Update Task
- **Command**: `update` or `3`
- **Input**: Task ID (int) and new description (string)
- **Output**: Confirmation message
- **Success Response**: "Task {id} updated successfully"
- **Error Responses**:
  - "Error: Task with ID {id} not found"
  - "Error: Task description cannot be empty"

### Delete Task
- **Command**: `delete` or `4`
- **Input**: Task ID (int)
- **Output**: Confirmation message
- **Success Response**: "Task {id} deleted successfully"
- **Error Responses**:
  - "Error: Task with ID {id} not found"

### Mark Task Complete
- **Command**: `complete` or `5`
- **Input**: Task ID (int)
- **Output**: Confirmation message
- **Success Response**: "Task {id} marked as complete"
- **Error Responses**:
  - "Error: Task with ID {id} not found"

### Exit Application
- **Command**: `exit` or `6`
- **Input**: None
- **Output**: Goodbye message
- **Success Response**: "Goodbye! Your tasks have been cleared."
- **Error Responses**: None