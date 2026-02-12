# Demo 4: Rollback on Failure

## Overview

This demonstration shows how the Spec-Driven Infrastructure Automation system automatically rolls back an operation when verification checks fail, ensuring service reliability.

**Scenario**: The `todo-frontend` service is scaled down from 3 to 2 replicas to save costs. However, verification reveals that latency has spiked and error rate has increased, triggering an automatic rollback.

**Agents Involved**:
- Decision Engine (decides to scale down)
- Governance Enforcer (validates operation is allowed)
- Execution Engine (executes scale down)
- Verification Engine (detects failure, triggers rollback)
- Execution Engine (executes rollback)
- Verification Engine (verifies rollback success)

**Duration**: ~5 minutes (including rollback and re-verification)

---

## Step 1: Initial Setup

### Blueprint Configuration

The `todo-frontend` service has the following verification configuration:

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
    scale_down_threshold: 40%

  performance:
    latency_p95_target: 200ms
    error_rate_threshold: 1%

verification:
  stabilization_period: 60s

  checks:
    - name: replica_count
      type: exact_match
      critical: true

    - name: pods_ready
      type: exact_match
      critical: true

    - name: cpu_utilization
      type: threshold
      target: "< 80%"
      critical: false

    - name: latency_p95
      type: threshold
      target: "< 200ms"
      critical: true
      rollback_trigger: true

    - name: error_rate
      type: threshold
      target: "< 1%"
      critical: true
      rollback_trigger: true

  rollback:
    enabled: true
    automatic: true
    trigger_on_critical_failure: true
    max_rollback_attempts: 3
```

### Current State

```json
{
  "service": "todo-frontend",
  "replicas": 3,
  "pods_running": 3,
  "pods_ready": 3,
  "metrics": {
    "cpu_utilization": 0.35,
    "memory_utilization": 0.40,
    "latency_p95": 120,
    "error_rate": 0.002
  }
}
```

**Observation**: CPU is low (35%), suggesting scale-down opportunity.

---

## Step 2: Decision to Scale Down

The Decision Engine analyzes metrics and decides to scale down:

### Decision Logic

```python
# Pseudocode from Decision Engine
def make_scaling_decision(metrics, blueprint):
    weighted_util = calculate_weighted_utilization(metrics)

    if weighted_util < blueprint.scale_down_threshold:
        # Calculate target replicas
        current_replicas = metrics.replicas
        target_replicas = max(
            blueprint.min_replicas,
            current_replicas - 1
        )

        return {
            "action": "scale_down",
            "current_replicas": current_replicas,
            "target_replicas": target_replicas,
            "rationale": f"Low utilization ({weighted_util}), scale down to save costs"
        }
```

### Decision Output

```json
{
  "decision_id": "dec-20260210-190000-006",
  "decision_type": "scaling",
  "action": "scale_down",
  "current_replicas": 3,
  "target_replicas": 2,
  "rationale": "Weighted utilization (37.5%) below scale_down_threshold (40%). Scaling down to save costs.",
  "weighted_utilization": 0.375,
  "expected_outcome": {
    "replicas": 2,
    "expected_cpu_utilization": 0.53,
    "expected_memory_utilization": 0.60,
    "cost_savings": "$10/month"
  }
}
```

**Decision**: Scale from 3 to 2 replicas.

---

## Step 3: Governance Check

The Governance Enforcer validates the decision:

```json
{
  "governance_check_id": "gov-20260210-190030-004",
  "decision_id": "dec-20260210-190000-006",
  "classification": "allowed",
  "requires_approval": false,
  "rationale": "Target replicas (2) within blueprint limits (1-5)",
  "safety_checks": {
    "circuit_breaker": "closed",
    "cooldown_elapsed": true,
    "rate_limit_ok": true
  }
}
```

**Result**: Operation is **ALLOWED** - proceed with execution.

---

## Step 4: Execution

The Execution Engine executes the scale-down operation:

### Execution Command

```bash
kubectl scale deployment todo-frontend --replicas=2 -n todo-app
```

### Execution Output

```json
{
  "operation_id": "dec-20260210-190000-006",
  "operation_type": "scale_down",
  "execution": {
    "started_at": "2026-02-10T19:00:45Z",
    "completed_at": "2026-02-10T19:00:47Z",
    "duration": "2.1s",
    "exit_code": 0,
    "stdout": "deployment.apps/todo-frontend scaled"
  },
  "pre_operation_state": {
    "replicas": 3,
    "pods_running": 3,
    "pods_ready": 3
  },
  "post_operation_state": {
    "replicas": 2,
    "pods_running": 2,
    "pods_ready": 2,
    "pods_terminating": 1
  }
}
```

**Result**: Deployment scaled down. One pod is terminating.

---

## Step 5: Stabilization Period

The system waits 60 seconds for metrics to stabilize:

```bash
# Watch pod status
kubectl get pods -n todo-app -l app=todo-frontend -w

