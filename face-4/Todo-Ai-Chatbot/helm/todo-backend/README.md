# Todo Backend Helm Chart

This Helm chart deploys the Todo AI Chatbot backend (FastAPI) to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.x
- Docker image `todo-backend:local` available in Minikube
- Neon PostgreSQL database (connection string required)
- OpenAI API key (for AI chatbot functionality)

## Installation

### 1. Build Docker Image in Minikube

```bash
# Configure Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build the backend image
docker build -t todo-backend:local -f docker/backend/Dockerfile .

# Verify image is available
minikube ssh
docker images | grep todo-backend
exit
```

### 2. Configure Secrets

**IMPORTANT**: Update the secrets in `values.yaml` before deployment:

```yaml
secrets:
  databaseUrl: "postgresql://user:password@neon.tech:5432/todo_db"
  betterAuthSecret: "your-secure-secret-key"
  openaiApiKey: "sk-your-openai-api-key"
```

**Security Best Practice**: Use a separate values file for secrets:

```bash
# Create secrets.yaml (add to .gitignore!)
cat > secrets.yaml <<EOF
secrets:
  databaseUrl: "postgresql://user:password@neon.tech:5432/todo_db"
  betterAuthSecret: "$(openssl rand -hex 32)"
  openaiApiKey: "sk-your-openai-api-key"
EOF

# Install with secrets file
helm install todo-backend ./helm/todo-backend -f secrets.yaml
```

### 3. Install the Chart

```bash
# Install with default values
helm install todo-backend ./helm/todo-backend

# Install with custom values
helm install todo-backend ./helm/todo-backend \
  --set replicaCount=2 \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.betterAuthSecret="your-secret" \
  --set secrets.openaiApiKey="sk-..."
```

### 4. Verify Deployment

```bash
# Check pod status
kubectl get pods -l app=todo-backend

# Check service
kubectl get svc todo-backend

# Check logs
kubectl logs -l app=todo-backend

# Test health endpoint
kubectl port-forward svc/todo-backend 8000:8000
curl http://localhost:8000/health
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `todo-backend` |
| `image.tag` | Image tag | `local` |
| `image.pullPolicy` | Image pull policy | `Never` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `resources.limits.cpu` | CPU limit | `1000m` |
| `resources.limits.memory` | Memory limit | `1Gi` |
| `resources.requests.cpu` | CPU request | `200m` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `config.apiHost` | API host | `0.0.0.0` |
| `config.apiPort` | API port | `8000` |
| `config.logLevel` | Log level | `INFO` |
| `secrets.databaseUrl` | PostgreSQL connection string | *Required* |
| `secrets.betterAuthSecret` | JWT signing secret | *Required* |
| `secrets.openaiApiKey` | OpenAI API key | *Required* |

## Customization

### Custom Values File

Create a `custom-values.yaml`:

```yaml
replicaCount: 2

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 512Mi

config:
  logLevel: "DEBUG"
  corsOrigins: "http://todo-frontend:3000,http://custom-frontend:3000"
```

Install with custom values:

```bash
helm install todo-backend ./helm/todo-backend \
  -f custom-values.yaml \
  -f secrets.yaml
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade todo-backend ./helm/todo-backend \
  --set replicaCount=3

# Upgrade with custom values file
helm upgrade todo-backend ./helm/todo-backend \
  -f custom-values.yaml \
  -f secrets.yaml
```

## Rollback

```bash
# List releases
helm list

# Rollback to previous version
helm rollback todo-backend

# Rollback to specific revision
helm rollback todo-backend 1
```

## Uninstallation

```bash
# Uninstall the release
helm uninstall todo-backend

# Verify removal
kubectl get pods -l app=todo-backend
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -l app=todo-backend

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# - Database connection failed: Check DATABASE_URL
# - Missing secrets: Verify secrets are set in values.yaml
# - Image pull errors: Ensure image exists in Minikube
```

### Database Connection Errors

If you see database connection errors in logs:

1. Verify DATABASE_URL format:
   ```
   postgresql://username:password@host:port/database
   ```

2. Test connection from pod:
   ```bash
   kubectl exec -it <pod-name> -- bash
   python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
   ```

3. Check network connectivity:
   ```bash
   kubectl exec -it <pod-name> -- ping neon.tech
   ```

### Health Check Failures

```bash
# Check health endpoint
kubectl port-forward <pod-name> 8000:8000
curl http://localhost:8000/health

# Check probe configuration
kubectl describe pod <pod-name> | grep -A 10 "Liveness\|Readiness"

# View detailed logs
kubectl logs <pod-name> --tail=100
```

### Secret Management

```bash
# View secret (base64 encoded)
kubectl get secret todo-backend-secret -o yaml

# Decode secret value
kubectl get secret todo-backend-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Update secret
kubectl create secret generic todo-backend-secret \
  --from-literal=DATABASE_URL="new-connection-string" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secret
kubectl rollout restart deployment todo-backend
```

## Health Checks

The chart includes liveness and readiness probes:

- **Liveness Probe**: Checks `/health` every 30s
- **Readiness Probe**: Checks `/health` every 10s

## Scaling

```bash
# Scale manually
kubectl scale deployment todo-backend --replicas=3

# Or via Helm
helm upgrade todo-backend ./helm/todo-backend --set replicaCount=3

# Verify scaling
kubectl get pods -l app=todo-backend
```

## Monitoring

```bash
# Watch pod status
kubectl get pods -l app=todo-backend -w

# Stream logs
kubectl logs -f -l app=todo-backend

# Check resource usage
kubectl top pods -l app=todo-backend

# View API documentation
kubectl port-forward svc/todo-backend 8000:8000
# Open http://localhost:8000/docs in browser
```

## Security Considerations

1. **Never commit secrets to version control**
   - Add `secrets.yaml` to `.gitignore`
   - Use Kubernetes Secrets or external secret management

2. **Rotate secrets regularly**
   ```bash
   # Generate new secret
   openssl rand -hex 32

   # Update and restart
   helm upgrade todo-backend ./helm/todo-backend \
     --set secrets.betterAuthSecret="new-secret"
   ```

3. **Use different secrets per environment**
   - Development: `secrets-dev.yaml`
   - Staging: `secrets-staging.yaml`
   - Production: External secret manager

4. **Limit CORS origins**
   ```yaml
   config:
     corsOrigins: "http://todo-frontend:3000"  # Specific origins only
   ```

## Dependencies

This chart is typically deployed alongside the frontend:

```bash
# Deploy backend first
helm install todo-backend ./helm/todo-backend -f secrets.yaml

# Then deploy frontend
helm install todo-frontend ./helm/todo-frontend
```

## API Endpoints

Once deployed, the backend exposes:

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs` (Swagger UI)
- **API Schema**: `GET /openapi.json`
- **Task API**: `GET/POST/PUT/DELETE /api/tasks`
- **Chat API**: `POST /api/chat`

## Support

For issues and questions:
- Check logs: `kubectl logs <pod-name>`
- Check events: `kubectl get events`
- Describe resources: `kubectl describe pod/svc/deployment <name>`
- Test health: `kubectl port-forward svc/todo-backend 8000:8000 && curl http://localhost:8000/health`
