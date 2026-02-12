# Frontend Health Check

## Health Check Endpoint

**Endpoint**: `/api/health`
**Method**: GET
**Port**: 3000

## Response

### Success (200 OK)
```json
{
  "status": "healthy",
  "service": "todo-frontend",
  "timestamp": "2026-02-10T23:00:00Z"
}
```

### Failure (503 Service Unavailable)
```json
{
  "status": "unhealthy",
  "service": "todo-frontend",
  "error": "Service not ready"
}
```

## Docker Health Check

The Dockerfile includes a built-in health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"
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
    path: /api/health
    port: 3000
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
    path: /api/health
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
```

## Testing Health Check

### Local Testing
```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Check Docker container health
docker ps
# Look for "healthy" status in the STATUS column
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
```

## Implementation Notes

The health check endpoint should be implemented in the Next.js application at:
- `frontend/src/app/api/health/route.ts` (App Router)

Example implementation:
```typescript
// frontend/src/app/api/health/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: 'todo-frontend',
    timestamp: new Date().toISOString(),
  });
}
```

## Troubleshooting

### Health Check Failing
1. Check if the application is running: `docker logs <container-id>`
2. Verify the health endpoint is accessible: `curl http://localhost:3000/api/health`
3. Check for errors in application logs
4. Verify environment variables are set correctly
5. Ensure the backend API is reachable

### Container Marked Unhealthy
1. Check Docker logs: `docker logs <container-id>`
2. Increase `start-period` if the application takes longer to start
3. Increase `timeout` if health checks are timing out
4. Check resource constraints (CPU, memory)
