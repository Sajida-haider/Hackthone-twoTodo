# Backend Health Check

## Health Check Endpoint

**Endpoint**: `/health`
**Method**: GET
**Port**: 8000

## Response

### Success (200 OK)
```json
{
  "status": "healthy",
  "service": "todo-backend",
  "timestamp": "2026-02-10T23:00:00Z",
  "database": "connected"
}
```

### Failure (503 Service Unavailable)
```json
{
  "status": "unhealthy",
  "service": "todo-backend",
  "error": "Database connection failed"
}
```

## Docker Health Check

The Dockerfile includes a built-in health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1
```

**Parameters**:
- **interval**: 30 seconds between checks
- **timeout**: 3 seconds for each check
- **start-period**: 40 seconds grace period on startup
- **retries**: 3 consecutive failures before marking unhealthy

## Kubernetes Probes

### Liveness Probe
Checks if the container is alive and should be restarted if failing:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 40
  periodSeconds: 30
  timeoutSeconds: 3
  failureThreshold: 3
```

### Readiness Probe
Checks if the container is ready to accept traffic:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
```

## Testing Health Check

### Local Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Check Docker container health
docker ps
# Look for "healthy" status in the STATUS column

# Test with detailed output
curl -v http://localhost:8000/health
```

### Kubernetes Testing
```bash
# Check pod health
kubectl get pods
# Look for READY column showing 1/1

# Describe pod to see probe results
kubectl describe pod <pod-name>

# Check events for probe failures
kubectl get events --field-selector involvedObject.name=<pod-name>

# Check logs
kubectl logs <pod-name>
```

## Implementation Notes

The health check endpoint should be implemented in the FastAPI application at:
- `backend/app/main.py` or `backend/app/api/health.py`

Example implementation:
```python
# backend/app/main.py
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    try:
        # Optional: Check database connection
        # db.execute("SELECT 1")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "service": "todo-backend",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "todo-backend",
                "error": str(e)
            }
        )
```

## Health Check Components

The health check should verify:
1. **Application Status**: FastAPI server is running
2. **Database Connection**: PostgreSQL connection is active
3. **Dependencies**: Critical services are reachable

## Troubleshooting

### Health Check Failing
1. Check if the application is running: `docker logs <container-id>`
2. Verify the health endpoint is accessible: `curl http://localhost:8000/health`
3. Check database connectivity: Verify DATABASE_URL is correct
4. Check for errors in application logs
5. Verify environment variables are set correctly

### Container Marked Unhealthy
1. Check Docker logs: `docker logs <container-id>`
2. Increase `start-period` if the application takes longer to start
3. Increase `timeout` if health checks are timing out
4. Check resource constraints (CPU, memory)
5. Verify database is accessible from container

### Database Connection Issues
1. Verify DATABASE_URL format: `postgresql://user:pass@host:port/db`
2. Check network connectivity to Neon PostgreSQL
3. Verify database credentials are correct
4. Check firewall rules and security groups
5. Test connection manually: `psql $DATABASE_URL`

## API Documentation

FastAPI automatically generates API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

The health endpoint will be included in the API documentation.