NAME                             READY   STATUS        RESTARTS   AGE
todo-frontend-7d8f9c5b6d-abc12   1/1     Running       0          20m
todo-frontend-7d8f9c5b6d-def34   1/1     Running       0          20m
todo-frontend-7d8f9c5b6d-ghi56   1/1     Terminating   0          20m
todo-frontend-7d8f9c5b6d-ghi56   0/1     Terminating   0          20m
```

**Stabilization**: 60 seconds to allow load redistribution and metric collection.

---

## Step 6: Verification - FAILURE DETECTED

The Verification Engine checks the operation outcome:

### Verification Checks

```python
# Pseudocode from Verification Engine
def verify_scaling_operation(operation, blueprint):
    checks = []

    # Check 1: Replica count
    checks.append(verify_replica_count(operation.target_replicas))

    # Check 2: Pods ready
    checks.append(verify_pods_ready())

    # Check 3: CPU utilization
    checks.append(verify_cpu_utilization(blueprint.target_cpu_utilization))

    # Check 4: Latency (CRITICAL)
    latency_check = verify_latency(blueprint.latency_p95_target)
    if not latency_check.passed and latency_check.critical:
        return trigger_rollback("Latency exceeds target")

    # Check 5: Error rate (CRITICAL)
    error_check = verify_error_rate(blueprint.error_rate_threshold)
    if not error_check.passed and error_check.critical:
        return trigger_rollback("Error rate exceeds threshold")

    return all(checks)
```

### Verification Output - FAILURE

```json
{
  "verification_id": "ver-20260210-190200-008",
  "operation_id": "dec-20260210-190000-006",
  "verification_timestamp": "2026-02-10T19:02:00Z",
  "outcome": "failure",

  "checks": [
    {
      "check": "replica_count",
      "expected": 2,
      "actual": 2,
      "status": "passed",
      "critical": true
    },
    {
      "check": "pods_ready",
      "expected": 2,
      "actual": 2,
      "status": "passed",
      "critical": true
    },
    {
      "check": "cpu_utilization",
      "expected": "< 80%",
      "actual": "65%",
      "status": "passed",
      "critical": false
    },
    {
      "check": "latency_p95",
      "expected": "< 200ms",
      "actual": "280ms",
      "status": "FAILED",
      "critical": true,
      "rollback_trigger": true,
      "degradation": "133% increase (120ms → 280ms)"
    },
    {
      "check": "error_rate",
      "expected": "< 1%",
      "actual": "1.2%",
      "status": "FAILED",
      "critical": true,
      "rollback_trigger": true,
      "degradation": "500% increase (0.2% → 1.2%)"
    }
  ],

  "summary": {
    "total_checks": 5,
    "passed": 3,
    "failed": 2,
    "critical_failures": 2,
    "verification_result": "failure"
  },

  "failure_analysis": {
    "root_cause": "Insufficient capacity after scale-down",
    "impact": "Latency spike and increased error rate",
    "severity": "high",
    "user_impact": "Degraded user experience"
  },

  "rollback_decision": {
    "rollback_required": true,
    "rollback_reason": "Critical verification checks failed: latency_p95, error_rate",
    "automatic_rollback": true,
    "rollback_target": {
      "replicas": 3,
      "rationale": "Restore to pre-operation state"
    }
  }
}
```

**Result**: Verification **FAILED** - Latency and error rate exceeded thresholds.

**Reference**: See `examples/verification-failure.json` for complete verification log.

---

## Step 7: Automatic Rollback Triggered

The Verification Engine automatically triggers rollback:

### Rollback Decision

```json
{
  "rollback_id": "rb-20260210-190200-001",
  "triggered_by": "verification-engine-001",
  "trigger_reason": "critical_verification_failure",
  "original_operation_id": "dec-20260210-190000-006",
  "timestamp": "2026-02-10T19:02:00Z",

  "rollback_plan": {
    "action": "scale_up",
    "from_replicas": 2,
    "to_replicas": 3,
    "rationale": "Restore to pre-operation state due to verification failure",
    "command": "kubectl scale deployment todo-frontend --replicas=3 -n todo-app"
  },

  "failure_details": {
    "failed_checks": ["latency_p95", "error_rate"],
    "latency_actual": "280ms",
    "latency_target": "200ms",
    "error_rate_actual": "1.2%",
    "error_rate_threshold": "1%"
  },

  "automatic": true,
  "approval_required": false
}
```

**Decision**: Automatically rollback to 3 replicas.

---

## Step 8: Rollback Execution

The Execution Engine executes the rollback:

### Rollback Command

```bash
kubectl scale deployment todo-frontend --replicas=3 -n todo-app
```

### Rollback Execution Output

```json
{
  "rollback_id": "rb-20260210-190200-001",
  "operation_type": "rollback_scale_up",
  "execution": {
    "started_at": "2026-02-10T19:02:05Z",
    "completed_at": "2026-02-10T19:02:07Z",
    "duration": "2.0s",
    "exit_code": 0,
    "stdout": "deployment.apps/todo-frontend scaled"
  },
  "pre_rollback_state": {
    "replicas": 2,
    "pods_running": 2,
    "pods_ready": 2,
    "latency_p95": 280,
    "error_rate": 0.012
  },
  "post_rollback_state": {
    "replicas": 3,
    "pods_running": 2,
    "pods_ready": 2,
    "pods_pending": 1,
    "note": "New pod starting"
  }
}
```

**Result**: Rollback executed successfully. New pod is starting.

---

## Step 9: Rollback Stabilization

The system waits for the new pod to become ready:

```bash
# Watch pod status during rollback
kubectl get pods -n todo-app -l app=todo-frontend -w

