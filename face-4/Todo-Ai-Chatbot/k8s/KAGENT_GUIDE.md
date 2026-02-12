# kagent Usage Guide

This guide provides comprehensive instructions for using kagent to analyze cluster health and optimize the Todo AI Chatbot deployment on Minikube.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Health Check Operations](#health-check-operations)
3. [Resource Analysis](#resource-analysis)
4. [Bottleneck Detection](#bottleneck-detection)
5. [Optimization Recommendations](#optimization-recommendations)
6. [Report Interpretation](#report-interpretation)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- kagent installed and configured
- Minikube running with Todo app deployed
- metrics-server enabled: `minikube addons enable metrics-server`
- kubectl configured to use Minikube context

### Basic Usage

```bash
# General syntax
kagent <command> [options]

# Get help
kagent --help

# Show version
kagent --version

# Check configuration
kagent config show
```

### Quick Start

```bash
# Run basic health check
kagent health

# Analyze resource usage
kagent analyze resources

# Get optimization recommendations
kagent recommend
```

## Health Check Operations

### Overall Cluster Health

**Basic health check**:
```bash
kagent health
```

**Output**:
```
Cluster Health Report
=====================
Generated: 2026-02-10 23:00:00
Cluster: minikube
Status: Healthy

Node Health:
  minikube: Healthy
  CPU: 45% (2 cores)
  Memory: 2.1GB / 4GB (52%)
  Disk: 15GB / 50GB (30%)

Pod Health:
  Total Pods: 4
  Running: 4
  Pending: 0
  Failed: 0
  Unknown: 0

Service Health:
  Total Services: 3
  Active: 3
  Inactive: 0
```

**Detailed health check**:
```bash
kagent health --detailed
```

**Output includes**:
- Node resource usage
- Pod status breakdown
- Service availability
- Persistent volume status
- Network connectivity
- DNS resolution

**Health check with threshold alerts**:
```bash
kagent health --alert-threshold cpu=80,memory=80
```

Alerts when CPU or memory exceeds 80%.

### Component-Specific Health

**Check specific namespace**:
```bash
kagent health --namespace default
```

**Check specific deployment**:
```bash
kagent health --deployment todo-frontend
kagent health --deployment todo-backend
```

**Check specific pod**:
```bash
kagent health --pod <pod-name>
```

## Resource Analysis

### CPU Analysis

**Cluster-wide CPU usage**:
```bash
kagent analyze cpu
```

**Output**:
```
CPU Analysis Report
===================
Cluster Total: 2 cores
Used: 0.9 cores (45%)
Available: 1.1 cores (55%)

Top CPU Consumers:
1. todo-backend-xxx: 0.5 cores (25%)
2. todo-frontend-xxx: 0.3 cores (15%)
3. metrics-server-xxx: 0.1 cores (5%)

Recommendations:
- todo-backend is using 50% of requested CPU (0.5/1.0)
- Consider reducing CPU request if consistently underutilized
```

**Per-pod CPU analysis**:
```bash
kagent analyze cpu --by-pod
```

**CPU trends over time**:
```bash
kagent analyze cpu --duration 1h
```

### Memory Analysis

**Cluster-wide memory usage**:
```bash
kagent analyze memory
```

**Output**:
```
Memory Analysis Report
======================
Cluster Total: 4GB
Used: 2.1GB (52%)
Available: 1.9GB (48%)

Top Memory Consumers:
1. todo-backend-xxx: 800MB (20%)
2. todo-frontend-xxx: 400MB (10%)
3. metrics-server-xxx: 200MB (5%)

Recommendations:
- todo-backend is using 80% of memory limit (800MB/1GB)
- Consider increasing memory limit to prevent OOMKilled
```

**Per-pod memory analysis**:
```bash
kagent analyze memory --by-pod
```

**Memory leak detection**:
```bash
kagent analyze memory --detect-leaks --duration 1h
```

### Disk Analysis

**Cluster-wide disk usage**:
```bash
kagent analyze disk
```

**Output**:
```
Disk Analysis Report
====================
Node: minikube
Total: 50GB
Used: 15GB (30%)
Available: 35GB (70%)

Disk Usage by Component:
- Container images: 8GB
- Container logs: 3GB
- Persistent volumes: 2GB
- System: 2GB

Recommendations:
- Disk usage is healthy
- Consider log rotation if logs exceed 5GB
```

**Persistent volume analysis**:
```bash
kagent analyze disk --pv
```

### Network Analysis

**Network traffic analysis**:
```bash
kagent analyze network
```

**Output**:
```
Network Analysis Report
=======================
Ingress Traffic: 10 MB/s
Egress Traffic: 5 MB/s

Service-to-Service Traffic:
- todo-frontend → todo-backend: 3 MB/s
- todo-backend → external (Neon DB): 2 MB/s

Recommendations:
- Network traffic is within normal range
- No bottlenecks detected
```

**Network latency analysis**:
```bash
kagent analyze network --latency
```

## Bottleneck Detection

### Automatic Bottleneck Detection

**Detect all bottlenecks**:
```bash
kagent detect bottlenecks
```

**Output**:
```
Bottleneck Detection Report
============================
Detected: 2 bottlenecks

1. CPU Bottleneck - todo-backend
   Severity: Medium
   Current: 0.9 cores (90% of limit)
   Recommendation: Increase CPU limit from 1.0 to 1.5 cores
   Impact: May cause request throttling during peak load

2. Memory Pressure - todo-backend
   Severity: High
   Current: 950MB (95% of limit)
   Recommendation: Increase memory limit from 1GB to 2GB
   Impact: Risk of OOMKilled, pod restarts
```

**Detect specific bottleneck types**:
```bash
kagent detect bottlenecks --type cpu
kagent detect bottlenecks --type memory
kagent detect bottlenecks --type disk
kagent detect bottlenecks --type network
```

### Performance Analysis

**Identify slow pods**:
```bash
kagent analyze performance
```

**Output**:
```
Performance Analysis Report
===========================
Slow Pods Detected: 1

todo-backend-xxx:
- Startup time: 45s (threshold: 30s)
- Response time: 250ms (threshold: 200ms)
- Restart count: 3 (last 24h)

Root Cause Analysis:
- High memory usage causing GC pressure
- Database connection pool exhausted
- Insufficient CPU during startup

Recommendations:
1. Increase memory limit to reduce GC frequency
2. Increase database connection pool size
3. Add CPU burst allowance for startup
```

**Analyze pod restart patterns**:
```bash
kagent analyze restarts
```

## Optimization Recommendations

### Get Recommendations

**General recommendations**:
```bash
kagent recommend
```

**Output**:
```
Optimization Recommendations
=============================
Generated: 2026-02-10 23:00:00
Priority: High to Low

1. [HIGH] Increase todo-backend memory limit
   Current: 1GB
   Recommended: 2GB
   Reason: Pod using 95% of memory limit, risk of OOMKilled
   Impact: Prevents pod crashes, improves stability
   Implementation:
     helm upgrade todo-backend ./helm/todo-backend \
       --set resources.limits.memory=2Gi

2. [MEDIUM] Reduce todo-frontend CPU request
   Current: 100m
   Recommended: 50m
   Reason: Pod consistently using only 30m CPU
   Impact: Frees up 50m CPU for other workloads
   Implementation:
     helm upgrade todo-frontend ./helm/todo-frontend \
       --set resources.requests.cpu=50m

3. [MEDIUM] Enable horizontal pod autoscaling for frontend
   Current: Fixed 1 replica
   Recommended: HPA with 1-3 replicas
   Reason: Traffic patterns show periodic spikes
   Impact: Automatic scaling during high load
   Implementation:
     kubectl autoscale deployment todo-frontend \
       --min=1 --max=3 --cpu-percent=70

4. [LOW] Implement log rotation
   Current: Logs consuming 3GB
   Recommended: Rotate logs daily, keep 7 days
   Reason: Prevent disk space issues
   Impact: Reduces disk usage by ~2GB
   Implementation:
     Configure log rotation in container runtime

5. [LOW] Add resource requests for metrics-server
   Current: No requests defined
   Recommended: CPU: 50m, Memory: 100Mi
   Reason: Ensures metrics-server gets guaranteed resources
   Impact: More reliable metrics collection
```

**Cost optimization recommendations**:
```bash
kagent recommend --focus cost
```

**Performance optimization recommendations**:
```bash
kagent recommend --focus performance
```

**Reliability optimization recommendations**:
```bash
kagent recommend --focus reliability
```

### Apply Recommendations

**Preview recommendation impact**:
```bash
kagent recommend --preview <recommendation-id>
```

**Generate implementation commands**:
```bash
kagent recommend --generate-commands
```

**Output**:
```bash
# Recommendation 1: Increase todo-backend memory
helm upgrade todo-backend ./helm/todo-backend \
  --set resources.limits.memory=2Gi \
  --reuse-values

# Recommendation 2: Reduce todo-frontend CPU
helm upgrade todo-frontend ./helm/todo-frontend \
  --set resources.requests.cpu=50m \
  --reuse-values

# Recommendation 3: Enable HPA
kubectl autoscale deployment todo-frontend \
  --min=1 --max=3 --cpu-percent=70
```

## Report Interpretation

### Understanding Severity Levels

**HIGH**: Immediate action required
- Risk of pod crashes or service disruption
- Performance significantly degraded
- Resource exhaustion imminent

**MEDIUM**: Action recommended soon
- Suboptimal resource allocation
- Performance could be improved
- Potential issues under load

**LOW**: Nice to have
- Minor optimizations
- Preventive measures
- Best practice improvements

### Reading Resource Metrics

**CPU Metrics**:
- **Request**: Guaranteed CPU allocation
- **Limit**: Maximum CPU allowed
- **Usage**: Current CPU consumption
- **Throttling**: CPU usage capped at limit

**Memory Metrics**:
- **Request**: Guaranteed memory allocation
- **Limit**: Maximum memory allowed
- **Usage**: Current memory consumption
- **OOMKilled**: Pod killed when exceeding limit

**Healthy Ranges**:
- CPU usage: 50-70% of limit (allows burst capacity)
- Memory usage: 60-80% of limit (prevents OOMKilled)
- Disk usage: <80% (prevents full disk issues)

### Trend Analysis

**Identify patterns**:
```bash
kagent analyze trends --duration 24h
```

**Output**:
```
Trend Analysis Report
=====================
Period: Last 24 hours

CPU Trends:
- Average: 45%
- Peak: 85% (at 14:00)
- Low: 20% (at 03:00)
- Pattern: Daily spike during business hours

Memory Trends:
- Average: 52%
- Peak: 75% (at 16:00)
- Low: 40% (at 04:00)
- Pattern: Gradual increase during day, drops at night

Recommendations:
- Consider HPA to handle daily traffic spikes
- Memory usage is stable, no leaks detected
```

## Best Practices

### 1. Regular Health Checks

Run health checks regularly:

```bash
# Daily health check
kagent health --detailed > health-$(date +%Y%m%d).txt

# Weekly trend analysis
kagent analyze trends --duration 7d
```

### 2. Monitor Before and After Changes

Always check metrics before and after making changes:

```bash
# Before change
kagent analyze resources > before.txt

# Make change (e.g., scale deployment)
helm upgrade todo-frontend ./helm/todo-frontend --set replicaCount=3

# Wait for stabilization
sleep 60

# After change
kagent analyze resources > after.txt

# Compare
diff before.txt after.txt
```

### 3. Act on High Priority Recommendations

Focus on HIGH severity recommendations first:

```bash
kagent recommend | grep "\[HIGH\]"
```

### 4. Validate Recommendations

Test recommendations in a safe way:

```bash
# Preview impact
kagent recommend --preview <id>

# Apply to single pod first
# Monitor for issues
# Then apply cluster-wide
```

### 5. Keep Historical Data

Save reports for trend analysis:

```bash
# Create reports directory
mkdir -p reports/$(date +%Y-%m)

# Save daily reports
kagent health --detailed > reports/$(date +%Y-%m)/health-$(date +%Y%m%d).txt
kagent analyze resources > reports/$(date +%Y-%m)/resources-$(date +%Y%m%d).txt
```

## Troubleshooting

### kagent Not Collecting Metrics

**Check metrics-server**:
```bash
kubectl get deployment metrics-server -n kube-system
kubectl top nodes
```

**Enable metrics-server**:
```bash
minikube addons enable metrics-server
```

**Wait for metrics to be available**:
```bash
# Metrics take 30-60 seconds to start collecting
sleep 60
kubectl top pods
```

### Inaccurate Resource Metrics

**Check metric collection interval**:
```bash
kagent config get metric-interval
# Should be 30s or less
```

**Force metric refresh**:
```bash
kagent analyze resources --refresh
```

### No Recommendations Generated

**Possible causes**:
1. Cluster is already optimized
2. Insufficient metrics data
3. Thresholds too strict

**Solutions**:
```bash
# Lower recommendation thresholds
kagent recommend --threshold low

# Wait for more metrics data
# (need at least 5 minutes of data)

# Check if metrics are being collected
kubectl top pods
```

### Permission Errors

**Check kagent permissions**:
```bash
kubectl auth can-i get pods
kubectl auth can-i get nodes
kubectl auth can-i get metrics
```

**Grant necessary permissions** (if needed):
```bash
# kagent needs read access to:
# - pods, nodes, services
# - metrics.k8s.io API
```

## Advanced Usage

### Custom Analysis Periods

```bash
# Last hour
kagent analyze resources --duration 1h

# Last 24 hours
kagent analyze resources --duration 24h

# Last week
kagent analyze resources --duration 7d
```

### Export Reports

```bash
# JSON format
kagent health --output json > health.json

# YAML format
kagent analyze resources --output yaml > resources.yaml

# CSV format (for spreadsheets)
kagent analyze resources --output csv > resources.csv
```

### Automated Monitoring

```bash
# Create monitoring script
cat > monitor.sh <<'EOF'
#!/bin/bash
while true; do
  kagent health --alert-threshold cpu=80,memory=80
  if [ $? -ne 0 ]; then
    echo "ALERT: Cluster health issue detected!"
    kagent analyze resources
  fi
  sleep 300  # Check every 5 minutes
done
EOF

chmod +x monitor.sh
./monitor.sh
```

### Integration with Alerting

```bash
# Check for critical issues
kagent health --severity critical --output json | \
  jq '.issues[] | select(.severity=="critical")'

# Send alert if critical issues found
if kagent health --severity critical | grep -q "critical"; then
  echo "Critical cluster issue!" | mail -s "Cluster Alert" admin@example.com
fi
```

## Quick Reference

| Operation | Command |
|-----------|---------|
| Health check | `kagent health` |
| CPU analysis | `kagent analyze cpu` |
| Memory analysis | `kagent analyze memory` |
| Detect bottlenecks | `kagent detect bottlenecks` |
| Get recommendations | `kagent recommend` |
| Trend analysis | `kagent analyze trends --duration 24h` |
| Export report | `kagent health --output json` |

## See Also

- [kubectl-ai Examples](./KUBECTL_AI_EXAMPLES.md) - Natural language operations
- [AI DevOps Best Practices](./AI_DEVOPS.md) - When to use which tool
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues
