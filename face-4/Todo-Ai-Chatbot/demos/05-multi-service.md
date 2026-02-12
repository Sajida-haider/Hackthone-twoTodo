# Demo 5: Multi-Service Management

## Overview

This demonstration shows how the Spec-Driven Infrastructure Automation system manages multiple services independently, each with its own blueprint, without cross-service interference.

**Scenario**: The `todo-frontend` and `todo-backend` services are managed simultaneously. Frontend experiences high load and scales up, while backend remains stable with no action needed.

**Agents Involved**:
- Multi-Service Coordinator (orchestrates evaluation of multiple services)
- Blueprint Parser (loads separate blueprints for each service)
- Decision Engine (makes independent decisions per service)
- Governance Enforcer (applies separate governance per service)
- Execution Engine (executes operations independently)
- Verification Engine (verifies each service independently)

**Duration**: ~2 minutes (both services evaluated in parallel)

---

## Step 1: Initial Setup

### Service Architecture

```
┌─────────────────────────────────────────────────────┐
│              Multi-Service Coordinator               │
│  Manages frontend and backend independently          │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐              ┌──────▼─────────┐
│ Frontend       │              │ Backend        │
│ Blueprint      │              │ Blueprint      │
│ (todo-frontend)│              │ (todo-backend) │
└───────┬────────┘              └──────┬─────────┘
        │                               │
┌───────▼────────┐              ┌──────▼─────────┐
│ Decision Engine│              │ Decision Engine│
│ (Frontend)     │              │ (Backend)      │
└───────┬────────┘              └──────┬─────────┘
        │                               │
┌───────▼────────┐              ┌──────▼─────────┐
│ Execution      │              │ Execution      │
│ (Frontend)     │              │ (Backend)      │
└────────────────┘              └────────────────┘
```

### Frontend Blueprint

```yaml
# blueprints/frontend/blueprint.yaml
metadata:
  name: todo-frontend
  version: 1.0.0
  priority: medium
  criticality: standard

spec:
  scaling:
    min_replicas: 1
    max_replicas: 5
    target_cpu_utilization: 70%
    target_memory_utilization: 80%
    scale_up_threshold: 80%
    scale_down_threshold: 40%

  resources:
    cpu_request: 50m
    cpu_limit: 200m
    memory_request: 128Mi
    memory_limit: 512Mi

  performance:
    latency_p95_target: 200ms
    error_rate_threshold: 1%
```

### Backend Blueprint

```yaml
# blueprints/backend/blueprint.yaml
metadata:
  name: todo-backend
  version: 1.0.0
  priority: high
  criticality: critical

spec:
  scaling:
    min_replicas: 2
    max_replicas: 5
    target_cpu_utilization: 70%
    target_memory_utilization: 80%
    scale_up_threshold: 75%
    scale_down_threshold: 35%

  resources:
    cpu_request: 100m
    cpu_limit: 500m
    memory_request: 256Mi
    memory_limit: 1Gi

  performance:
    latency_p95_target: 150ms
    error_rate_threshold: 0.5%
```

**Key Differences**:
- Backend has higher priority (high vs medium)
- Backend is critical service (critical vs standard)
- Backend has stricter thresholds (75% vs 80% scale-up)
- Backend has higher resource limits
- Backend has stricter performance targets

---

## Step 2: Current State

### Frontend State

```json
{
  "service": "todo-frontend",
  "replicas": 2,
  "pods_running": 2,
  "pods_ready": 2,
  "metrics": {
    "cpu_utilization": 0.85,
    "memory_utilization": 0.70,
    "latency_p50": 120,
    "latency_p95": 180,
    "throughput": 180,
    "error_rate": 0.005
  }
}
```

**Observation**: Frontend CPU is 85%, exceeding 80% threshold. Needs scaling.

### Backend State

```json
{
  "service": "todo-backend",
  "replicas": 3,
  "pods_running": 3,
  "pods_ready": 3,
  "metrics": {
    "cpu_utilization": 0.45,
    "memory_utilization": 0.50,
    "latency_p50": 60,
    "latency_p95": 100,
    "throughput": 250,
    "error_rate": 0.002
  }
}
```

