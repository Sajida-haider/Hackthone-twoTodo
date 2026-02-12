# AI DevOps Best Practices

This guide provides best practices for using AI-assisted tools (kubectl-ai and kagent) to manage the Todo AI Chatbot deployment on Kubernetes.

## Table of Contents

1. [Tool Selection Guide](#tool-selection-guide)
2. [When to Use kubectl-ai](#when-to-use-kubectl-ai)
3. [When to Use kagent](#when-to-use-kagent)
4. [Workflow Recommendations](#workflow-recommendations)
5. [Safety Guidelines](#safety-guidelines)
6. [Integration Patterns](#integration-patterns)
7. [Decision Trees](#decision-trees)
8. [Common Scenarios](#common-scenarios)
9. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
10. [Performance Considerations](#performance-considerations)

## Tool Selection Guide

### kubectl-ai

**Purpose**: Natural language interface for Kubernetes operations

**Best For**:
- Quick inspections and queries
- Scaling operations
- Log viewing and filtering
- Debugging specific pods
- Ad-hoc operational tasks
- Learning Kubernetes commands

**Strengths**:
- Fast command generation
- Interactive and conversational
- Shows preview before execution
- Great for one-off operations
- Reduces kubectl syntax errors

**Limitations**:
- No cluster-wide analysis
- No optimization recommendations
- Limited to single operations
- Requires confirmation for each command

### kagent

**Purpose**: Cluster health analysis and optimization

**Best For**:
- Cluster health monitoring
- Resource usage analysis
- Bottleneck detection
- Optimization recommendations
- Trend analysis over time
- Capacity planning
- Performance tuning

**Strengths**:
- Comprehensive health reports
- Actionable recommendations
- Historical trend analysis
- Proactive problem detection
- Multi-resource correlation

**Limitations**:
- Not for individual operations
- Requires metrics-server
- Analysis takes time (30-60s)
- No command execution

## When to Use kubectl-ai

### Inspection Tasks

Use kubectl-ai when you need to:

```bash
# View specific resources
kubectl-ai "show me all pods for todo-frontend"
kubectl-ai "describe the backend deployment"
kubectl-ai "show me all services"

# Check status
kubectl-ai "are all pods running"
kubectl-ai "is the frontend deployment ready"
kubectl-ai "show me pods that are not ready"
```

**Why kubectl-ai**: Fast, conversational, generates exact kubectl commands.

### Scaling Operations

Use kubectl-ai when you need to:

```bash
# Scale deployments
kubectl-ai "scale todo-frontend to 3 replicas"
kubectl-ai "reduce backend to 1 replica"
kubectl-ai "show me current replica counts"
```

**Why kubectl-ai**: Interactive confirmation, clear preview, immediate execution.

### Log Analysis

Use kubectl-ai when you need to:

```bash
# View logs
kubectl-ai "show me logs for the backend pod"
kubectl-ai "show me the last 50 lines of frontend logs"
kubectl-ai "follow the backend logs"

# Search logs
kubectl-ai "show me error logs from the backend"
kubectl-ai "find API errors in backend logs"
```

**Why kubectl-ai**: Natural language log filtering, easy to specify what you want.

### Debugging

Use kubectl-ai when you need to:

```bash
# Debug specific issues
kubectl-ai "why is the backend pod failing"
kubectl-ai "debug the frontend readiness probe"
kubectl-ai "show me all failing pods and their errors"
```

**Why kubectl-ai**: Combines multiple kubectl commands, provides context-aware debugging.

## When to Use kagent

### Health Monitoring

Use kagent when you need to:

```bash
# Overall cluster health
kagent health
kagent health --detailed
kagent health --alert-threshold cpu=80,memory=80

# Component health
kagent health --namespace default
kagent health --deployment todo-frontend
```

**Why kagent**: Comprehensive view, correlates multiple metrics, identifies patterns.

### Resource Analysis

Use kagent when you need to:

```bash
# Analyze resource usage
kagent analyze cpu
kagent analyze memory
kagent analyze disk
kagent analyze network

# Per-pod analysis
kagent analyze cpu --by-pod
kagent analyze memory --by-pod
```

**Why kagent**: Deep analysis, historical trends, identifies inefficiencies.

### Optimization

Use kagent when you need to:

```bash
# Get recommendations
kagent recommend
kagent recommend --focus cost
kagent recommend --focus performance
kagent recommend --focus reliability

# Detect bottlenecks
kagent detect bottlenecks
kagent detect bottlenecks --type cpu
kagent detect bottlenecks --type memory
```

**Why kagent**: AI-powered recommendations, considers cluster-wide context, prioritizes actions.

### Capacity Planning

Use kagent when you need to:

```bash
# Trend analysis
kagent analyze trends --duration 24h
kagent analyze trends --duration 7d

# Performance analysis
kagent analyze performance
kagent analyze restarts
```

**Why kagent**: Historical data, predictive insights, identifies growth patterns.

## Workflow Recommendations

### Daily Operations Workflow

**Morning Health Check**:
```bash
# 1. Quick cluster overview (kagent)
kagent health

# 2. Check for any issues (kubectl-ai)
kubectl-ai "show me all failing pods"

# 3. Review recent events (kubectl-ai)
kubectl-ai "show me recent warning events"
```

**Why This Order**: kagent gives big picture, kubectl-ai drills into specifics.

### Scaling Workflow

**Before Scaling**:
```bash
# 1. Check current resource usage (kagent)
kagent analyze resources

# 2. Verify current replica counts (kubectl-ai)
kubectl-ai "show me current replica counts"

# 3. Scale deployment (kubectl-ai)
kubectl-ai "scale todo-frontend to 3 replicas"

# 4. Verify scaling completed (kubectl-ai)
kubectl-ai "watch the frontend deployment scale"

# 5. Check resource impact (kagent)
kagent analyze resources
```

**Why This Order**: Understand before acting, verify after acting, measure impact.

### Debugging Workflow

**When Pod Fails**:
```bash
# 1. Identify failing pods (kubectl-ai)
kubectl-ai "show me all failing pods"

# 2. Get pod details (kubectl-ai)
kubectl-ai "why is the backend pod failing"

# 3. Check resource constraints (kagent)
kagent analyze resources --pod <pod-name>

# 4. View logs (kubectl-ai)
kubectl-ai "show me logs from the previous backend container"

# 5. Check cluster health (kagent)
kagent health --detailed
```

**Why This Order**: Narrow from symptom to root cause, consider resource constraints.

### Optimization Workflow

**Weekly Optimization**:
```bash
# 1. Run health analysis (kagent)
kagent health --detailed

# 2. Analyze resource usage (kagent)
kagent analyze resources

# 3. Detect bottlenecks (kagent)
kagent detect bottlenecks

# 4. Get recommendations (kagent)
kagent recommend

# 5. Implement high-priority recommendations (kubectl-ai + manual)
# Review each recommendation, use kubectl-ai for simple changes

# 6. Verify improvements (kagent)
kagent analyze resources
```

**Why This Order**: Systematic analysis, prioritized actions, measure results.

## Safety Guidelines

### 1. Always Preview Before Execution

**kubectl-ai automatically shows previews**:
```bash
$ kubectl-ai "scale todo-frontend to 10 replicas"

Generated command:
  kubectl scale deployment todo-frontend --replicas=10

Execute this command? [y/N]:
```

**Always review**:
- Resource names are correct
- Replica counts are reasonable
- No destructive operations (delete, force)

### 2. Use Read-Only Operations First

**Safe exploration**:
```bash
# Good: Read-only operations
kubectl-ai "show me all pods"
kagent health
kagent analyze resources

# Risky: Write operations
kubectl-ai "delete all pods"  # ❌ Dangerous
kubectl-ai "scale to 100 replicas"  # ❌ May exhaust resources
```

### 3. Validate Recommendations

**kagent provides recommendations, but you decide**:
```bash
# Get recommendations
kagent recommend

# Review each recommendation:
# - Does it align with your goals?
# - Are there any side effects?
# - Is this the right time?

# Test in non-production first
# Implement incrementally
# Monitor after each change
```

### 4. Set Resource Limits

**Prevent resource exhaustion**:
```bash
# Before scaling, check available resources
kagent analyze resources

# Ensure you have capacity
# Don't scale beyond cluster limits
# Monitor resource usage after scaling
```

### 5. Keep Audit Logs

**Track all AI-assisted operations**:
```bash
# Log kubectl-ai operations
kubectl-ai "scale todo-frontend to 3 replicas" | tee -a ai-ops.log

# Save kagent reports
kagent health > reports/health-$(date +%Y%m%d).txt
kagent recommend > reports/recommendations-$(date +%Y%m%d).txt
```

### 6. Understand Generated Commands

**Don't blindly execute**:
```bash
# Good: Understand what the command does
kubectl-ai "show me all pods"
# Generated: kubectl get pods
# ✅ Safe, read-only

# Bad: Execute without understanding
kubectl-ai "fix the broken deployment"
# Generated: kubectl delete deployment todo-frontend && kubectl apply -f ...
# ❌ Destructive, may cause downtime
```

## Integration Patterns

### Pattern 1: Inspect → Analyze → Act

**Use Case**: Investigating performance issues

```bash
# 1. Inspect with kubectl-ai
kubectl-ai "show me all pods and their status"

# 2. Analyze with kagent
kagent analyze resources
kagent detect bottlenecks

# 3. Act based on findings
# If kagent recommends scaling:
kubectl-ai "scale todo-frontend to 3 replicas"

# 4. Verify with kagent
kagent analyze resources
```

**Why**: kubectl-ai for quick inspection, kagent for deep analysis, kubectl-ai for action.

### Pattern 2: Monitor → Alert → Debug

**Use Case**: Proactive monitoring

```bash
# 1. Monitor with kagent (scheduled)
kagent health --alert-threshold cpu=80,memory=80

# 2. If alert triggered, inspect with kubectl-ai
kubectl-ai "show me pods using high CPU"
kubectl-ai "show me pods using high memory"

# 3. Debug with kubectl-ai
kubectl-ai "why is the backend pod using high CPU"
kubectl-ai "show me backend logs for errors"

# 4. Analyze root cause with kagent
kagent analyze performance
kagent detect bottlenecks
```

**Why**: kagent for continuous monitoring, kubectl-ai for interactive debugging.

### Pattern 3: Plan → Validate → Execute

**Use Case**: Implementing kagent recommendations

```bash
# 1. Get recommendations from kagent
kagent recommend > recommendations.txt

# 2. Review recommendations
cat recommendations.txt

# 3. Validate current state with kubectl-ai
kubectl-ai "show me current resource usage for todo-frontend"

# 4. Execute recommendation with kubectl-ai
kubectl-ai "scale todo-frontend to 3 replicas"

# 5. Verify with kagent
kagent analyze resources
kagent health
```

**Why**: kagent provides strategy, kubectl-ai executes tactics, kagent validates results.

### Pattern 4: Baseline → Change → Compare

**Use Case**: Measuring impact of changes

```bash
# 1. Establish baseline with kagent
kagent analyze resources > baseline.txt

# 2. Make change with kubectl-ai
kubectl-ai "scale todo-frontend to 3 replicas"

# 3. Wait for stabilization
sleep 60

# 4. Measure new state with kagent
kagent analyze resources > after-change.txt

# 5. Compare
diff baseline.txt after-change.txt
```

**Why**: kagent for before/after comparison, kubectl-ai for making changes.

## Decision Trees

### Decision Tree 1: Which Tool to Use?

```
Need to perform an operation?
│
├─ Single, specific operation? (view, scale, logs)
│  └─ Use kubectl-ai
│     Examples: "show me pods", "scale to 3", "view logs"
│
├─ Cluster-wide analysis? (health, resources, trends)
│  └─ Use kagent
│     Examples: health check, resource analysis, bottleneck detection
│
├─ Need recommendations? (optimization, capacity planning)
│  └─ Use kagent
│     Examples: recommend, detect bottlenecks, analyze trends
│
└─ Complex workflow? (debug, optimize, scale)
   └─ Use both (integration pattern)
      Examples: inspect → analyze → act
```

### Decision Tree 2: Debugging Approach

```
Pod is failing?
│
├─ Need to see what's wrong quickly?
│  └─ kubectl-ai "why is the pod failing"
│     └─ Shows logs + events + status
│
├─ Need to understand resource constraints?
│  └─ kagent analyze resources
│     └─ Shows CPU, memory, disk usage
│
├─ Need to find root cause?
│  └─ Use both:
│     1. kubectl-ai "show me failing pods"
│     2. kagent detect bottlenecks
│     3. kubectl-ai "show me logs for <pod>"
│     4. kagent analyze performance
│
└─ Need to prevent future failures?
   └─ kagent recommend
      └─ Get optimization recommendations
```

### Decision Tree 3: Scaling Decision

```
Need to scale?
│
├─ Know exact replica count?
│  └─ kubectl-ai "scale to N replicas"
│
├─ Don't know how much to scale?
│  └─ Use kagent first:
│     1. kagent analyze resources
│     2. kagent recommend
│     3. Review recommendations
│     4. kubectl-ai "scale to N replicas"
│
├─ Need automatic scaling?
│  └─ Use kagent to determine thresholds:
│     1. kagent analyze trends --duration 7d
│     2. Identify peak usage patterns
│     3. kubectl-ai "create HPA with min/max replicas"
│
└─ Scaling for load test?
   └─ Use both:
      1. kagent analyze resources (baseline)
      2. kubectl-ai "scale to N replicas"
      3. Run load test
      4. kagent analyze resources (compare)
```

## Common Scenarios

### Scenario 1: Morning Health Check

**Goal**: Verify cluster is healthy before starting work

```bash
# 1. Quick health check (30 seconds)
kagent health

# 2. If issues found, investigate
kubectl-ai "show me all failing pods"
kubectl-ai "show me recent warning events"

# 3. Check resource usage
kagent analyze resources

# 4. If high usage, get recommendations
kagent recommend
```

**Time**: 2-3 minutes
**Tools**: kagent (overview) → kubectl-ai (details)

### Scenario 2: Responding to High CPU Alert

**Goal**: Identify and resolve high CPU usage

```bash
# 1. Identify high CPU pods
kubectl-ai "show me pods using high CPU"

# 2. Analyze CPU usage patterns
kagent analyze cpu --by-pod

# 3. Check if it's a bottleneck
kagent detect bottlenecks --type cpu

# 4. Get recommendations
kagent recommend --focus performance

# 5. If recommendation is to scale, execute
kubectl-ai "scale todo-frontend to 3 replicas"

# 6. Verify improvement
kagent analyze cpu
```

**Time**: 5-10 minutes
**Tools**: kubectl-ai (identify) → kagent (analyze) → kubectl-ai (act) → kagent (verify)

### Scenario 3: Preparing for Traffic Spike

**Goal**: Scale proactively before expected load

```bash
# 1. Check current resource usage
kagent analyze resources

# 2. Check historical trends
kagent analyze trends --duration 7d

# 3. Verify current replica counts
kubectl-ai "show me current replica counts"

# 4. Scale frontend for traffic
kubectl-ai "scale todo-frontend to 5 replicas"

# 5. Verify all replicas are ready
kubectl-ai "show me all pods for todo-frontend"

# 6. Monitor resource usage
kagent analyze resources

# 7. After traffic spike, scale down
kubectl-ai "scale todo-frontend to 2 replicas"
```

**Time**: 5-10 minutes
**Tools**: kagent (plan) → kubectl-ai (execute) → kagent (monitor)

### Scenario 4: Weekly Optimization Review

**Goal**: Identify and implement optimizations

```bash
# 1. Generate comprehensive health report
kagent health --detailed > weekly-health.txt

# 2. Analyze resource usage trends
kagent analyze trends --duration 7d > weekly-trends.txt

# 3. Detect bottlenecks
kagent detect bottlenecks > weekly-bottlenecks.txt

# 4. Get optimization recommendations
kagent recommend > weekly-recommendations.txt

# 5. Review all reports
cat weekly-*.txt

# 6. Implement high-priority recommendations
# Use kubectl-ai for each recommendation

# 7. Verify improvements
kagent analyze resources
```

**Time**: 30-60 minutes
**Tools**: kagent (analysis) → manual review → kubectl-ai (implementation) → kagent (verification)

### Scenario 5: Debugging CrashLoopBackOff

**Goal**: Identify why pod keeps crashing

```bash
# 1. Identify crashing pods
kubectl-ai "show me pods in CrashLoopBackOff"

# 2. Get detailed pod information
kubectl-ai "why is the backend pod failing"

# 3. Check previous container logs
kubectl-ai "show me logs from the previous backend container"

# 4. Check resource constraints
kagent analyze resources --pod <pod-name>

# 5. Check for memory issues
kagent analyze memory --detect-leaks

# 6. Get recommendations
kagent recommend --focus reliability

# 7. Implement fix based on findings
# Example: If memory limit too low
kubectl-ai "increase memory limit for backend"
```

**Time**: 10-15 minutes
**Tools**: kubectl-ai (identify + logs) → kagent (resource analysis) → kubectl-ai (fix)

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Using kubectl-ai for Cluster-Wide Analysis

**Wrong**:
```bash
kubectl-ai "show me all pods"
kubectl-ai "show me CPU usage for all pods"
kubectl-ai "show me memory usage for all pods"
# Tedious, incomplete, no recommendations
```

**Right**:
```bash
kagent health
kagent analyze resources
# Comprehensive, correlated, with recommendations
```

### ❌ Anti-Pattern 2: Using kagent for Single Operations

**Wrong**:
```bash
kagent scale todo-frontend to 3 replicas  # kagent doesn't execute operations
```

**Right**:
```bash
kubectl-ai "scale todo-frontend to 3 replicas"
```

### ❌ Anti-Pattern 3: Ignoring Previews

**Wrong**:
```bash
# Blindly accepting all kubectl-ai commands without review
kubectl-ai "fix the deployment"  # What will it do?
# Press 'y' without reading
```

**Right**:
```bash
kubectl-ai "fix the deployment"
# Read the generated command carefully
# Understand what it will do
# Only then press 'y'
```

### ❌ Anti-Pattern 4: Not Validating Recommendations

**Wrong**:
```bash
kagent recommend
# Implement all recommendations immediately without review
```

**Right**:
```bash
kagent recommend
# Review each recommendation
# Understand the impact
# Test in non-production first
# Implement incrementally
```

### ❌ Anti-Pattern 5: Using AI Tools for Everything

**Wrong**:
```bash
# Using kubectl-ai for simple commands you already know
kubectl-ai "get pods"  # Just use: kubectl get pods
```

**Right**:
```bash
# Use kubectl-ai for complex or unfamiliar operations
kubectl-ai "show me pods that are not ready and their events"
# Use regular kubectl for simple operations
kubectl get pods
```

### ❌ Anti-Pattern 6: Not Measuring Impact

**Wrong**:
```bash
kubectl-ai "scale todo-frontend to 5 replicas"
# Don't check if it helped
```

**Right**:
```bash
# Before
kagent analyze resources > before.txt

# Change
kubectl-ai "scale todo-frontend to 5 replicas"

# After
sleep 60
kagent analyze resources > after.txt

# Compare
diff before.txt after.txt
```

## Performance Considerations

### kubectl-ai Performance

**Fast Operations** (<5 seconds):
- Viewing pods, deployments, services
- Describing resources
- Checking status

**Medium Operations** (5-15 seconds):
- Scaling deployments
- Viewing logs (depends on log size)
- Filtering events

**Slow Operations** (>15 seconds):
- Following logs in real-time (continuous)
- Watching resource changes (continuous)

**Optimization Tips**:
- Use specific queries instead of broad ones
- Limit log output with `--tail=N`
- Use `--since=1h` for recent logs only

### kagent Performance

**Fast Operations** (<30 seconds):
- Basic health check
- Single resource analysis (CPU or memory)

**Medium Operations** (30-60 seconds):
- Detailed health check
- Multi-resource analysis
- Bottleneck detection

**Slow Operations** (>60 seconds):
- Trend analysis over long periods (7d+)
- Memory leak detection
- Comprehensive optimization analysis

**Optimization Tips**:
- Run detailed analysis during off-peak hours
- Use shorter duration for trend analysis when possible
- Cache reports for reference instead of re-running

### Combined Workflow Performance

**Efficient Workflow**:
```bash
# Run kagent analysis once, save results
kagent health > health.txt
kagent analyze resources > resources.txt

# Use kubectl-ai for multiple quick operations
kubectl-ai "show me frontend pods"
kubectl-ai "show me backend pods"
kubectl-ai "show me services"

# Review kagent reports
cat health.txt resources.txt
```

**Inefficient Workflow**:
```bash
# Running kagent multiple times unnecessarily
kagent health
kagent health --detailed
kagent health --namespace default
# Each run takes 30-60 seconds
```

## Quick Reference

### When to Use What

| Task | Tool | Command Example |
|------|------|-----------------|
| View pods | kubectl-ai | `kubectl-ai "show me all pods"` |
| Scale deployment | kubectl-ai | `kubectl-ai "scale to 3 replicas"` |
| View logs | kubectl-ai | `kubectl-ai "show me backend logs"` |
| Debug pod | kubectl-ai | `kubectl-ai "why is pod failing"` |
| Cluster health | kagent | `kagent health` |
| Resource analysis | kagent | `kagent analyze resources` |
| Bottleneck detection | kagent | `kagent detect bottlenecks` |
| Optimization | kagent | `kagent recommend` |
| Trend analysis | kagent | `kagent analyze trends --duration 24h` |

### Integration Patterns

| Pattern | Tools | Use Case |
|---------|-------|----------|
| Inspect → Analyze → Act | kubectl-ai → kagent → kubectl-ai | Performance issues |
| Monitor → Alert → Debug | kagent → kubectl-ai | Proactive monitoring |
| Plan → Validate → Execute | kagent → kubectl-ai → kagent | Implementing recommendations |
| Baseline → Change → Compare | kagent → kubectl-ai → kagent | Measuring impact |

## See Also

- [kubectl-ai Examples](./KUBECTL_AI_EXAMPLES.md) - Detailed kubectl-ai usage examples
- [kagent Guide](./KAGENT_GUIDE.md) - Comprehensive kagent usage guide
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions
