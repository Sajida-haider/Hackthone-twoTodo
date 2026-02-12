# Demo 1: Autonomous Scaling

## Overview

This demonstration shows how the Spec-Driven Infrastructure Automation system autonomously scales a service in response to high CPU utilization, without human intervention.

**Scenario**: The `todo-frontend` service experiences high load, triggering autonomous scaling from 2 to 3 replicas.

**Agents Involved**:
- Blueprint Parser (loads and validates blueprint)
- Decision Engine (analyzes metrics and decides to scale)
- Governance Enforcer (validates operation is allowed)
- Execution Engine (executes scaling command)
- Verification Engine (verifies outcome)

**Duration**: ~2 minutes from trigger to verification

---

## Step 1: Initial Setup

### Blueprint Configuration

The `todo-frontend` service has the following blueprint configuration:

```yaml
# blueprints/frontend/blueprint.yaml
metadata:
  name: todo-frontend
  version: 1.0.0

spec:
  scaling:
    min_replicas: 1
    max_replicas: 5
    target_cpu_utilization: 70%
    target_memory_utilization: 80%
    scale_up_threshold: 80%
    scale_down_threshold: 40%

governance:
  agent_authority:
    allowed_operations:
      - operation: scale_within_limits
        condition: target_replicas >= min_replicas AND target_replicas <= max_replicas
        autonomous: true
```

### Current State

```json
{
  "service": "todo-frontend",
  "replicas": 2,
  "pods_running": 2,
  "pods_ready": 2,
  "metrics": {
    "cpu_utilization": 0.85,
    "memory_utilization": 0.70,
    "latency_p95": 180
  }
}
```

**Observation**: CPU utilization is 85%, which exceeds the scale_up_threshold of 80%.

---

## Step 2: Metrics Collection

The monitoring system continuously collects metrics from the service:

```bash
# Simulated metrics collection
kubectl top pods -n todo-app -l app=todo-frontend

NAME                             CPU(cores)   MEMORY(bytes)
todo-frontend-7d8f9c5b6d-abc12   85m          358Mi
todo-frontend-7d8f9c5b6d-def34   85m          358Mi
```

**Calculated Metrics**:
- Average CPU: 85% (85m / 100m request)
- Average Memory: 70% (358Mi / 512Mi limit)
- Latency P95: 180ms (target: 200ms)

**Weighted Utilization**: (0.85 × 0.5) + (0.70 × 0.3) + (0.90 × 0.2) = **0.815** (81.5%)

---

## Step 3: Decision Engine Analysis

The Decision Engine receives the metrics and analyzes them against the blueprint:

### Decision Logic

```python
# Pseudocode from Decision Engine
def make_scaling_decision(metrics, blueprint):
    weighted_util = calculate_weighted_utilization(metrics)

    if weighted_util > blueprint.scale_up_threshold:
        # Calculate target replicas
        current_replicas = metrics.replicas
        target_replicas = calculate_target_replicas(
            current_replicas,
            weighted_util,
            blueprint.target_cpu_utilization
        )

        return {
            "action": "scale_up",
            "current_replicas": current_replicas,
            "target_replicas": target_replicas,
            "rationale": f"Weighted utilization ({weighted_util}) exceeds threshold"
        }
```

### Decision Output

```json
{
  "decision_id": "dec-20260210-153000-001",
  "decision_type": "scaling",
  "action": "scale_up",
  "current_replicas": 2,
  "target_replicas": 3,
  "rationale": "Weighted utilization (81.5%) exceeds scale_up_threshold (80%). Scaling to 3 replicas to reduce load.",
  "weighted_utilization": 0.815,
  "expected_outcome": {
    "replicas": 3,
    "expected_cpu_utilization": 0.57,
    "expected_memory_utilization": 0.47
  }
}
```

**Decision**: Scale from 2 to 3 replicas.

**Reference**: See `examples/scaling-decision.json` for complete decision structure.

---

## Step 4: Governance Check

The Governance Enforcer validates the decision against governance policies:

### Governance Logic

```python
# Pseudocode from Governance Enforcer
def classify_operation(decision, blueprint):
    target_replicas = decision.target_replicas
    min_replicas = blueprint.spec.scaling.min_replicas
    max_replicas = blueprint.spec.scaling.max_replicas

    # Check if within limits
    if min_replicas <= target_replicas <= max_replicas:
        return {
            "classification": "allowed",
            "requires_approval": False,
            "rationale": f"Target replicas ({target_replicas}) within limits ({min_replicas}-{max_replicas})"
        }
```

### Governance Output

