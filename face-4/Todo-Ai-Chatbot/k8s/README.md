# Phase IV: Local Kubernetes Deployment Guide

This guide provides step-by-step instructions for deploying the Todo AI Chatbot to a local Kubernetes cluster using Minikube.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Building Docker Images](#building-docker-images)
4. [Deploying to Kubernetes](#deploying-to-kubernetes)
5. [Accessing the Application](#accessing-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Cleanup](#cleanup)

## Prerequisites

### Required Tools

- **Docker Desktop** (20.10+)
  - Download: https://www.docker.com/products/docker-desktop/
  - Verify: `docker --version`

- **Minikube** (latest)
  - Download: https://minikube.sigs.k8s.io/docs/start/
  - Verify: `minikube version`

- **kubectl** (1.19+)
  - Usually included with Docker Desktop
  - Verify: `kubectl version --client`

- **Helm** (3.x)
  - Download: https://helm.sh/docs/intro/install/
  - Verify: `helm version`

### Required Credentials

- **Neon PostgreSQL**: Database connection string
- **OpenAI API Key**: For AI chatbot functionality
- **JWT Secret**: For authentication (generate with `openssl rand -hex 32`)

## Environment Setup

### 1. Start Minikube

```bash
# Start Minikube with adequate resources
minikube start --memory=4096 --cpus=2

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

### 2. Configure Docker for Minikube

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify configuration
docker ps
```

**Note**: This configuration is session-specific. Run this command in each new terminal session.

### 3. Create Secrets File

Create a `secrets.yaml` file (add to `.gitignore`):

```yaml
secrets:
  databaseUrl: "postgresql://user:password@neon.tech:5432/todo_db"
  betterAuthSecret: "your-32-character-secret-key"
  openaiApiKey: "sk-your-openai-api-key"
```

Generate a secure secret:
```bash
openssl rand -hex 32
```

## Building Docker Images

### 1. Build Backend Image

```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
docker build -t todo-backend:local -f docker/backend/Dockerfile .

# Verify image
docker images | grep todo-backend
```

Expected output:
```
todo-backend    local    <image-id>    <time>    <size>
```

### 2. Build Frontend Image

```bash
# Build frontend image
docker build -t todo-frontend:local -f docker/frontend/Dockerfile .

# Verify image
docker images | grep todo-frontend
```

Expected output:
```
todo-frontend    local    <image-id>    <time>    <size>
```

### 3. Verify Images in Minikube

```bash
# SSH into Minikube
minikube ssh

# List images
docker images | grep todo

# Exit Minikube
exit
```

## Deploying to Kubernetes

### 1. Deploy Backend

```bash
# Install backend Helm chart
helm install todo-backend ./helm/todo-backend -f secrets.yaml

# Wait for backend to be ready
kubectl wait --for=condition=Ready pod -l app=todo-backend --timeout=120s

# Verify deployment
kubectl get pods -l app=todo-backend
kubectl get svc todo-backend
```

Expected output:
```
NAME                            READY   STATUS    RESTARTS   AGE
todo-backend-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

### 2. Deploy Frontend

```bash
# Install frontend Helm chart
helm install todo-frontend ./helm/todo-frontend

# Wait for frontend to be ready
kubectl wait --for=condition=Ready pod -l app=todo-frontend --timeout=120s

# Verify deployment
kubectl get pods -l app=todo-frontend
kubectl get svc todo-frontend
```

Expected output:
```
NAME                             READY   STATUS    RESTARTS   AGE
todo-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

### 3. Verify All Resources

```bash
# Check all pods
kubectl get pods

# Check all services
kubectl get svc

# Check deployments
kubectl get deployments

# Check configmaps and secrets
kubectl get configmaps
kubectl get secrets
```

## Accessing the Application

### Method 1: Minikube Service (Recommended)

```bash
# Get frontend URL
minikube service todo-frontend --url

# Open in browser
minikube service todo-frontend
```

### Method 2: NodePort

```bash
# Get Minikube IP
minikube ip

# Get NodePort
kubectl get svc todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Access application
# URL: http://<minikube-ip>:<nodeport>
# Example: http://192.168.49.2:30080
```

### Method 3: Port Forward

```bash
# Forward frontend port
kubectl port-forward svc/todo-frontend 3000:3000

# Access application
# URL: http://localhost:3000
```

### Verify Backend API

```bash
# Forward backend port
kubectl port-forward svc/todo-backend 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# View API documentation
# Open http://localhost:8000/docs in browser
```

## Monitoring and Logs

### View Logs

```bash
# Frontend logs
kubectl logs -l app=todo-frontend --tail=50 -f

# Backend logs
kubectl logs -l app=todo-backend --tail=50 -f

# All logs
kubectl logs -l 'app in (todo-frontend,todo-backend)' --tail=50 -f
```

### Check Pod Status

```bash
# Watch pod status
kubectl get pods -w

# Describe pod for details
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Resource Usage

```bash
# Enable metrics server (if not already enabled)
minikube addons enable metrics-server

# Wait a minute for metrics to be collected
sleep 60

# Check resource usage
kubectl top nodes
kubectl top pods
```

## Scaling

### Scale Frontend

```bash
# Scale to 3 replicas
kubectl scale deployment todo-frontend --replicas=3

# Verify scaling
kubectl get pods -l app=todo-frontend

# Or use Helm
helm upgrade todo-frontend ./helm/todo-frontend --set replicaCount=3
```

### Scale Backend

```bash
# Scale to 2 replicas
kubectl scale deployment todo-backend --replicas=2

# Verify scaling
kubectl get pods -l app=todo-backend
```

## Configuration Updates

### Update Frontend Configuration

```bash
# Edit values
# Update helm/todo-frontend/values.yaml

# Apply changes
helm upgrade todo-frontend ./helm/todo-frontend

# Verify update
kubectl rollout status deployment/todo-frontend
```

### Update Backend Secrets

```bash
# Edit secrets.yaml with new values

# Apply changes
helm upgrade todo-backend ./helm/todo-backend -f secrets.yaml

# Pods will automatically restart with new secrets
kubectl get pods -l app=todo-backend -w
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# - ImagePullBackOff: Image not in Minikube (rebuild with eval $(minikube docker-env))
# - CrashLoopBackOff: Application error (check logs)
# - Pending: Resource constraints (check minikube resources)
```

### Database Connection Errors

```bash
# Check backend logs
kubectl logs -l app=todo-backend

# Verify DATABASE_URL secret
kubectl get secret todo-backend-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Test connection from pod
kubectl exec -it <backend-pod> -- python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### Frontend Can't Reach Backend

```bash
# Check backend service
kubectl get svc todo-backend

# Verify service endpoints
kubectl get endpoints todo-backend

# Test from frontend pod
kubectl exec -it <frontend-pod> -- curl http://todo-backend:8000/health
```

### Health Checks Failing

```bash
# Check probe configuration
kubectl describe pod <pod-name> | grep -A 10 "Liveness\|Readiness"

# Test health endpoint manually
kubectl port-forward <pod-name> 8000:8000
curl http://localhost:8000/health

# Increase probe timeouts if needed
# Edit values.yaml and helm upgrade
```

### Minikube Issues

```bash
# Check Minikube status
minikube status

# Restart Minikube
minikube stop
minikube start --memory=4096 --cpus=2

# Delete and recreate cluster
minikube delete
minikube start --memory=4096 --cpus=2
```

## Cleanup

### Uninstall Applications

```bash
# Uninstall frontend
helm uninstall todo-frontend

# Uninstall backend
helm uninstall todo-backend

# Verify removal
kubectl get pods
kubectl get svc
```

### Stop Minikube

```bash
# Stop Minikube (preserves cluster)
minikube stop

# Delete Minikube cluster (removes everything)
minikube delete
```

### Clean Docker Images

```bash
# Remove local images
docker rmi todo-frontend:local
docker rmi todo-backend:local

# Clean up unused images
docker image prune -a
```

## Quick Reference

### Essential Commands

```bash
# Start Minikube
minikube start --memory=4096 --cpus=2

# Configure Docker
eval $(minikube docker-env)

# Build images
docker build -t todo-backend:local -f docker/backend/Dockerfile .
docker build -t todo-frontend:local -f docker/frontend/Dockerfile .

# Deploy
helm install todo-backend ./helm/todo-backend -f secrets.yaml
helm install todo-frontend ./helm/todo-frontend

# Access application
minikube service todo-frontend

# View logs
kubectl logs -l app=todo-frontend -f
kubectl logs -l app=todo-backend -f

# Cleanup
helm uninstall todo-frontend todo-backend
minikube stop
```

## Next Steps

After successful deployment:

1. **Test the application**: Create tasks, test chat functionality
2. **Experiment with scaling**: Scale pods up and down
3. **Monitor resources**: Use `kubectl top` to monitor usage
4. **Try configuration updates**: Update environment variables via Helm
5. **Explore kubectl-ai**: Use AI-assisted Kubernetes operations (Spec 2)
6. **Analyze with kagent**: Get cluster health insights (Spec 2)

## Support

For issues:
- Check logs: `kubectl logs <pod-name>`
- Check events: `kubectl get events`
- Describe resources: `kubectl describe <resource-type> <name>`
- Consult Helm chart READMEs in `helm/todo-frontend/` and `helm/todo-backend/`