**Observation**: Backend CPU is 45%, well within acceptable range. No action needed.

---

## Step 3: Parallel Metrics Collection

The Multi-Service Coordinator collects metrics for both services in parallel:

```bash
# Frontend metrics
kubectl top pods -n todo-app -l app=todo-frontend

NAME                             CPU(cores)   MEMORY(bytes)
todo-frontend-7d8f9c5b6d-abc12   85m          358Mi
todo-frontend-7d8f9c5b6d-def34   85m          358Mi

# Backend metrics
kubectl top pods -n todo-app -l app=todo-backend

NAME                            CPU(cores)   MEMORY(bytes)
todo-backend-6c7d8e9f5a-xyz01   45m          512Mi
todo-backend-6c7d8e9f5a-xyz02   45m          512Mi
todo-backend-6c7d8e9f5a-xyz03   45m          512Mi
```

**Key Point**: Metrics collected independently for each service.

---

## Step 4: Independent Decision Making

### Frontend Decision

The Decision Engine evaluates frontend metrics:

```python
# Frontend Decision Engine
weighted_util = (0.85 * 0.5) + (0.70 * 0.3) + (0.90 * 0.2)
# = 0.425 + 0.210 + 0.180 = 0.815 (81.5%)

if weighted_util > 0.80:  # scale_up_threshold
    return {
        "action": "scale_up",
        "current_replicas": 2,
        "target_replicas": 3,
        "rationale": "Weighted utilization (81.5%) exceeds threshold (80%)"
    }
```

**Frontend Decision Output**:

```json
{
  "decision_id": "dec-20260210-183000-001",
  "service": "todo-frontend",
  "decision_type": "scaling",
  "action": "scale_up",
  "current_replicas": 2,
  "target_replicas": 3,
  "rationale": "Weighted utilization (81.5%) exceeds scale_up_threshold (80%). Scaling to 3 replicas to reduce load.",
  "weighted_utilization": 0.815
}
```

### Backend Decision

The Decision Engine evaluates backend metrics:

```python
# Backend Decision Engine
weighted_util = (0.45 * 0.5) + (0.50 * 0.3) + (0.67 * 0.2)
# = 0.225 + 0.150 + 0.134 = 0.475 (47.5%)

if weighted_util < 0.35:  # scale_down_threshold
    return {"action": "scale_down"}
elif weighted_util > 0.75:  # scale_up_threshold
    return {"action": "scale_up"}
else:
    return {
        "action": "no_action",
        "rationale": "Utilization within optimal range"
    }
```

**Backend Decision Output**:

```json
{
  "decision_id": "dec-20260210-183000-002",
  "service": "todo-backend",
  "decision_type": "no_action",
  "action": "no_action",
  "current_replicas": 3,
  "target_replicas": 3,
  "rationale": "Weighted utilization (47.5%) is between scale_down_threshold (35%) and scale_up_threshold (75%). System operating within optimal range. No scaling needed.",
  "weighted_utilization": 0.475
}
```

**Key Point**: Decisions made independently based on each service's blueprint.

**Reference**: See `examples/multi-service-independent.json` for complete multi-service evaluation.

---

## Step 5: Independent Governance Checks

### Frontend Governance

```json
{
  "governance_check_id": "gov-20260210-183000-001",
  "service": "todo-frontend",
  "decision_id": "dec-20260210-183000-001",
  "classification": "allowed",
  "requires_approval": false,
  "rationale": "Target replicas (3) within blueprint limits (1-5)",
  "blueprint_references": [
    "blueprints/frontend/blueprint.yaml:spec.scaling.max_replicas"
  ]
}
```

**Result**: Frontend scale-up is **ALLOWED**.

### Backend Governance

```json
{
  "governance_check_id": "gov-20260210-183000-002",
  "service": "todo-backend",
  "decision_id": "dec-20260210-183000-002",
  "classification": "n/a",
  "requires_approval": false,
  "rationale": "No operation proposed, no governance check needed"
}
```

