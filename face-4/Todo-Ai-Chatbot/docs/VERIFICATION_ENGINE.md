# Verification Engine Documentation

## Overview

The Verification Engine is the agent responsible for validating that operations achieved their intended outcomes and meet blueprint targets. It runs post-execution checks, detects failures, and triggers rollbacks when necessary.

**Key Responsibility**: Ensure operations had the intended effect and blueprint targets are met.

## Verification Architecture

```
Operation Executed
        ↓
[Wait for Stabilization]
        ↓
[Collect Post-Operation Metrics]
        ↓
[Compare to Blueprint Targets]
        ↓
    ┌───┴───┐
    │       │
[Pass]   [Fail]
    │       │
[Log]  [Trigger Rollback]
    │       │
[Done]  [Verify Rollback]
            │
        [Done]
```

## Verification Timeline

Operations are verified at multiple time intervals to ensure both immediate success and sustained stability.

### Immediate Verification (0-10s)

**Purpose**: Confirm operation executed without errors

**Checks**:
- Command executed successfully (exit code 0)
- No kubectl/API errors
- Resources created/updated as expected
- No immediate failures

**Example**:
```
Operation: kubectl scale deployment todo-frontend --replicas=3
Immediate Check: Deployment scaled successfully, no errors
```

### Short-Term Verification (10-60s)

**Purpose**: Confirm resources reached desired state

**Checks**:
- Pods reach Running state
- Readiness probes pass
- Liveness probes pass
- No crash loops
- Replica count matches target

**Example**:
```
Operation: Scale to 3 replicas
Short-Term Check: 3 pods Running and Ready
```

### Medium-Term Verification (60-300s)

**Purpose**: Confirm performance targets are met

**Checks**:
- CPU utilization within target range
- Memory utilization within target range
- Latency meets blueprint target (p95 < target)
- Error rate below threshold
- No pod restarts

**Example**:
```
Operation: Scale to 3 replicas
Medium-Term Check: CPU 60% (target 70%), latency 150ms (target 200ms)
```

### Long-Term Monitoring (5m+)

**Purpose**: Confirm sustained stability

**Checks**:
- Metrics remain within targets over time
- No degradation or drift
- No unexpected side effects
- System stable

**Example**:
```
Operation: Scale to 3 replicas
Long-Term Check: Metrics stable for 10 minutes, no issues
```

## Verification Criteria by Operation Type

### Scaling Operations

**Pre-Operation State**:
```json
{
  "replicas": 2,
  "cpu_utilization": 0.85,
  "memory_utilization": 0.70,
  "latency_p95": 180,
  "error_rate": 0.005
}
```

**Operation**: Scale from 2 to 3 replicas

**Post-Operation Verification**:

1. **Replica Count Check**
   - Expected: 3 replicas
   - Actual: `kubectl get deployment -o jsonpath='{.status.replicas}'`
   - Pass: Actual == Expected

2. **Pod Status Check**
   - Expected: All 3 pods Running and Ready
   - Actual: `kubectl get pods -l app=todo-frontend`
   - Pass: All pods status == Running, Ready == True

3. **CPU Utilization Check**
   - Expected: ~57% (85% / 1.5 = 57%)
   - Actual: Current CPU utilization
   - Pass: Within ±10% of expected (51-63%)

4. **Memory Utilization Check**
   - Expected: ~47% (70% / 1.5 = 47%)
   - Actual: Current memory utilization
   - Pass: Within ±10% of expected (42-52%)

5. **Latency Check**
   - Expected: < 200ms (blueprint target)
   - Actual: Current p95 latency
   - Pass: Actual < Target

6. **Error Rate Check**
   - Expected: < 1% (blueprint target)
   - Actual: Current error rate
   - Pass: Actual < Target

**Verification Result**:
```json
{
  "verification_id": "ver-20260210-153200-001",
  "operation_id": "dec-20260210-153045-001",
  "verification_status": "passed",
  "checks": {
    "replica_count": {"expected": 3, "actual": 3, "passed": true},
    "pod_status": {"expected": "3 Running", "actual": "3 Running", "passed": true},
    "cpu_utilization": {"expected": 0.57, "actual": 0.60, "passed": true},
    "memory_utilization": {"expected": 0.47, "actual": 0.50, "passed": true},
    "latency_p95": {"expected": "<200ms", "actual": 150, "passed": true},
    "error_rate": {"expected": "<1%", "actual": 0.004, "passed": true}
  },
  "all_checks_passed": true
}
```

### Resource Optimization Operations

**Pre-Operation State**:
```json
{
  "cpu_request": "100m",
  "cpu_usage": "30m",
  "memory_request": "128Mi",
  "memory_usage": "100Mi"
}
```

**Operation**: Reduce CPU request from 100m to 43m

**Post-Operation Verification**:

1. **Resource Request Check**
   - Expected: CPU request == 43m
   - Actual: `kubectl get deployment -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}'`
   - Pass: Actual == Expected

