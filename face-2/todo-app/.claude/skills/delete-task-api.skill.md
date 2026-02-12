# Delete Task API

## Purpose
Delete a task owned by the authenticated user.

## Steps
1. Verify JWT token
2. Confirm task belongs to user
3. Remove task from database

## Output
DELETE /api/{user_id}/tasks/{id} endpoint

## Implementation Details

### Authentication
- Verify JWT token from Authorization header
- Extract user identity from token payload
- Ensure user exists and is active

### Task Ownership Verification
- Verify that the authenticated user owns the task
- Compare user_id in JWT with user_id in task record
- Return 403 Forbidden if user doesn't own the task
- Check if task exists before attempting deletion

### Database Operations
- Delete the specified task record from the database
- Handle foreign key constraints if any
- Handle database errors gracefully
- Return appropriate response indicating success or failure

### Soft Delete Option
- Consider implementing soft delete (mark as deleted instead of removing)
- Set deleted_at timestamp instead of physically removing
- Update to reflect soft delete approach if required

## Expected Response Format
Success:
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

Failure:
```json
{
  "success": false,
  "error": "Error message explaining failure reason"
}
```

## Error Handling
- 401 Unauthorized: Invalid or missing JWT
- 403 Forbidden: User doesn't own the task
- 404 Not Found: Task doesn't exist
- 500 Internal Server Error: Database errors
- 409 Conflict: Cannot delete due to related records