NAME                             READY   STATUS    RESTARTS   AGE
todo-frontend-7d8f9c5b6d-abc12   1/1     Running   0          22m
todo-frontend-7d8f9c5b6d-def34   1/1     Running   0          22m
todo-frontend-7d8f9c5b6d-jkl78   0/1     Pending   0          2s
todo-frontend-7d8f9c5b6d-jkl78   0/1     ContainerCreating   0          5s
todo-frontend-7d8f9c5b6d-jkl78   1/1     Running             0          50s
```

**Stabilization**: 60 seconds for new pod to start and metrics to stabilize.

---

## Step 10: Rollback Verification - SUCCESS

The Verification Engine verifies the rollback was successful:

### Rollback Verification Output

```json
{
  "verification_id": "ver-20260210-190330-009",
  "rollback_id": "rb-20260210-190200-001",
  "verification_timestamp": "2026-02-10T19:03:30Z",
  "outcome": "success",

  "checks": [
    {
      "check": "replica_count",
      "expected": 3,
      "actual": 3,
      "status": "passed",
      "critical": true
    },
    {
      "check": "pods_ready",
      "expected": 3,
      "actual": 3,
      "status": "passed",
      "critical": true
    },
    {
      "check": "cpu_utilization",
      "expected": "< 80%",
      "actual": "38%",
      "status": "passed",
      "critical": false
    },
    {
      "check": "latency_p95",
      "expected": "< 200ms",
      "actual": "125ms",
      "status": "passed",
      "critical": true,
      "improvement": "Restored from 280ms to 125ms"
    },
    {
      "check": "error_rate",
      "expected": "< 1%",
      "actual": "0.3%",
      "status": "passed",
      "critical": true,
      "improvement": "Restored from 1.2% to 0.3%"
    }
  ],

  "summary": {
    "total_checks": 5,
    "passed": 5,
    "failed": 0,
    "verification_result": "success"
  },

  "recovery_analysis": {
    "service_restored": true,
    "latency_recovered": true,
    "error_rate_recovered": true,
    "recovery_time": "3m 30s",
    "user_impact_duration": "3m 30s"
  }
}
```

**Result**: Rollback verification **PASSED** - Service fully restored.

---

## Step 11: Audit Logging

Complete audit trail of the operation and rollback:

### Operation Log

```json
{
  "timestamp": "2026-02-10T19:00:45Z",
  "event_type": "operation_executed",
  "operation_id": "dec-20260210-190000-006",
  "action": "scale_down",
  "from_replicas": 3,
  "to_replicas": 2,
  "outcome": "executed"
}
```

### Verification Failure Log

```json
{
  "timestamp": "2026-02-10T19:02:00Z",
  "event_type": "verification_failed",
  "verification_id": "ver-20260210-190200-008",
  "operation_id": "dec-20260210-190000-006",
  "failed_checks": ["latency_p95", "error_rate"],
  "outcome": "failure"
}
```

### Rollback Log

```json
{
  "timestamp": "2026-02-10T19:02:05Z",
  "event_type": "rollback_executed",
  "rollback_id": "rb-20260210-190200-001",
  "operation_id": "dec-20260210-190000-006",
  "action": "scale_up",
  "from_replicas": 2,
  "to_replicas": 3,
  "outcome": "executed"
}
```

### Rollback Verification Log

```json
{
  "timestamp": "2026-02-10T19:03:30Z",
  "event_type": "rollback_verified",
  "verification_id": "ver-20260210-190330-009",
  "rollback_id": "rb-20260210-190200-001",
  "outcome": "success",
  "service_restored": true
}
```

**Reference**: See `docs/ROLLBACK_PROCEDURES.md` for complete rollback documentation.

---

## Step 12: Notification

DevOps team is notified of the rollback:

### Slack Notification

```
⚠️ Automatic Rollback Executed: todo-frontend