2. **Pod Restart Check**
   - Expected: Pods restarted successfully
   - Actual: All pods Running with new resource requests
   - Pass: All pods Running, no CrashLoopBackOff

3. **CPU Usage Check**
   - Expected: ~30m (same as before)
   - Actual: Current CPU usage
   - Pass: Within ±20% of expected (24-36m)

4. **CPU Utilization Check**
   - Expected: ~70% (30m / 43m = 70%)
   - Actual: Current CPU utilization
   - Pass: Within target range (60-80%)

5. **No OOMKilled Check**
   - Expected: No OOMKilled events
   - Actual: Check pod events
   - Pass: No OOMKilled events

6. **Performance Check**
   - Expected: Latency still meets target
   - Actual: Current p95 latency
   - Pass: Latency < blueprint target

**Verification Result**:
```json
{
  "verification_id": "ver-20260210-154300-002",
  "operation_id": "dec-20260210-154230-002",
  "verification_status": "passed",
  "checks": {
    "resource_request": {"expected": "43m", "actual": "43m", "passed": true},
    "pod_restart": {"expected": "success", "actual": "success", "passed": true},
    "cpu_usage": {"expected": 30, "actual": 32, "passed": true},
    "cpu_utilization": {"expected": 0.70, "actual": 0.74, "passed": true},
    "no_oomkilled": {"expected": false, "actual": false, "passed": true},
    "latency_p95": {"expected": "<200ms", "actual": 160, "passed": true}
  },
  "all_checks_passed": true
}
```

### Failure Recovery Operations

**Pre-Operation State**:
```json
{
  "pod_name": "todo-frontend-7d8f9c5b6-xk2m9",
  "pod_status": "CrashLoopBackOff",
  "restart_count": 2
}
```

**Operation**: Restart pod

**Post-Operation Verification**:

1. **Pod Status Check**
   - Expected: Pod status == Running
   - Actual: `kubectl get pod {pod_name} -o jsonpath='{.status.phase}'`
   - Pass: Actual == Running

2. **Readiness Check**
   - Expected: Readiness probe passing
   - Actual: Pod Ready condition
   - Pass: Ready == True

3. **Liveness Check**
   - Expected: Liveness probe passing
   - Actual: Pod liveness status
   - Pass: No liveness failures

4. **No Immediate Crash Check**
   - Expected: Pod stays running for 60s
   - Actual: Pod status after 60s
   - Pass: Still Running after 60s

5. **Restart Count Check**
   - Expected: RestartCount not increasing
   - Actual: Current RestartCount
   - Pass: RestartCount stable

**Verification Result**:
```json
{
  "verification_id": "ver-20260210-160900-003",
  "operation_id": "dec-20260210-160815-003",
  "verification_status": "passed",
  "checks": {
    "pod_status": {"expected": "Running", "actual": "Running", "passed": true},
    "readiness": {"expected": true, "actual": true, "passed": true},
    "liveness": {"expected": true, "actual": true, "passed": true},
    "no_crash": {"expected": "stable", "actual": "stable", "passed": true},
    "restart_count": {"expected": "stable", "actual": 0, "passed": true}
  },
  "all_checks_passed": true
}
```

## Rollback Triggers

The Verification Engine triggers automatic rollback when verification fails.

### Rollback Trigger Conditions

1. **Target Violation**: Post-operation metrics violate blueprint targets
2. **Performance Degradation**: Latency increases beyond acceptable range
3. **Error Rate Increase**: Error rate exceeds threshold
4. **Pod Failures**: Pods crash or fail health checks
5. **Resource Exhaustion**: OOMKilled or CPU throttling detected

### Rollback Decision Logic

```python
def should_trigger_rollback(
    verification_result: dict,
    blueprint_targets: dict
) -> dict:
    """
    Determine if rollback should be triggered based on verification result.

    Args:
        verification_result: Post-operation verification checks
        blueprint_targets: Blueprint performance targets

    Returns:
        Rollback decision with trigger reason
    """
    # Check if any critical checks failed
    critical_failures = []

    # Check 1: Latency exceeds target
    if verification_result['latency_p95'] > blueprint_targets['latency_p95']:
        critical_failures.append({
            'check': 'latency_p95',
            'expected': f"< {blueprint_targets['latency_p95']}ms",
            'actual': f"{verification_result['latency_p95']}ms",
            'severity': 'high'
        })

    # Check 2: Error rate exceeds threshold
    if verification_result['error_rate'] > blueprint_targets['error_rate_max']:
        critical_failures.append({
            'check': 'error_rate',
            'expected': f"< {blueprint_targets['error_rate_max']}",
            'actual': f"{verification_result['error_rate']}",
            'severity': 'critical'
        })

    # Check 3: Pods not healthy
    if not verification_result['all_pods_healthy']:
        critical_failures.append({
            'check': 'pod_health',
            'expected': 'all pods healthy',
            'actual': 'some pods unhealthy',
            'severity': 'critical'
        })

    # Trigger rollback if any critical failures
    if critical_failures:
        return {
            'trigger_rollback': True,
            'reason': 'verification_failed',
            'failures': critical_failures,
            'rationale': 'Post-operation metrics violate blueprint targets. Triggering automatic rollback.'
        }
    else:
        return {
            'trigger_rollback': False,
            'reason': 'all_checks_passed',
            'rationale': 'All verification checks passed. Operation successful.'
        }
```