**Result**: Backend no-action requires **NO GOVERNANCE CHECK**.

**Key Point**: Governance applied independently per service.

---

## Step 6: Service Isolation Verification

The Multi-Service Coordinator verifies that services are truly independent:

### Independence Checks

```json
{
  "independence_verification": {
    "frontend_decision_independent": true,
    "backend_decision_independent": true,
    "no_cross_service_interference": true,
    "separate_blueprints_used": true,
    "separate_metrics_collected": true,
    "separate_governance_applied": true,
    "rationale": "Frontend and backend evaluated independently. Frontend decision to scale up did not affect backend decision. Backend remains stable while frontend scales."
  }
}
```

### Isolation Proof

```json
{
  "service_isolation_proof": {
    "frontend_metrics_not_affected_by_backend": true,
    "backend_metrics_not_affected_by_frontend": true,

    "separate_cooldown_timers": {
      "frontend_last_operation": "2026-02-10T18:25:00Z",
      "frontend_cooldown_elapsed": true,
      "backend_last_operation": "2026-02-10T18:10:00Z",
      "backend_cooldown_elapsed": true
    },

    "separate_circuit_breakers": {
      "frontend_circuit_breaker": "closed",
      "backend_circuit_breaker": "closed"
    },

    "independent_governance": {
      "frontend_governance": "allowed_operations applied",
      "backend_governance": "allowed_operations applied (different rules)"
    }
  }
}
```

**Key Point**: Complete isolation between services.

---

## Step 7: Execution - Frontend Only

Only the frontend operation is executed (backend has no operation):

### Frontend Execution

```bash
kubectl scale deployment todo-frontend --replicas=3 -n todo-app
```

```json
{
  "operation_id": "dec-20260210-183000-001",
  "service": "todo-frontend",
  "operation_type": "scale_up",
  "execution": {
    "started_at": "2026-02-10T18:30:05Z",
    "completed_at": "2026-02-10T18:30:07Z",
    "duration": "2.1s",
    "exit_code": 0,
    "stdout": "deployment.apps/todo-frontend scaled"
  }
}
```

### Backend Execution

```json
{
  "service": "todo-backend",
  "operation": "no_action",
  "command": "none",
  "execution_order": "n/a",
  "estimated_duration": "0s"
}
```

**Key Point**: Only frontend scaled. Backend unchanged.

---

## Step 8: Parallel Verification

Both services are verified independently:

### Frontend Verification

```json
{
  "verification_id": "ver-20260210-183130-001",
  "service": "todo-frontend",
  "outcome": "success",
  "checks": [
    {
      "check": "replica_count",
      "expected": 3,
      "actual": 3,
      "status": "passed"
    },
    {
      "check": "cpu_utilization",
      "expected": "< 70%",
      "actual": "57%",
      "status": "passed",
      "improvement": "28% reduction (85% → 57%)"
    },
    {
      "check": "latency_p95",
      "expected": "< 200ms",
      "actual": "150ms",
      "status": "passed"
    }
  ],
  "summary": {
    "verification_result": "success"
  }
}
```

**Result**: Frontend verification **PASSED**.

### Backend Verification

```json
{
  "verification_id": "ver-20260210-183130-002",
  "service": "todo-backend",
  "outcome": "no_verification_needed",
  "rationale": "No operation executed, service remains stable",
  "current_state": {
    "replicas": 3,
    "cpu_utilization": 0.45,
    "latency_p95": 100,
    "status": "healthy"
  }
}
```

**Result**: Backend remains stable, no verification needed.

**Key Point**: Verification performed independently per service.

---

## Step 9: Expected Outcomes

### Frontend Outcome

```json
{
  "service": "todo-frontend",
  "replicas_before": 2,
  "replicas_after": 3,
  "cpu_before": 0.85,
  "cpu_after": 0.57,
  "latency_before": 180,
  "latency_after": 150,
  "improvement": "Reduced load per replica, improved performance"
}
```

### Backend Outcome

