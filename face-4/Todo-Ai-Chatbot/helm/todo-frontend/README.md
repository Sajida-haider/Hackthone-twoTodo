# Todo Frontend Helm Chart

This Helm chart deploys the Todo AI Chatbot frontend (Next.js) to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.x
- Docker image `todo-frontend:local` available in Minikube

## Installation

### 1. Build Docker Image in Minikube

```bash
# Configure Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build the frontend image
docker build -t todo-frontend:local -f docker/frontend/Dockerfile .

# Verify image is available
minikube ssh
docker images | grep todo-frontend
exit
```

### 2. Install the Chart

```bash
# Install with default values
helm install todo-frontend ./helm/todo-frontend

# Install with custom values
helm install todo-frontend ./helm/todo-frontend \
  --set replicaCount=2 \
  --set config.nextPublicApiUrl=http://todo-backend:8000
```

### 3. Verify Deployment

```bash
# Check pod status
kubectl get pods -l app=todo-frontend

# Check service
kubectl get svc todo-frontend

# Get NodePort
kubectl get svc todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Access the application
minikube service todo-frontend --url
# Or manually: http://$(minikube ip):30080
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `todo-frontend` |
| `image.tag` | Image tag | `local` |
| `image.pullPolicy` | Image pull policy | `Never` |
| `service.type` | Service type | `NodePort` |
| `service.port` | Service port | `3000` |
| `service.nodePort` | NodePort (if type is NodePort) | `30080` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `config.nextPublicApiUrl` | Backend API URL | `http://todo-backend:8000` |
| `config.nodeEnv` | Node environment | `production` |

## Customization

### Custom Values File

Create a `custom-values.yaml`:

```yaml
replicaCount: 3

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

config:
  nextPublicApiUrl: "http://custom-backend:8000"
```

Install with custom values:

```bash
helm install todo-frontend ./helm/todo-frontend -f custom-values.yaml
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade todo-frontend ./helm/todo-frontend \
  --set replicaCount=3

# Upgrade with custom values file
helm upgrade todo-frontend ./helm/todo-frontend -f custom-values.yaml
```

## Rollback

```bash
# List releases
helm list

# Rollback to previous version
helm rollback todo-frontend

# Rollback to specific revision
helm rollback todo-frontend 1
```

## Uninstallation

```bash
# Uninstall the release
helm uninstall todo-frontend

# Verify removal
kubectl get pods -l app=todo-frontend
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -l app=todo-frontend

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Image Pull Errors

If you see `ImagePullBackOff`:

1. Verify image exists in Minikube:
   ```bash
   minikube ssh
   docker images | grep todo-frontend
   ```

2. Ensure `imagePullPolicy: Never` is set in values.yaml

3. Rebuild image in Minikube context:
   ```bash
   eval $(minikube docker-env)
   docker build -t todo-frontend:local -f docker/frontend/Dockerfile .
   ```

### Health Check Failures

```bash
# Check health endpoint
kubectl port-forward <pod-name> 3000:3000
curl http://localhost:3000/api/health

# Check probe configuration
kubectl describe pod <pod-name> | grep -A 10 "Liveness\|Readiness"
```

### Service Not Accessible

```bash
# Check service
kubectl get svc todo-frontend

# Get service URL
minikube service todo-frontend --url

# Check endpoints
kubectl get endpoints todo-frontend
```

## Health Checks

The chart includes liveness and readiness probes:

- **Liveness Probe**: Checks `/api/health` every 30s
- **Readiness Probe**: Checks `/api/health` every 10s

## Scaling

```bash
# Scale manually
kubectl scale deployment todo-frontend --replicas=3

# Or via Helm
helm upgrade todo-frontend ./helm/todo-frontend --set replicaCount=3
```

## Monitoring

```bash
# Watch pod status
kubectl get pods -l app=todo-frontend -w

# Stream logs
kubectl logs -f -l app=todo-frontend

# Check resource usage
kubectl top pods -l app=todo-frontend
```

## Dependencies

This chart requires the backend service to be deployed:

```bash
# Install backend first
helm install todo-backend ./helm/todo-backend

# Then install frontend
helm install todo-frontend ./helm/todo-frontend
```

## Support

For issues and questions:
- Check logs: `kubectl logs <pod-name>`
- Check events: `kubectl get events`
- Describe resources: `kubectl describe pod/svc/deployment <name>`