Original Operation: Scale down from 3 to 2 replicas
Verification: FAILED
Reason: Latency spike (280ms) and error rate increase (1.2%)

Rollback Action: Scaled back to 3 replicas
Rollback Status: ✅ SUCCESS
Service Status: ✅ RESTORED

Metrics After Rollback:
- Latency: 125ms (target: 200ms) ✓
- Error Rate: 0.3% (threshold: 1%) ✓
- CPU: 38% ✓

Recovery Time: 3m 30s

Recommendation: Service requires 3 replicas for current load.
Do not attempt scale-down until load decreases further.

[View Full Details] [Review Metrics]

Operation ID: dec-20260210-190000-006
Rollback ID: rb-20260210-190200-001
```

---

## Timeline Summary

```
19:00:00 - Low CPU detected (35%)
19:00:00 - Decision Engine: Scale down from 3 to 2 replicas
19:00:30 - Governance Enforcer: Operation allowed
19:00:45 - Execution Engine: kubectl scale executed (2.1s)
19:00:47 - Pod terminating
19:01:00 - Stabilization period begins (60s)
19:02:00 - Verification Engine: FAILURE detected
19:02:00 - Latency: 280ms (target: 200ms) ❌
19:02:00 - Error Rate: 1.2% (threshold: 1%) ❌
19:02:00 - Rollback triggered automatically
19:02:05 - Execution Engine: Rollback executed (2.0s)
19:02:07 - New pod starting
19:02:57 - New pod ready (50s startup)
19:03:30 - Verification Engine: Rollback verified ✓
19:03:30 - Service fully restored

Total Duration: 3m 30s (from operation to full recovery)
User Impact: 3m 30s (degraded performance during this period)
```

---

## Key Observations

### Automatic Recovery

✅ **No human intervention required**
- Verification detected failure automatically
- Rollback triggered automatically
- Service restored automatically
- DevOps team notified after recovery

### Fast Recovery

✅ **Service restored in 3.5 minutes**
- Rollback decision: immediate
- Rollback execution: 2 seconds
- Pod startup: 50 seconds
- Metric stabilization: 60 seconds
- Total recovery: 3m 30s

### Safety Mechanism

✅ **Prevented prolonged outage**
- Without rollback: degraded performance continues indefinitely
- With rollback: degraded performance limited to 3.5 minutes
- Automatic recovery reduces MTTR (Mean Time To Recovery)

### Learning Opportunity

✅ **System learns from failure**
- Scale-down to 2 replicas is not viable for current load
- Blueprint can be updated to reflect this
- Future decisions will consider this constraint

---

## Comparison: With vs Without Rollback

### Without Automatic Rollback

```
19:00:45 - Scale down executed
19:02:00 - Verification fails
19:02:00 - Alert sent to DevOps team
19:15:00 - DevOps engineer notices alert (13 minutes later)
19:20:00 - Engineer investigates issue (5 minutes)
19:25:00 - Engineer manually scales back up (5 minutes)
19:26:00 - Service restored