```json
{
  "governance_check_id": "gov-20260210-153030-001",
  "decision_id": "dec-20260210-153000-001",
  "classification": "allowed",
  "requires_approval": false,
  "rationale": "Target replicas (3) within blueprint limits (1-5)",
  "blueprint_references": [
    "spec.scaling.min_replicas",
    "spec.scaling.max_replicas",
    "governance.agent_authority.allowed_operations[0]"
  ],
  "safety_checks": {
    "circuit_breaker": "closed",
    "cooldown_elapsed": true,
    "rate_limit_ok": true
  }
}
```

**Result**: Operation is **ALLOWED** - proceed with execution autonomously.

**Reference**: See `examples/governance-allowed.json` for complete governance check.

---

## Step 5: Execution

The Execution Engine executes the scaling operation:

### Execution Command

```bash
kubectl scale deployment todo-frontend --replicas=3 -n todo-app
```

### Execution Output

```json
{
  "operation_id": "dec-20260210-153000-001",
  "operation_type": "scale_up",
  "execution": {
    "started_at": "2026-02-10T15:30:45Z",
    "completed_at": "2026-02-10T15:30:47Z",
    "duration": "2.3s",
    "exit_code": 0,
    "stdout": "deployment.apps/todo-frontend scaled",
    "stderr": ""
  },
  "post_operation_state": {
    "replicas": 3,
    "pods_running": 2,
    "pods_ready": 2,
    "pods_pending": 1,
    "note": "New pod starting, not ready yet"
  }
}
```

**Result**: Deployment scaled successfully. New pod is starting.

**Reference**: See `examples/audit-operation.json` for complete operation log.

---

## Step 6: Stabilization Period

The system waits 60 seconds for the new pod to start and become ready:

```bash
# Watch pod status
kubectl get pods -n todo-app -l app=todo-frontend -w

NAME                             READY   STATUS    RESTARTS   AGE
todo-frontend-7d8f9c5b6d-abc12   1/1     Running   0          10m
todo-frontend-7d8f9c5b6d-def34   1/1     Running   0          10m
todo-frontend-7d8f9c5b6d-ghi56   0/1     Pending   0          2s
todo-frontend-7d8f9c5b6d-ghi56   0/1     ContainerCreating   0          5s
todo-frontend-7d8f9c5b6d-ghi56   1/1     Running             0          45s
```

**Stabilization**: 60 seconds configured in blueprint.

---

## Step 7: Verification

The Verification Engine verifies the operation was successful:

### Verification Checks

```python
# Pseudocode from Verification Engine
def verify_scaling_operation(operation, blueprint):
    checks = []

    # Check 1: Replica count matches target
    checks.append(verify_replica_count(operation.target_replicas))

    # Check 2: All pods are ready
    checks.append(verify_pods_ready())

    # Check 3: CPU utilization reduced
    checks.append(verify_cpu_reduced(blueprint.target_cpu_utilization))

    # Check 4: Latency within target
    checks.append(verify_latency(blueprint.latency_p95_target))

    # Check 5: No error rate increase
    checks.append(verify_error_rate())

    return all(checks)
```

### Verification Output

```json
{
  "verification_id": "ver-20260210-153200-001",
  "operation_id": "dec-20260210-153000-001",
  "verification_timestamp": "2026-02-10T15:32:00Z",
  "outcome": "success",

  "checks": [
    {
      "check": "replica_count",
      "expected": 3,
      "actual": 3,
      "status": "passed"
    },
    {
      "check": "pods_ready",
      "expected": 3,
      "actual": 3,
      "status": "passed"
    },
    {
      "check": "cpu_utilization",
      "expected": "< 70%",
      "actual": "60%",
      "status": "passed",
      "improvement": "25% reduction (85% → 60%)"
    },
    {
      "check": "memory_utilization",
      "expected": "< 80%",
      "actual": "50%",
      "status": "passed"
    },
    {
      "check": "latency_p95",
      "expected": "< 200ms",
      "actual": "150ms",
      "status": "passed",
      "improvement": "30ms reduction (180ms → 150ms)"
    },
    {
      "check": "error_rate",
      "expected": "< 1%",
      "actual": "0.3%",
      "status": "passed"
    }
  ],

  "summary": {
    "total_checks": 6,
    "passed": 6,
    "failed": 0,
    "verification_result": "success"
  }
}
```

**Result**: All checks passed. Operation verified successfully.

**Reference**: See `examples/verification-success.json` for complete verification log.

---

## Step 8: Audit Logging

All agent actions are logged for audit trail:

### Decision Log

```json
{
  "timestamp": "2026-02-10T15:30:00Z",
  "event_type": "decision_made",
  "agent_id": "decision-engine-001",
  "service": "todo-frontend",
  "decision": {
    "action": "scale_up",
    "from_replicas": 2,
    "to_replicas": 3,
    "rationale": "Weighted utilization 81.5% exceeds threshold 80%"
  }
}
```

### Governance Log

```json
{
  "timestamp": "2026-02-10T15:30:30Z",
  "event_type": "governance_check",
  "agent_id": "governance-enforcer-001",
  "classification": "allowed",
  "requires_approval": false
}
```

### Operation Log

```json
{
  "timestamp": "2026-02-10T15:30:45Z",
  "event_type": "operation_executed",
  "agent_id": "execution-engine-001",
  "operation": "scale_up",
  "exit_code": 0,
  "duration": "2.3s"
}
```

### Verification Log

```json
{
  "timestamp": "2026-02-10T15:32:00Z",
  "event_type": "verification_completed",
  "agent_id": "verification-engine-001",
  "outcome": "success",
  "checks_passed": 6,
  "checks_failed": 0
}
```

**Reference**: See `docs/AUDIT_LOGGING.md` for complete audit log format.

---

## Timeline Summary

```
15:30:00 - High CPU detected (85%)
15:30:00 - Decision Engine: Scale from 2 to 3 replicas
15:30:30 - Governance Enforcer: Operation allowed
15:30:45 - Execution Engine: kubectl scale executed (2.3s)
15:30:47 - New pod starting
15:31:32 - New pod ready (45s startup time)
15:32:00 - Verification Engine: All checks passed
15:32:00 - Operation complete

Total Duration: 2 minutes (from trigger to verification)
```

---

## Key Observations

### Autonomous Operation

✅ **No human intervention required**
- Decision made autonomously by Decision Engine
- Governance check passed automatically
- Execution proceeded without approval
- Verification confirmed success

### Blueprint Compliance

✅ **All actions within blueprint limits**
- Target replicas (3) within min/max (1-5)
- Operation classified as "allowed"
- Safety mechanisms respected (circuit breaker, cooldown)

### Performance Improvement

✅ **Metrics improved after scaling**
- CPU: 85% → 60% (25% reduction)
- Latency: 180ms → 150ms (30ms improvement)
- Error rate: 0.5% → 0.3% (40% reduction)

### Audit Trail

✅ **Complete audit trail maintained**
- Decision logged with rationale
- Governance check logged
- Operation execution logged
- Verification results logged

---

## What Makes This Autonomous?

1. **No Human Approval**: Operation within blueprint limits, no approval needed
2. **Automatic Trigger**: Metrics monitoring detected high CPU automatically
3. **Intelligent Decision**: Decision Engine calculated optimal replica count
4. **Self-Validation**: Governance Enforcer validated operation autonomously
5. **Self-Verification**: Verification Engine confirmed success automatically

---

## Contrast with Manual Approach

### Traditional Manual Approach

```
1. Operator notices high CPU in monitoring dashboard
2. Operator analyzes metrics manually
3. Operator decides to scale (based on experience)
4. Operator runs: kubectl scale deployment todo-frontend --replicas=3
5. Operator monitors pod startup
6. Operator checks metrics after scaling
7. Operator documents change in ticket

Time: 10-30 minutes (depending on operator availability)
```

### Spec-Driven Autonomous Approach

```
1. System detects high CPU automatically
2. Decision Engine analyzes metrics against blueprint
3. Governance Enforcer validates operation
4. Execution Engine scales deployment
5. Verification Engine confirms success
6. All actions logged automatically

Time: 2 minutes (fully automated)
```

**Improvement**: 5-15x faster, consistent, documented, no human error.

---

## Try It Yourself

### Prerequisites

1. Kubernetes cluster (Minikube or cloud)
2. Todo AI Chatbot deployed
3. Blueprint configured for todo-frontend
4. Agent system running

### Simulation Steps

```bash
# 1. Check current state
kubectl get deployment todo-frontend -n todo-app

# 2. Simulate high load (optional)
kubectl run load-generator --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://todo-frontend:3000; done"

# 3. Watch agent logs
kubectl logs -f -l app=agent-system -n agent-system

# 4. Observe autonomous scaling
kubectl get pods -n todo-app -l app=todo-frontend -w

# 5. Check audit logs
cat logs/agent-decisions/$(date +%Y-%m-%d)/decisions.log | jq '.event_type'
```

---

## Related Documentation

- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`
- **Decision Engine**: `docs/DECISION_ENGINE.md`
- **Governance**: `docs/GOVERNANCE.md`
- **Verification**: `docs/VERIFICATION_ENGINE.md`
- **Audit Logging**: `docs/AUDIT_LOGGING.md`

---

## Next Demos

- **Demo 2**: Approval Workflow (operation requiring human approval)
- **Demo 3**: Governance Blocking (forbidden operation blocked)
- **Demo 4**: Rollback on Failure (automatic rollback when verification fails)
- **Demo 5**: Multi-Service Management (independent management of multiple services)
