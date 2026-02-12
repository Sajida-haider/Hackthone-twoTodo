# kubectl-ai Usage Examples

This guide provides examples of using kubectl-ai for natural language Kubernetes operations on the Todo AI Chatbot deployment.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Inspection Operations](#inspection-operations)
3. [Scaling Operations](#scaling-operations)
4. [Debugging Operations](#debugging-operations)
5. [Log Analysis](#log-analysis)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- kubectl-ai installed and configured
- Minikube running with Todo app deployed
- kubectl configured to use Minikube context

### Basic Usage

```bash
# General syntax
kubectl-ai "<natural language query>"

# Get help
kubectl-ai --help

# Show version
kubectl-ai --version
```

### Safety Features

kubectl-ai shows the generated kubectl command before execution:

```bash
$ kubectl-ai "scale todo-frontend to 3 replicas"

Generated command:
  kubectl scale deployment todo-frontend --replicas=3

Execute this command? [y/N]: y
```

## Inspection Operations

### Viewing Pods

**Show all pods**:
```bash
kubectl-ai "show me all pods"
# Generates: kubectl get pods
```

**Show pods for specific app**:
```bash
kubectl-ai "show me all pods for todo-frontend"
# Generates: kubectl get pods -l app=todo-frontend

kubectl-ai "show me all pods for todo-backend"
# Generates: kubectl get pods -l app=todo-backend
```

**Show pod details**:
```bash
kubectl-ai "describe the frontend pod"
# Generates: kubectl describe pod <pod-name>

kubectl-ai "show me detailed information about the backend pod"
# Generates: kubectl describe pod <pod-name>
```

**Check pod status**:
```bash
kubectl-ai "are all pods running"
# Generates: kubectl get pods --field-selector=status.phase=Running

kubectl-ai "show me pods that are not ready"
# Generates: kubectl get pods --field-selector=status.phase!=Running
```

### Viewing Deployments

**Show all deployments**:
```bash
kubectl-ai "show me all deployments"
# Generates: kubectl get deployments

kubectl-ai "list all deployments"
# Generates: kubectl get deployments
```

**Describe specific deployment**:
```bash
kubectl-ai "describe the todo-backend deployment"
# Generates: kubectl describe deployment todo-backend

kubectl-ai "show me details of the frontend deployment"
# Generates: kubectl describe deployment todo-frontend
```

**Check deployment status**:
```bash
kubectl-ai "is the frontend deployment ready"
# Generates: kubectl get deployment todo-frontend

kubectl-ai "show me replica counts for all deployments"
# Generates: kubectl get deployments -o wide
```

### Viewing Services

**Show all services**:
```bash
kubectl-ai "show me all services"
# Generates: kubectl get services

kubectl-ai "list all services"
# Generates: kubectl get svc
```

**Describe specific service**:
```bash
kubectl-ai "describe the todo-frontend service"
# Generates: kubectl describe service todo-frontend

kubectl-ai "show me the backend service details"
# Generates: kubectl describe service todo-backend
```

**Check service endpoints**:
```bash
kubectl-ai "show me endpoints for todo-frontend"
# Generates: kubectl get endpoints todo-frontend

kubectl-ai "what is the NodePort for the frontend service"
# Generates: kubectl get svc todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'
```

### Viewing ConfigMaps and Secrets

**Show ConfigMaps**:
```bash
kubectl-ai "show me all configmaps"
# Generates: kubectl get configmaps

kubectl-ai "describe the frontend configmap"
# Generates: kubectl describe configmap todo-frontend-config
```

**Show Secrets** (values are base64 encoded):
```bash
kubectl-ai "show me all secrets"
# Generates: kubectl get secrets

kubectl-ai "describe the backend secret"
# Generates: kubectl describe secret todo-backend-secret
```

## Scaling Operations

### Scale Up

**Scale frontend**:
```bash
kubectl-ai "scale todo-frontend to 3 replicas"
# Generates: kubectl scale deployment todo-frontend --replicas=3

kubectl-ai "increase frontend replicas to 5"
# Generates: kubectl scale deployment todo-frontend --replicas=5
```

**Scale backend**:
```bash
kubectl-ai "scale todo-backend to 2 replicas"
# Generates: kubectl scale deployment todo-backend --replicas=2
```

### Scale Down

**Reduce replicas**:
```bash
kubectl-ai "scale todo-frontend down to 1 replica"
# Generates: kubectl scale deployment todo-frontend --replicas=1

kubectl-ai "reduce backend to 1 replica"
# Generates: kubectl scale deployment todo-backend --replicas=1
```

### Check Scaling Status

**Verify replica counts**:
```bash
kubectl-ai "show me current replica counts"
# Generates: kubectl get deployments

kubectl-ai "how many frontend pods are running"
# Generates: kubectl get pods -l app=todo-frontend --no-headers | wc -l
```

**Watch scaling progress**:
```bash
kubectl-ai "watch the frontend deployment scale"
# Generates: kubectl get pods -l app=todo-frontend -w
```

## Debugging Operations

### Identify Failing Pods

**Find failing pods**:
```bash
kubectl-ai "show me all failing pods"
# Generates: kubectl get pods --field-selector=status.phase!=Running

kubectl-ai "which pods are in CrashLoopBackOff"
# Generates: kubectl get pods --field-selector=status.phase=Failed
```

**Check specific pod status**:
```bash
kubectl-ai "why is the backend pod failing"
# Generates: kubectl describe pod <pod-name> && kubectl logs <pod-name>

kubectl-ai "what's wrong with the frontend pod"
# Generates: kubectl describe pod <pod-name>
```

### Debug Health Checks

**Check readiness probes**:
```bash
kubectl-ai "debug the frontend readiness probe"
# Generates: kubectl describe pod <pod-name> | grep -A 10 "Readiness"

kubectl-ai "why is the backend pod not ready"
# Generates: kubectl describe pod <pod-name> && kubectl logs <pod-name>
```

**Check liveness probes**:
```bash
kubectl-ai "check the backend liveness probe"
# Generates: kubectl describe pod <pod-name> | grep -A 10 "Liveness"
```

### View Events

**Show recent events**:
```bash
kubectl-ai "show me recent events"
# Generates: kubectl get events --sort-by='.lastTimestamp'

kubectl-ai "show me events for the frontend deployment"
# Generates: kubectl get events --field-selector involvedObject.name=todo-frontend
```

**Filter events by type**:
```bash
kubectl-ai "show me warning events"
# Generates: kubectl get events --field-selector type=Warning

kubectl-ai "show me error events"
# Generates: kubectl get events --field-selector type=Error
```

## Log Analysis

### View Logs

**Show recent logs**:
```bash
kubectl-ai "show me logs for the backend pod"
# Generates: kubectl logs <pod-name>

kubectl-ai "show me frontend logs"
# Generates: kubectl logs -l app=todo-frontend
```

**Show specific number of lines**:
```bash
kubectl-ai "show me the last 50 lines of backend logs"
# Generates: kubectl logs <pod-name> --tail=50

kubectl-ai "show me the last 100 lines of frontend logs"
# Generates: kubectl logs -l app=todo-frontend --tail=100
```

**Follow logs in real-time**:
```bash
kubectl-ai "follow the backend logs"
# Generates: kubectl logs -f <pod-name>

kubectl-ai "stream frontend logs"
# Generates: kubectl logs -f -l app=todo-frontend
```

### Filter Logs

**Search for errors**:
```bash
kubectl-ai "show me error logs from the backend"
# Generates: kubectl logs <pod-name> | grep -i error

kubectl-ai "find errors in frontend logs"
# Generates: kubectl logs -l app=todo-frontend | grep -i error
```

**Search for specific patterns**:
```bash
kubectl-ai "show me logs containing 'database' from the backend"
# Generates: kubectl logs <pod-name> | grep database

kubectl-ai "find API errors in backend logs"
# Generates: kubectl logs <pod-name> | grep -i "api.*error"
```

### Previous Container Logs

**View logs from crashed container**:
```bash
kubectl-ai "show me logs from the previous backend container"
# Generates: kubectl logs <pod-name> --previous

kubectl-ai "what happened before the frontend pod crashed"
# Generates: kubectl logs <pod-name> --previous
```

## Best Practices

### 1. Be Specific

**Good**:
```bash
kubectl-ai "scale todo-frontend to 3 replicas"
kubectl-ai "show me logs for the backend pod"
```

**Less Good**:
```bash
kubectl-ai "scale frontend"  # Ambiguous - how many replicas?
kubectl-ai "show logs"  # Which pod?
```

### 2. Use App Names

Always include the app name (todo-frontend, todo-backend) for clarity:

```bash
kubectl-ai "show me all pods for todo-frontend"  # Clear
kubectl-ai "show me frontend pods"  # May be ambiguous
```

### 3. Review Before Executing

Always review the generated command before confirming execution, especially for:
- Scaling operations
- Deletion operations
- Configuration changes

### 4. Use Natural Language

kubectl-ai understands conversational queries:

```bash
kubectl-ai "how many frontend pods are running"
kubectl-ai "is the backend deployment healthy"
kubectl-ai "what's wrong with the frontend pod"
```

### 5. Combine with Manual kubectl

For complex operations, use kubectl-ai to generate the command, then modify it manually:

```bash
# Generate base command
kubectl-ai "show me backend logs"

# Then add additional flags manually
kubectl logs <pod-name> --tail=100 --since=1h
```

## Troubleshooting

### kubectl-ai Not Responding

**Check installation**:
```bash
kubectl-ai --version
which kubectl-ai
```

**Check kubectl context**:
```bash
kubectl config current-context
# Should show: minikube
```

### Incorrect Commands Generated

**Be more specific**:
```bash
# Instead of: "show pods"
# Use: "show me all pods for todo-frontend"
```

**Check for typos**:
```bash
# Correct: "todo-frontend"
# Incorrect: "frontend-todo"
```

### Permission Errors

**Check kubectl permissions**:
```bash
kubectl auth can-i get pods
kubectl auth can-i scale deployments
```

### Command Not Executing

**Check if preview mode is enabled**:
```bash
kubectl-ai config get preview-mode
# If true, commands won't execute automatically
```

**Manually execute generated command**:
```bash
# Copy the generated kubectl command and run it directly
kubectl get pods
```

## Advanced Usage

### Chaining Operations

Use kubectl-ai to generate commands, then chain them:

```bash
# Get pod name, then view logs
POD=$(kubectl-ai "show me the backend pod name" | tail -1)
kubectl logs $POD
```

### Custom Output Formats

Request specific output formats:

```bash
kubectl-ai "show me all pods in JSON format"
# Generates: kubectl get pods -o json

kubectl-ai "show me deployments in YAML"
# Generates: kubectl get deployments -o yaml
```

### Resource Monitoring

Monitor resources over time:

```bash
kubectl-ai "watch pod status"
# Generates: kubectl get pods -w

kubectl-ai "monitor frontend deployment"
# Generates: kubectl get deployment todo-frontend -w
```

## Quick Reference

| Operation | Example Query |
|-----------|---------------|
| List pods | "show me all pods" |
| Describe pod | "describe the backend pod" |
| View logs | "show me backend logs" |
| Scale up | "scale todo-frontend to 3 replicas" |
| Scale down | "reduce backend to 1 replica" |
| Find errors | "show me failing pods" |
| Check status | "is the frontend deployment ready" |
| View events | "show me recent events" |
| Debug probe | "debug the frontend readiness probe" |

## See Also

- [kagent Guide](./KAGENT_GUIDE.md) - Cluster health analysis
- [AI DevOps Best Practices](./AI_DEVOPS.md) - When to use which tool
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues
