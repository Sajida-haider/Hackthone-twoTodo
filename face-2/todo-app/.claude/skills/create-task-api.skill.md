# Create Task API

## Purpose
Create a new todo task for the authenticated user.

## Steps
1. Authenticate user using JWT
2. Validate request body
3. Associate task with user_id
4. Save task in database

## Output
POST /api/{user_id}/tasks endpoint

## Implementation Details

### Authentication
- Verify JWT token from Authorization header
- Extract user identity from token payload
- Ensure user exists and is active

### Request Validation
- Validate required fields (title, description)
- Check field length limits
- Validate data types
- Ensure proper format for dates if applicable

### Task Association
- Link task to authenticated user via user_id
- Ensure user can only create tasks for themselves
- Verify user permissions

### Database Operations
- Create new task record with user association
- Set appropriate timestamps (created_at, updated_at)
- Handle database errors gracefully
- Return created task with unique identifier

## Expected Request Format
```json
{
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "due_date": "2023-12-31"
}
```

## Expected Response Format
```json
{
  "id": "generated_task_id",
  "user_id": "authenticated_user_id",
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## Error Handling
- 401 Unauthorized: Invalid or missing JWT
- 400 Bad Request: Invalid request body
- 500 Internal Server Error: Database errors