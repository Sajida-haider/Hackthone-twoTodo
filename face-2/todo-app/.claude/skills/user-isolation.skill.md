# User Isolation

## Purpose
Ensure users can only access their own data.

## Steps
1. Extract user_id from JWT
2. Match with user_id in request path
3. Filter all database queries by user_id

## Output
Strict user data isolation

## Implementation Details

### JWT Token Processing
- Extract user_id from JWT token payload
- Verify token signature and validity
- Handle token expiration and invalidation
- Ensure user_id is present and valid in token

### Request Path Validation
- Compare user_id from JWT with user_id in URL path
- Return 403 Forbidden if IDs don't match
- Allow admin users to access other users' data if applicable
- Validate user_id format and existence

### Database Query Filtering
- Apply user_id filter to all database queries
- Ensure every SELECT, UPDATE, DELETE includes user_id condition
- Use parameterized queries to prevent injection
- Implement consistent filtering across all data access layers

### Middleware Implementation
- Create authentication middleware to verify JWT
- Create authorization middleware to check user_id matching
- Apply middleware to all protected endpoints
- Cache user identity for performance optimization

### Security Measures
- Prevent direct object reference (IDOR) attacks
- Validate user permissions for each operation
- Log access attempts for audit purposes
- Implement rate limiting per user

## Example Implementation Pattern
```python
def get_user_tasks(user_id_from_token, user_id_from_path):
    # Verify user_id consistency
    if user_id_from_token != user_id_from_path:
        raise PermissionError("User ID mismatch")

    # Apply user_id filter to database query
    return db.query(Task).filter(Task.user_id == user_id_from_token).all()
```

## Error Handling
- 401 Unauthorized: Invalid or missing JWT
- 403 Forbidden: User ID mismatch or insufficient permissions
- 404 Not Found: Requested resource doesn't exist for user
- 500 Internal Server Error: System errors during verification