# AI DevOps Quick Reference

Quick reference cards for kubectl-ai and kagent operations on the Todo AI Chatbot deployment.

## kubectl-ai Quick Reference

### Inspection Commands

| Task | Command |
|------|---------|
| List all pods | `kubectl-ai "show me all pods"` |
| List pods for app | `kubectl-ai "show me all pods for todo-frontend"` |
| Describe pod | `kubectl-ai "describe the backend pod"` |
| Check pod status | `kubectl-ai "are all pods running"` |
| List deployments | `kubectl-ai "show me all deployments"` |
| Describe deployment | `kubectl-ai "describe the todo-backend deployment"` |
| List services | `kubectl-ai "show me all services"` |
| Check service endpoints | `kubectl-ai "show me endpoints for todo-frontend"` |

### Scaling Commands

| Task | Command |
|------|---------|
| Scale up | `kubectl-ai "scale todo-frontend to 3 replicas"` |
| Scale down | `kubectl-ai "reduce backend to 1 replica"` |
| Check replica counts | `kubectl-ai "show me current replica counts"` |
| Watch scaling | `kubectl-ai "watch the frontend deployment scale"` |

### Log Commands

| Task | Command |
|------|---------|
| View logs | `kubectl-ai "show me logs for the backend pod"` |
| Last N lines | `kubectl-ai "show me the last 50 lines of backend logs"` |
| Follow logs | `kubectl-ai "follow the backend logs"` |
| Search errors | `kubectl-ai "show me error logs from the backend"` |
| Previous container | `kubectl-ai "show me logs from the previous backend container"` |

### Debugging Commands

| Task | Command |
|------|---------|
| Find failing pods | `kubectl-ai "show me all failing pods"` |
| Debug pod failure | `kubectl-ai "why is the backend pod failing"` |
| Debug readiness | `kubectl-ai "debug the frontend readiness probe"` |
| View events | `kubectl-ai "show me recent events"` |
| View warnings | `kubectl-ai "show me warning events"` |

### Tips

- ✅ Always review the generated command before confirming
- ✅ Be specific with app names (todo-frontend, todo-backend)
- ✅ Use natural language - kubectl-ai understands conversational queries
- ❌ Don't use for cluster-wide analysis - use kagent instead

---

## kagent Quick Reference

### Health Check Commands

| Task | Command |
|------|---------|
| Basic health check | `kagent health` |
| Detailed health | `kagent health --detailed` |
| With alerts | `kagent health --alert-threshold cpu=80,memory=80` |
| Specific namespace | `kagent health --namespace default` |
| Specific deployment | `kagent health --deployment todo-frontend` |

### Resource Analysis Commands

| Task | Command |
|------|---------|
| CPU analysis | `kagent analyze cpu` |
| Memory analysis | `kagent analyze memory` |
| Disk analysis | `kagent analyze disk` |
| Network analysis | `kagent analyze network` |
| All resources | `kagent analyze resources` |
| Per-pod analysis | `kagent analyze cpu --by-pod` |
| Trend analysis | `kagent analyze trends --duration 24h` |

### Bottleneck Detection Commands

| Task | Command |
|------|---------|
| Detect all bottlenecks | `kagent detect bottlenecks` |
| CPU bottlenecks | `kagent detect bottlenecks --type cpu` |
| Memory bottlenecks | `kagent detect bottlenecks --type memory` |
| Performance analysis | `kagent analyze performance` |
| Restart analysis | `kagent analyze restarts` |

### Optimization Commands

| Task | Command |
|------|---------|
| Get recommendations | `kagent recommend` |
| Cost optimization | `kagent recommend --focus cost` |
| Performance optimization | `kagent recommend --focus performance` |
| Reliability optimization | `kagent recommend --focus reliability` |
| Generate commands | `kagent recommend --generate-commands` |

### Tips

- ✅ Run health checks regularly (daily)
- ✅ Save reports for historical comparison
- ✅ Review recommendations before implementing
- ✅ Wait 30-60 seconds for metrics to be collected
- ❌ Don't use for single operations - use kubectl-ai instead

---

## Decision Matrix

### Which Tool Should I Use?

| Scenario | Tool | Why |
|----------|------|-----|
| View specific pods | kubectl-ai | Fast, specific query |
| Scale deployment | kubectl-ai | Interactive, immediate |
| View logs | kubectl-ai | Natural language filtering |
| Debug failing pod | kubectl-ai | Combines logs + events |
| Cluster health | kagent | Comprehensive overview |
| Resource usage | kagent | Deep analysis + trends |
| Find bottlenecks | kagent | AI-powered detection |
| Get optimization tips | kagent | Actionable recommendations |
| Complex debugging | Both | kubectl-ai for details, kagent for context |
| Before scaling | Both | kagent to analyze, kubectl-ai to execute |

---

## Common Workflows

### Morning Health Check (2 minutes)

```bash
# 1. Check cluster health
kagent health

# 2. If issues, investigate
kubectl-ai "show me all failing pods"

# 3. Check resource usage
kagent analyze resources
```

### Scale for Traffic (5 minutes)