Total Downtime: 25 minutes
User Impact: 25 minutes of degraded performance
```

### With Automatic Rollback

```
19:00:45 - Scale down executed
19:02:00 - Verification fails
19:02:00 - Automatic rollback triggered
19:03:30 - Service restored
19:03:30 - DevOps team notified (after recovery)

Total Downtime: 3.5 minutes
User Impact: 3.5 minutes of degraded performance
```

**Improvement**: 7x faster recovery (25 minutes → 3.5 minutes)

---

## Rollback Scenarios

### Scenario 1: Latency Spike (This Demo)

- **Trigger**: Latency exceeds target
- **Cause**: Insufficient capacity after scale-down
- **Rollback**: Scale back up
- **Recovery**: Immediate

### Scenario 2: Error Rate Increase

- **Trigger**: Error rate exceeds threshold
- **Cause**: Pods overloaded, dropping requests
- **Rollback**: Scale back up
- **Recovery**: Immediate

### Scenario 3: Pod Failures

- **Trigger**: Pods not ready or crashing
- **Cause**: Resource limits too low, OOMKilled
- **Rollback**: Restore previous resource limits
- **Recovery**: Requires pod restart

### Scenario 4: Configuration Error

- **Trigger**: Application errors after config change
- **Cause**: Invalid configuration
- **Rollback**: Restore previous configuration
- **Recovery**: Requires pod restart

---

## Rollback Limitations

### Cannot Rollback

❌ **Rollback not possible for:**
- Data deletion (irreversible)
- External API calls (side effects)
- Database migrations (requires manual rollback)
- Persistent volume deletion (data loss)

### Partial Rollback

⚠️ **May require manual intervention:**
- Multi-step operations (rollback each step)
- Cross-service dependencies (coordinate rollback)
- Stateful applications (data consistency)

---

## Preventing Rollbacks

### Better Capacity Planning

```yaml
# Update blueprint based on learnings
spec:
  scaling:
    min_replicas: 3  # Increased from 1 to 3
    scale_down_threshold: 30%  # Lowered from 40% to 30%
```

### Gradual Scale-Down

```yaml
# Scale down gradually, one replica at a time
decision_engine:
  scaling:
    max_scale_down_step: 1  # Only scale down by 1 replica at a time
    verification_between_steps: true
```

### Load Testing

```bash
# Test scale-down in staging first
kubectl scale deployment todo-frontend --replicas=2 -n staging
# Monitor for 1 hour
# If successful, apply to production
```

---

## Try It Yourself

### Prerequisites

1. Kubernetes cluster with todo-frontend deployed
2. Blueprint with verification and rollback configured
3. Agent system running
4. Monitoring system collecting metrics

### Simulation Steps

```bash
# 1. Check current state
kubectl get deployment todo-frontend -n todo-app

# 2. Trigger scale-down
# (Agent will do this automatically if CPU is low)
# Or manually via API:
curl -X POST http://agent-system/api/operations \
  -d '{"service": "todo-frontend", "operation": "scale_down"}'

# 3. Simulate load spike during verification
kubectl run load-generator --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://todo-frontend:3000; done"

# 4. Watch for rollback
kubectl get pods -n todo-app -l app=todo-frontend -w

# 5. Check audit logs
cat logs/agent-decisions/$(date +%Y-%m-%d)/rollbacks.log | jq '.'

# 6. Verify service restored
kubectl get deployment todo-frontend -n todo-app
# Should be back to original replica count
```

---

## Related Documentation

- **Verification Engine**: `docs/VERIFICATION_ENGINE.md`
- **Rollback Procedures**: `docs/ROLLBACK_PROCEDURES.md`
- **Audit Logging**: `docs/AUDIT_LOGGING.md`
- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`

---

## Next Demo

- **Demo 5**: Multi-Service Management (independent management of multiple services)
