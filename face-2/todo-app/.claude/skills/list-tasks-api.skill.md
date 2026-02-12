# List Tasks API

## Purpose
List all tasks belonging to the authenticated user.

## Steps
1. Verify JWT token
2. Filter tasks by user_id
3. Support status filtering and sorting

## Output
GET /api/{user_id}/tasks endpoint

## Implementation Details

### Authentication
- Verify JWT token from Authorization header
- Extract user identity from token payload
- Ensure user exists and is active

### Task Filtering
- Filter tasks by authenticated user's user_id
- Ensure user can only access their own tasks
- Support optional query parameters for filtering

### Optional Filters
- `status`: Filter by completion status (e.g., "completed", "pending")
- `sort`: Sort by field (e.g., "created_at", "due_date", "title")
- `order`: Sort order ("asc", "desc")
- `limit`: Number of tasks to return
- `offset`: Offset for pagination

### Database Operations
- Query tasks filtered by user_id
- Apply optional filters and sorting
- Handle database errors gracefully
- Return paginated results if needed

## Expected Query Parameters
```
GET /api/{user_id}/tasks?status=pending&sort=created_at&order=desc&limit=10&offset=0
```

## Expected Response Format
```json
{
  "tasks": [
    {
      "id": "task_id",
      "user_id": "authenticated_user_id",
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "total_count": 15,
  "limit": 10,
  "offset": 0
}
```

## Error Handling
- 401 Unauthorized: Invalid or missing JWT
- 403 Forbidden: User attempting to access other user's tasks
- 500 Internal Server Error: Database errors