```json
{
  "service": "todo-backend",
  "replicas_before": 3,
  "replicas_after": 3,
  "cpu_before": 0.45,
  "cpu_after": 0.45,
  "latency_before": 100,
  "latency_after": 100,
  "status": "Remains stable, no changes"
}
```

**Key Point**: Frontend improved, backend unchanged.

---

## Step 10: Multi-Service Benefits

### Benefit 1: Independent Scaling

✅ **Frontend scales without waiting for backend**
- Frontend needed scaling, scaled immediately
- Backend didn't need scaling, remained stable
- No unnecessary operations on backend

### Benefit 2: Service-Specific Optimization

✅ **Each service optimized for its own workload**
- Frontend optimized for web traffic patterns
- Backend optimized for API request patterns
- Different thresholds, different targets

### Benefit 3: No Cascading Effects

✅ **No cross-service interference**
- Frontend scaling didn't trigger backend scaling
- Backend stability didn't prevent frontend scaling
- Each service operates independently

### Benefit 4: Resource Efficiency

✅ **Resources allocated only where needed**
- Frontend: +1 replica (50m CPU, 128Mi memory)
- Backend: 0 replicas (no resources allocated)
- Total cost: Only what's needed

### Benefit 5: Separate Governance

✅ **Different governance rules per service**
- Frontend: medium priority, standard criticality
- Backend: high priority, critical service
- Different approval workflows if needed

---

## Comparison: Multi-Service vs Single-Service

### If Managed Together (Single Blueprint)

```yaml
# Hypothetical combined blueprint (WRONG APPROACH)
metadata:
  name: todo-app
  services: [frontend, backend]

spec:
  scaling:
    scale_up_threshold: 80%  # Which service's threshold?
    target_cpu_utilization: 70%  # Same for both?
```

**Problems**:
- ❌ Cannot have different thresholds per service
- ❌ Would need to scale both services together
- ❌ Backend would scale unnecessarily
- ❌ Wastes resources
- ❌ Cannot optimize per service

### With Independent Management (Separate Blueprints)

```yaml
# Frontend blueprint
metadata:
  name: todo-frontend
spec:
  scaling:
    scale_up_threshold: 80%

# Backend blueprint
metadata:
  name: todo-backend
spec:
  scaling:
    scale_up_threshold: 75%
```

**Benefits**:
- ✅ Different thresholds per service
- ✅ Each service scales independently
- ✅ Backend remains stable
- ✅ Efficient resource usage
- ✅ Service-specific optimization

---

## Timeline Summary

```
18:30:00 - Multi-Service Coordinator: Evaluate all services
18:30:00 - Frontend: High CPU detected (85%)
18:30:00 - Backend: Normal CPU detected (45%)
18:30:00 - Frontend Decision: Scale from 2 to 3 replicas
18:30:00 - Backend Decision: No action needed
18:30:00 - Frontend Governance: Allowed
18:30:00 - Backend Governance: N/A
18:30:05 - Frontend Execution: kubectl scale executed (2.1s)
18:30:07 - Backend Execution: None
18:30:07 - Frontend: New pod starting
18:30:57 - Frontend: New pod ready (50s)
18:31:30 - Frontend Verification: Success ✓
18:31:30 - Backend Verification: Stable ✓
18:31:30 - Multi-Service evaluation complete

Total Duration: 1m 30s (both services evaluated in parallel)
```

**Key Point**: Both services evaluated simultaneously, but only frontend scaled.

---

## Resource Conflict Scenario

What if both services needed scaling but cluster capacity was limited?

### Conflict Detection

```json
{
  "conflict_detection": {
    "conflicts_detected": true,
    "conflict_type": "resource_conflict",

    "cluster_capacity": {
      "cpu_available": "120m",
      "memory_available": "300Mi"
    },

    "total_resources_requested": {
      "frontend_cpu": "50m",
      "backend_cpu": "100m",
      "total_cpu": "150m"
    },

    "capacity_check": {
      "cpu_sufficient": false,
      "cpu_shortfall": "30m"
    }
  }
}
```

### Conflict Resolution

