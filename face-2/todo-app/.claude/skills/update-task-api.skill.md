# Update Task API

## Purpose
Update an existing task.

## Steps
1. Verify JWT token
2. Check task ownership
3. Update allowed fields
4. Save changes

## Output
PUT /api/{user_id}/tasks/{id} endpoint

## Implementation Details

### Authentication
- Verify JWT token from Authorization header
- Extract user identity from token payload
- Ensure user exists and is active

### Task Ownership Verification
- Verify that the authenticated user owns the task
- Compare user_id in JWT with user_id in task record
- Return 403 Forbidden if user doesn't own the task

### Allowed Update Fields
- Title: Update task title
- Description: Update task description
- Completed: Toggle completion status
- Due date: Update task deadline
- Prevent updating user_id to maintain ownership integrity

### Validation
- Validate updated field values
- Check field length limits
- Validate data types
- Ensure proper format for dates if applicable

### Database Operations
- Update specified fields in the task record
- Update the updated_at timestamp
- Handle database errors gracefully
- Return updated task with latest values

## Expected Request Format
```json
{
  "title": "Updated task title",
  "description": "Updated task description",
  "completed": true,
  "due_date": "2023-12-31"
}
```

## Expected Response Format
```json
{
  "id": "task_id",
  "user_id": "authenticated_user_id",
  "title": "Updated task title",
  "description": "Updated task description",
  "completed": true,
  "created_at": "original_timestamp",
  "updated_at": "updated_timestamp"
}
```

## Error Handling
- 401 Unauthorized: Invalid or missing JWT
- 403 Forbidden: User doesn't own the task
- 404 Not Found: Task doesn't exist
- 400 Bad Request: Invalid request body
- 500 Internal Server Error: Database errors