### Rollback Execution

When rollback is triggered:

1. **Log Rollback Decision**
   - Record verification failure
   - Document trigger reason
   - Reference blueprint targets

2. **Execute Rollback**
   - Revert to pre-operation state
   - Use appropriate rollback command
   - Monitor rollback progress

3. **Verify Rollback**
   - Confirm rollback succeeded
   - Verify metrics return to acceptable range
   - Log rollback outcome

**Rollback Example**:
```json
{
  "rollback_id": "rbk-20260210-161000-001",
  "triggered_by": "verification-engine-001",
  "trigger_reason": "latency_exceeds_target",
  "operation_id": "dec-20260210-160500-006",
  "rollback_action": "scale_down",
  "rollback_command": "kubectl scale deployment todo-frontend --replicas=2 -n todo-app",
  "rollback_executed_at": "2026-02-10T16:10:00Z",
  "rollback_verified_at": "2026-02-10T16:11:00Z",
  "rollback_status": "success",
  "post_rollback_metrics": {
    "replicas": 2,
    "latency_p95": 180,
    "error_rate": 0.005
  }
}
```

## Verification Failure Examples

### Example 1: Latency Violation

**Operation**: Scale down from 3 to 2 replicas

**Verification Result**:
```json
{
  "verification_status": "failed",
  "failed_checks": [
    {
      "check": "latency_p95",
      "expected": "< 200ms",
      "actual": "280ms",
      "passed": false,
      "severity": "high"
    }
  ],
  "rollback_triggered": true,
  "rollback_reason": "Latency (280ms) exceeds blueprint target (200ms)"
}
```

**Rollback Action**: Scale back to 3 replicas

### Example 2: Pod Crash

**Operation**: Update resource requests

**Verification Result**:
```json
{
  "verification_status": "failed",
  "failed_checks": [
    {
      "check": "pod_health",
      "expected": "all pods Running",
      "actual": "1 pod CrashLoopBackOff",
      "passed": false,
      "severity": "critical"
    }
  ],
  "rollback_triggered": true,
  "rollback_reason": "Pod crashed after resource update (OOMKilled)"
}
```

**Rollback Action**: Revert resource requests to previous values

### Example 3: Error Rate Spike

**Operation**: Deploy new version

**Verification Result**:
```json
{
  "verification_status": "failed",
  "failed_checks": [
    {
      "check": "error_rate",
      "expected": "< 1%",
      "actual": "5.2%",
      "passed": false,
      "severity": "critical"
    }
  ],
  "rollback_triggered": true,
  "rollback_reason": "Error rate (5.2%) exceeds blueprint threshold (1%)"
}
```

**Rollback Action**: Rollback deployment to previous revision

## Stabilization Period

Before verification, the system waits for a stabilization period to allow metrics to settle.

### Stabilization Duration by Operation Type

| Operation Type | Stabilization Period | Rationale |
|----------------|---------------------|-----------|
| Scaling | 60 seconds | Pods need time to start and receive traffic |
| Resource Changes | 60 seconds | Pods restart, need time to stabilize |
| Configuration Updates | 30 seconds | ConfigMap changes applied quickly |
| Deployment Updates | 120 seconds | Rolling update takes time to complete |

### Stabilization Logic

```python
def wait_for_stabilization(operation_type: str) -> int:
    """
    Return stabilization period in seconds for operation type.
    """
    stabilization_periods = {
        'scale_up': 60,
        'scale_down': 60,
        'adjust_resources': 60,
        'update_config': 30,
        'deploy_update': 120,
        'restart_pod': 30
    }
    return stabilization_periods.get(operation_type, 60)
```

## Verification Logging

All verification results are logged for audit and analysis.

### Verification Log Format

```json
{
  "timestamp": "2026-02-10T15:32:00Z",
  "event_type": "verification_completed",
  "verification_id": "ver-20260210-153200-001",
  "operation_id": "dec-20260210-153045-001",
  "service": "todo-frontend",
  "operation_type": "scale_up",
  "verification_status": "passed",
  "checks_performed": 6,
  "checks_passed": 6,
  "checks_failed": 0,
  "verification_duration": "62s",
  "rollback_triggered": false
}
```

## Best Practices

1. **Wait for Stabilization**: Always wait for stabilization period before verification
2. **Multiple Checks**: Verify multiple metrics, not just one
3. **Clear Thresholds**: Define clear pass/fail criteria in blueprint
4. **Fast Rollback**: Trigger rollback quickly when verification fails
5. **Verify Rollback**: Always verify that rollback succeeded

## See Also

- [Decision Engine Documentation](./DECISION_ENGINE.md) - How decisions are made
- [Governance Documentation](./GOVERNANCE.md) - How operations are authorized
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md) - Detailed rollback steps