```json
{
  "conflict_resolution": {
    "strategy": "prioritize_by_criticality",

    "backend": {
      "priority_level": "high",
      "criticality": "critical",
      "priority_score": 90,
      "action": "execute",
      "rationale": "Backend is critical service, gets priority"
    },

    "frontend": {
      "priority_level": "medium",
      "criticality": "standard",
      "priority_score": 50,
      "action": "defer",
      "defer_duration": "5 minutes",
      "rationale": "Frontend deferred until resources available"
    }
  }
}
```

**Key Point**: Priority-based resolution when conflicts occur.

**Reference**: See `examples/multi-service-conflict.json` for complete conflict scenario.

---

## Key Observations

### True Independence

✅ **Services operate independently**
- Separate blueprints
- Separate metrics
- Separate decisions
- Separate governance
- Separate execution
- Separate verification

### Intelligent Coordination

✅ **Coordinator manages without interference**
- Evaluates all services in parallel
- Detects potential conflicts
- Resolves conflicts by priority
- Ensures cluster capacity

### Service-Specific Policies

✅ **Each service has its own rules**
- Frontend: 80% scale-up threshold
- Backend: 75% scale-up threshold
- Different resource limits
- Different performance targets

### Efficient Resource Usage

✅ **Resources allocated optimally**
- Frontend: Scaled when needed
- Backend: Remained stable
- No wasted resources
- Cost-effective operation

---

## Multi-Service Best Practices

### 1. Separate Blueprints

✅ **Create separate blueprint per service**
```
blueprints/
├── frontend/
│   └── blueprint.yaml
└── backend/
    └── blueprint.yaml
```

### 2. Service-Specific Thresholds

✅ **Tune thresholds per service**
```yaml
# Frontend (web traffic, bursty)
scale_up_threshold: 80%
scale_down_threshold: 40%

# Backend (API traffic, steady)
scale_up_threshold: 75%
scale_down_threshold: 35%
```

### 3. Priority Assignment

✅ **Assign priorities for conflict resolution**
```yaml
# Critical services
priority: high
criticality: critical

# Standard services
priority: medium
criticality: standard
```

### 4. Independent Monitoring

✅ **Monitor each service separately**
```bash
# Frontend metrics
kubectl top pods -l app=todo-frontend

# Backend metrics
kubectl top pods -l app=todo-backend
```

### 5. Coordinated Updates

✅ **Update blueprints in coordination**
- Review impact on other services
- Consider cluster capacity
- Test in staging first

---

## Try It Yourself

### Prerequisites

1. Kubernetes cluster with frontend and backend deployed
2. Separate blueprints for each service
3. Multi-Service Coordinator running
4. Monitoring system collecting metrics

### Simulation Steps

```bash
# 1. Check current state of both services
kubectl get deployments -n todo-app

# 2. Simulate high load on frontend only
kubectl run load-generator-frontend --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://todo-frontend:3000; done"

# 3. Watch both services
watch kubectl get pods -n todo-app

# 4. Observe frontend scales, backend remains stable
# Frontend: 2 → 3 replicas
# Backend: 3 → 3 replicas (no change)

# 5. Check audit logs for both services
cat logs/agent-decisions/$(date +%Y-%m-%d)/multi-service.log | \
  jq '.service'

# 6. Verify independence
# Frontend should have scaled
# Backend should be unchanged
```

---

## Related Documentation

- **Multi-Service Architecture**: `docs/MULTI_SERVICE.md`
- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`
- **Decision Engine**: `docs/DECISION_ENGINE.md`
- **Conflict Resolution**: `docs/CONFLICT_RESOLUTION.md`

---

## Summary

This demo showed:

1. ✅ **Independent Blueprints**: Frontend and backend have separate blueprints
2. ✅ **Independent Decisions**: Each service evaluated separately
3. ✅ **No Interference**: Frontend scaling didn't affect backend
4. ✅ **Service Isolation**: Complete isolation between services
5. ✅ **Efficient Resources**: Only frontend scaled, backend remained stable
6. ✅ **Conflict Handling**: System can detect and resolve conflicts when needed

**Key Takeaway**: Multi-service management enables independent, efficient, and intelligent infrastructure automation at scale.