```bash
# 1. Check current resources
kagent analyze resources

# 2. Scale up
kubectl-ai "scale todo-frontend to 3 replicas"

# 3. Verify
kubectl-ai "show me all pods for todo-frontend"

# 4. Monitor impact
kagent analyze resources
```

### Debug Pod Failure (10 minutes)

```bash
# 1. Identify failing pods
kubectl-ai "show me all failing pods"

# 2. Get details
kubectl-ai "why is the backend pod failing"

# 3. Check resources
kagent analyze resources

# 4. View logs
kubectl-ai "show me logs from the previous backend container"

# 5. Get recommendations
kagent recommend --focus reliability
```

### Weekly Optimization (30 minutes)

```bash
# 1. Health report
kagent health --detailed > weekly-health.txt

# 2. Trend analysis
kagent analyze trends --duration 7d > weekly-trends.txt

# 3. Bottleneck detection
kagent detect bottlenecks > weekly-bottlenecks.txt

# 4. Recommendations
kagent recommend > weekly-recommendations.txt

# 5. Review and implement
cat weekly-*.txt
# Use kubectl-ai to implement recommendations
```

---

## Safety Checklist

Before executing any operation:

- [ ] Reviewed the generated command
- [ ] Verified resource names are correct
- [ ] Checked replica counts are reasonable
- [ ] Confirmed no destructive operations (delete, force)
- [ ] Understood the impact of the change
- [ ] Have a rollback plan if needed

---

## Emergency Commands

### Pod is CrashLooping

```bash
kubectl-ai "show me pods in CrashLoopBackOff"
kubectl-ai "why is the backend pod failing"
kubectl-ai "show me logs from the previous backend container"
kagent analyze resources
```

### High CPU Usage

```bash
kubectl-ai "show me pods using high CPU"
kagent analyze cpu --by-pod
kagent detect bottlenecks --type cpu
kagent recommend --focus performance
```

### High Memory Usage

```bash
kubectl-ai "show me pods using high memory"
kagent analyze memory --by-pod
kagent detect bottlenecks --type memory
kagent recommend --focus reliability
```

### Service Not Responding

```bash
kubectl-ai "show me all services"
kubectl-ai "show me endpoints for todo-frontend"
kubectl-ai "show me all pods for todo-frontend"
kagent health --deployment todo-frontend
```

---

## Output Formats

### kubectl-ai Output

```bash
# Default: Human-readable
kubectl-ai "show me all pods"

# JSON format
kubectl-ai "show me all pods in JSON format"

# YAML format
kubectl-ai "show me deployments in YAML"
```

### kagent Output

```bash
# Default: Human-readable
kagent health

# JSON format
kagent health --output json

# YAML format
kagent analyze resources --output yaml

# CSV format (for spreadsheets)
kagent analyze resources --output csv
```

---

## Keyboard Shortcuts

### kubectl-ai Interactive Mode

- `y` or `Enter` - Execute command
- `n` or `Ctrl+C` - Cancel command
- `e` - Edit command before execution

### kagent Report Navigation

- `q` - Quit report view
- `Space` - Next page
- `b` - Previous page
- `/` - Search in report

---

## Environment Variables

### kubectl-ai Configuration

```bash
# Set default context
export KUBECTL_AI_CONTEXT=minikube

# Set preview mode (always show preview)
export KUBECTL_AI_PREVIEW=true

# Set timeout (seconds)
export KUBECTL_AI_TIMEOUT=30
```

### kagent Configuration

```bash
# Set metric collection interval
export KAGENT_METRIC_INTERVAL=30s

# Set alert thresholds
export KAGENT_CPU_THRESHOLD=80
export KAGENT_MEMORY_THRESHOLD=80

# Set report format
export KAGENT_OUTPUT_FORMAT=text
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| kubectl-ai not found | Check PATH: `which kubectl-ai` |
| kagent not found | Check PATH: `which kagent` |
| No metrics available | Enable metrics-server: `minikube addons enable metrics-server` |
| Incorrect context | Switch context: `kubectl config use-context minikube` |
| Permission denied | Check kubectl permissions: `kubectl auth can-i get pods` |
| Command timeout | Increase timeout: `kubectl-ai --timeout 60 "..."` |
| Stale metrics | Wait 60 seconds, then retry |

---

## Resource Limits Reference

### Minikube Default Resources

- **CPU**: 2 cores
- **Memory**: 4GB
- **Disk**: 50GB

### Recommended Pod Resources

**Frontend (todo-frontend)**:
- CPU Request: 50m
- CPU Limit: 200m
- Memory Request: 128Mi
- Memory Limit: 512Mi

**Backend (todo-backend)**:
- CPU Request: 100m
- CPU Limit: 500m
- Memory Request: 256Mi
- Memory Limit: 1Gi

### Healthy Resource Usage

- **CPU**: 50-70% of limit (allows burst capacity)
- **Memory**: 60-80% of limit (prevents OOMKilled)
- **Disk**: <80% (prevents full disk issues)

---

## See Also

- [kubectl-ai Examples](./KUBECTL_AI_EXAMPLES.md) - Detailed usage examples
- [kagent Guide](./KAGENT_GUIDE.md) - Comprehensive guide
- [AI DevOps Best Practices](./AI_DEVOPS.md) - Best practices and patterns
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions
