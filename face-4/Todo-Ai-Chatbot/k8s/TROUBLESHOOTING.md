# Kubernetes Troubleshooting Guide

This guide covers common issues and their solutions when deploying the Todo AI Chatbot to Kubernetes.

## Table of Contents

1. [Pod Issues](#pod-issues)
2. [Image Issues](#image-issues)
3. [Network Issues](#network-issues)
4. [Database Issues](#database-issues)
5. [Health Check Issues](#health-check-issues)
6. [Resource Issues](#resource-issues)
7. [Helm Issues](#helm-issues)
8. [Minikube Issues](#minikube-issues)

## Pod Issues

### Pods Stuck in Pending State

**Symptoms**: Pods show `Pending` status indefinitely

**Diagnosis**:
```bash
kubectl describe pod <pod-name>
# Look for events showing why pod can't be scheduled
```

**Common Causes**:
1. **Insufficient resources**
   ```bash
   # Check node resources
   kubectl describe nodes

   # Solution: Increase Minikube resources
   minikube stop
   minikube start --memory=8192 --cpus=4
   ```

2. **Image pull issues**
   ```bash
   # Check if image exists
   minikube ssh
   docker images | grep todo

   # Solution: Rebuild images in Minikube context
   eval $(minikube docker-env)
   docker build -t todo-backend:local -f docker/backend/Dockerfile .
   ```

### Pods in CrashLoopBackOff

**Symptoms**: Pods repeatedly crash and restart

**Diagnosis**:
```bash
# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Logs from previous crash

# Check events
kubectl describe pod <pod-name>
```

**Common Causes**:
1. **Application errors**
   - Check logs for error messages
   - Verify environment variables are set correctly
   - Test application locally first

2. **Database connection failures**
   ```bash
   # Verify DATABASE_URL
   kubectl get secret todo-backend-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d

   # Test connection from pod
   kubectl exec -it <pod-name> -- python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
   ```

3. **Missing dependencies**
   - Verify Dockerfile includes all required dependencies
   - Rebuild image with updated requirements

### Pods Not Ready

**Symptoms**: Pods show `0/1` in READY column

**Diagnosis**:
```bash
# Check readiness probe
kubectl describe pod <pod-name> | grep -A 10 "Readiness"

# Test health endpoint
kubectl port-forward <pod-name> 8000:8000
curl http://localhost:8000/health
```

**Solutions**:
1. **Increase probe delays**
   ```yaml
   # In values.yaml
   readinessProbe:
     initialDelaySeconds: 30  # Increase if app takes longer to start
     periodSeconds: 10
     timeoutSeconds: 5
   ```

2. **Fix health endpoint**
   - Ensure `/health` endpoint is implemented
   - Verify endpoint returns 200 status code

## Image Issues

### ImagePullBackOff Error

**Symptoms**: Pods show `ImagePullBackOff` or `ErrImagePull`

**Diagnosis**:
```bash
kubectl describe pod <pod-name>
# Look for "Failed to pull image" messages
```

**Solutions**:
1. **Image not in Minikube**
   ```bash
   # Verify image exists
   minikube ssh
   docker images | grep todo
   exit

   # If missing, rebuild in Minikube context
   eval $(minikube docker-env)
   docker build -t todo-backend:local -f docker/backend/Dockerfile .
   docker build -t todo-frontend:local -f docker/frontend/Dockerfile .
   ```

2. **Wrong imagePullPolicy**
   ```yaml
   # In values.yaml, ensure:
   image:
     pullPolicy: Never  # For local images
   ```

3. **Wrong image tag**
   ```yaml
   # Verify image tag matches
   image:
     repository: todo-backend
     tag: local
   ```

### Image Too Large

**Symptoms**: Image build takes very long or fails

**Solutions**:
1. **Use multi-stage builds** (already implemented in Dockerfiles)
2. **Optimize .dockerignore**
   ```
   # Add to .dockerignore
   node_modules/
   .git/
   *.log
   ```

3. **Use Alpine base images** (already implemented)

## Network Issues

### Frontend Can't Reach Backend

**Symptoms**: Frontend shows API connection errors

**Diagnosis**:
```bash
# Check backend service
kubectl get svc todo-backend

# Check service endpoints
kubectl get endpoints todo-backend

# Test from frontend pod
kubectl exec -it <frontend-pod> -- curl http://todo-backend:8000/health
```

**Solutions**:
1. **Verify service name in frontend config**
   ```yaml
   # In helm/todo-frontend/values.yaml
   config:
     nextPublicApiUrl: "http://todo-backend:8000"  # Must match backend service name
   ```

2. **Check backend is running**
   ```bash
   kubectl get pods -l app=todo-backend
   kubectl logs -l app=todo-backend
   ```

3. **Verify network policies** (if any)
   ```bash
   kubectl get networkpolicies
   ```

### Can't Access Application from Browser

**Symptoms**: Can't access frontend URL

**Solutions**:
1. **Use Minikube service command**
   ```bash
   minikube service todo-frontend
   # Or get URL
   minikube service todo-frontend --url
   ```

2. **Check NodePort**
   ```bash
   kubectl get svc todo-frontend
   # Note the NodePort (e.g., 30080)

   # Access via: http://<minikube-ip>:<nodeport>
   minikube ip
   ```

3. **Use port forwarding**
   ```bash
   kubectl port-forward svc/todo-frontend 3000:3000
   # Access via: http://localhost:3000
   ```

## Database Issues

### Connection Refused

**Symptoms**: Backend logs show "connection refused" errors

**Solutions**:
1. **Verify DATABASE_URL format**
   ```
   postgresql://username:password@host:port/database
   ```

2. **Check network connectivity**
   ```bash
   # Test from backend pod
   kubectl exec -it <backend-pod> -- ping neon.tech
   kubectl exec -it <backend-pod> -- nc -zv neon.tech 5432
   ```

3. **Verify credentials**
   ```bash
   # Decode secret
   kubectl get secret todo-backend-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d

   # Test connection
   kubectl exec -it <backend-pod> -- python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
   ```

### SSL/TLS Errors

**Symptoms**: "SSL connection error" in logs

**Solutions**:
1. **Add SSL mode to connection string**
   ```
   postgresql://user:pass@host:5432/db?sslmode=require
   ```

2. **For Neon, use sslmode=require**
   ```yaml
   # In secrets.yaml
   secrets:
     databaseUrl: "postgresql://user:pass@neon.tech:5432/db?sslmode=require"
   ```

## Health Check Issues

### Liveness Probe Failures

**Symptoms**: Pods restart frequently

**Diagnosis**:
```bash
# Check events
kubectl get events --field-selector involvedObject.name=<pod-name>

# Check logs before restart
kubectl logs <pod-name> --previous
```

**Solutions**:
1. **Increase probe timeouts**
   ```yaml
   livenessProbe:
     initialDelaySeconds: 60  # Give app more time to start
     periodSeconds: 30
     timeoutSeconds: 5
     failureThreshold: 5  # Allow more failures before restart
   ```

2. **Fix health endpoint**
   - Ensure endpoint responds quickly (< 3 seconds)
   - Don't include heavy operations in health check

### Readiness Probe Failures

**Symptoms**: Pods never become ready, no traffic routed

**Solutions**:
1. **Check health endpoint**
   ```bash
   kubectl port-forward <pod-name> 8000:8000
   curl -v http://localhost:8000/health
   ```

2. **Adjust probe settings**
   ```yaml
   readinessProbe:
     initialDelaySeconds: 20
     periodSeconds: 10
     timeoutSeconds: 3
     successThreshold: 1
     failureThreshold: 3
   ```

## Resource Issues

### Out of Memory (OOMKilled)

**Symptoms**: Pods show `OOMKilled` status

**Diagnosis**:
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check resource usage
kubectl top pod <pod-name>
```

**Solutions**:
1. **Increase memory limits**
   ```yaml
   # In values.yaml
   resources:
     limits:
       memory: 2Gi  # Increase from 1Gi
     requests:
       memory: 512Mi
   ```

2. **Optimize application**
   - Reduce memory usage in code
   - Use connection pooling for database
   - Implement caching

### CPU Throttling

**Symptoms**: Application slow, high CPU usage

**Solutions**:
1. **Increase CPU limits**
   ```yaml
   resources:
     limits:
       cpu: 2000m  # Increase from 1000m
     requests:
       cpu: 500m
   ```

2. **Scale horizontally**
   ```bash
   kubectl scale deployment todo-backend --replicas=3
   ```

## Helm Issues

### Helm Install Fails

**Diagnosis**:
```bash
# Dry run to check for errors
helm install todo-backend ./helm/todo-backend --dry-run --debug

# Lint chart
helm lint ./helm/todo-backend
```

**Common Issues**:
1. **Template errors**
   ```bash
   # Test template rendering
   helm template todo-backend ./helm/todo-backend
   ```

2. **Missing values**
   ```bash
   # Verify required values are set
   helm show values ./helm/todo-backend
   ```

### Helm Upgrade Fails

**Solutions**:
1. **Check release status**
   ```bash
   helm list
   helm status todo-backend
   ```

2. **Rollback if needed**
   ```bash
   helm rollback todo-backend
   ```

3. **Force upgrade**
   ```bash
   helm upgrade todo-backend ./helm/todo-backend --force
   ```

## Minikube Issues

### Minikube Won't Start

**Solutions**:
1. **Delete and recreate**
   ```bash
   minikube delete
   minikube start --memory=4096 --cpus=2
   ```

2. **Check system resources**
   - Ensure enough RAM available
   - Close other applications
   - Check disk space

3. **Try different driver**
   ```bash
   minikube start --driver=docker
   # Or
   minikube start --driver=virtualbox
   ```

### Minikube Slow

**Solutions**:
1. **Increase resources**
   ```bash
   minikube stop
   minikube start --memory=8192 --cpus=4
   ```

2. **Clean up**
   ```bash
   # Remove unused images
   minikube ssh
   docker system prune -a
   exit
   ```

## General Debugging Commands

```bash
# Check everything
kubectl get all

# Describe resource
kubectl describe <resource-type> <name>

# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
kubectl logs -l app=todo-backend --tail=100

# Execute commands in pod
kubectl exec -it <pod-name> -- bash
kubectl exec -it <pod-name> -- env

# Port forward for testing
kubectl port-forward <pod-name> 8000:8000

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check resource usage
kubectl top nodes
kubectl top pods

# Debug with temporary pod
kubectl run debug --rm -it --image=busybox -- sh
```

## Getting Help

If issues persist:
1. Check logs: `kubectl logs <pod-name>`
2. Check events: `kubectl get events`
3. Describe resources: `kubectl describe <resource> <name>`
4. Review Helm chart READMEs
5. Consult Kubernetes documentation
6. Check Minikube documentation
