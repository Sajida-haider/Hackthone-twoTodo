# Data Model: Memory-Based Console Todo App

## Task Entity

**Definition**: Represents a single todo item in the application

**Attributes**:
- `id` (int): Unique identifier for the task (auto-generated)
- `description` (str): Text description of the task
- `completed` (bool): Status indicator (True = completed, False = pending)

**Validation Rules**:
- `id` must be a positive integer
- `description` must be non-empty (after stripping whitespace)
- `completed` must be a boolean value

**State Transitions**:
- `pending` (completed=False) → `completed` (completed=True) via mark_complete operation
- `completed` (completed=True) → `pending` (completed=False) via mark_incomplete operation

## Todo List Collection

**Definition**: Container for managing multiple Task entities

**Structure**:
- Primary storage: List of Task objects
- Secondary access: Dictionary mapping id → Task object for efficient lookup

**Operations Supported**:
- Add new task to collection
- Retrieve all tasks
- Retrieve specific task by ID
- Update task description by ID
- Mark task as complete/incomplete by ID
- Delete task by ID
- Validate task existence by ID

**Constraints**:
- Maximum 100 tasks supported in memory (per success criteria SC-005)
- All operations must maintain data integrity
- IDs must remain unique within the collection

## Relationships

**Within Collection**: Tasks exist independently within the Todo List collection. Each task has a unique ID that allows for individual operations without affecting other tasks.

**State Consistency**: The completed status of each task is independent of other tasks in the collection.