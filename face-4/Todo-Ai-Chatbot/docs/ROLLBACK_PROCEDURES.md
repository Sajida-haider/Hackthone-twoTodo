# Rollback Procedures Documentation

## Overview

Rollback is the automatic recovery mechanism that reverts failed operations to restore system stability. This document explains rollback triggers, procedures for each operation type, and verification steps.

**Key Principle**: When verification fails, rollback quickly to minimize service degradation.

## Rollback Triggers

Rollback is triggered automatically when post-operation verification detects failures.

### Trigger Conditions

1. **Performance Target Violation**
   - Latency exceeds blueprint target (e.g., p95 > 200ms)
   - Throughput falls below minimum threshold
   - Response time degradation detected

2. **Error Rate Increase**
   - Error rate exceeds blueprint threshold (e.g., > 1%)
   - 5xx errors spike
   - Timeout rate increases

3. **Resource Exhaustion**
   - OOMKilled events detected
   - CPU throttling excessive
   - Disk space exhausted

4. **Pod Failures**
   - Pods crash or enter CrashLoopBackOff
   - Readiness probes fail
   - Liveness probes fail

5. **Availability Impact**
   - Replica count below minimum
   - Service unavailable
   - Health check failures

### Trigger Decision Logic

```python
def should_trigger_rollback(verification_result: dict) -> bool:
    """
    Determine if rollback should be triggered.

    Returns True if any critical failure detected.
    """
    # Critical failures that always trigger rollback
    if verification_result['error_rate'] > blueprint['error_rate_max']:
        return True

    if verification_result['latency_p95'] > blueprint['latency_p95_target']:
        return True

    if not verification_result['all_pods_healthy']:
        return True

    if verification_result['availability'] < blueprint['availability_target']:
        return True

    return False
```

## Rollback Procedures by Operation Type

### 1. Scaling Operations

#### Scale Up Rollback

**Scenario**: Scaled from 2 to 3 replicas, but performance degraded

**Rollback Action**: Scale back to 2 replicas

**Procedure**:
```bash
# 1. Scale back to previous replica count
kubectl scale deployment todo-frontend --replicas=2 -n todo-app

# 2. Wait for stabilization (30s)
sleep 30

# 3. Verify rollback
kubectl get deployment todo-frontend -n todo-app
kubectl get pods -l app=todo-frontend -n todo-app
```

**Verification**:
- Replica count == 2
- All pods Running and Ready
- Metrics return to acceptable range

**Rollback Duration**: < 30 seconds

#### Scale Down Rollback

**Scenario**: Scaled from 3 to 2 replicas, latency spiked

**Rollback Action**: Scale back to 3 replicas

**Procedure**:
```bash
# 1. Scale back to previous replica count
kubectl scale deployment todo-frontend --replicas=3 -n todo-app

# 2. Wait for new pod to start (60s)
sleep 60

# 3. Verify rollback
kubectl get deployment todo-frontend -n todo-app
kubectl get pods -l app=todo-frontend -n todo-app
```

**Verification**:
- Replica count == 3
- All 3 pods Running and Ready
- Latency returns to < 200ms
- Error rate returns to < 1%

**Rollback Duration**: < 60 seconds

### 2. Resource Changes

#### CPU/Memory Request Rollback

**Scenario**: Reduced CPU request from 100m to 43m, pods OOMKilled

**Rollback Action**: Restore previous resource requests

**Procedure**:
```bash
# 1. Restore previous resource requests
kubectl set resources deployment todo-frontend \
  --requests=cpu=100m,memory=128Mi \
  -n todo-app

# 2. Wait for pods to restart with new resources (60s)
sleep 60

# 3. Verify rollback
kubectl get deployment todo-frontend -n todo-app -o yaml | grep -A 5 resources
kubectl get pods -l app=todo-frontend -n todo-app
```

**Verification**:
- Resource requests restored to previous values
- All pods Running and Ready
- No OOMKilled events
- Performance metrics stable

**Rollback Duration**: < 60 seconds

#### Resource Limit Rollback

**Scenario**: Increased CPU limit, caused unexpected behavior

**Rollback Action**: Restore previous resource limits

**Procedure**:
```bash
# 1. Restore previous resource limits
kubectl set resources deployment todo-frontend \
  --limits=cpu=200m,memory=512Mi \
  -n todo-app

# 2. Wait for pods to restart (60s)
sleep 60

# 3. Verify rollback
kubectl get deployment todo-frontend -n todo-app -o yaml | grep -A 5 resources
```

**Verification**:
- Resource limits restored
- Pods stable
- No throttling issues

**Rollback Duration**: < 60 seconds

### 3. Configuration Changes

#### ConfigMap Rollback

**Scenario**: Updated ConfigMap, application behavior changed unexpectedly

**Rollback Action**: Restore previous ConfigMap version

**Procedure**:
```bash
# 1. Restore previous ConfigMap
kubectl apply -f configmap-backup.yaml -n todo-app

# 2. Restart pods to pick up old config (30s)
kubectl rollout restart deployment/todo-frontend -n todo-app

# 3. Wait for rollout to complete (60s)
kubectl rollout status deployment/todo-frontend -n todo-app

# 4. Verify rollback
kubectl get configmap todo-frontend-config -n todo-app -o yaml
```

**Verification**:
- ConfigMap restored to previous version
- Pods restarted successfully
- Application behavior normal

**Rollback Duration**: < 90 seconds

### 4. Deployment Updates

#### Image Version Rollback

**Scenario**: Deployed new image version, errors increased

**Rollback Action**: Rollback to previous deployment revision

**Procedure**:
```bash
# 1. Rollback deployment to previous revision
kubectl rollout undo deployment/todo-frontend -n todo-app

# 2. Wait for rollout to complete (120s)
kubectl rollout status deployment/todo-frontend -n todo-app

# 3. Verify rollback
kubectl rollout history deployment/todo-frontend -n todo-app
kubectl get pods -l app=todo-frontend -n todo-app
```

**Verification**:
- Deployment rolled back to previous revision
- All pods Running with old image
- Error rate returns to normal
- Performance metrics stable

**Rollback Duration**: < 120 seconds

#### Deployment Strategy Rollback

**Scenario**: Changed maxSurge/maxUnavailable, caused availability issues

**Rollback Action**: Restore previous deployment strategy

**Procedure**:
```bash
# 1. Restore previous deployment strategy
kubectl patch deployment todo-frontend -n todo-app --patch '
spec:
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
'

# 2. Verify strategy restored
kubectl get deployment todo-frontend -n todo-app -o yaml | grep -A 5 strategy
```

**Verification**:
- Deployment strategy restored
- No immediate impact (takes effect on next update)

**Rollback Duration**: < 5 seconds

### 5. Health Check Changes

#### Probe Configuration Rollback

**Scenario**: Modified readiness probe, pods marked unready

**Rollback Action**: Restore previous probe configuration

**Procedure**:
```bash
# 1. Restore previous probe configuration
kubectl patch deployment todo-frontend -n todo-app --patch '
spec:
  template:
    spec:
      containers:
      - name: frontend
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
'

# 2. Wait for pods to restart (60s)
kubectl rollout status deployment/todo-frontend -n todo-app

# 3. Verify rollback
kubectl get deployment todo-frontend -n todo-app -o yaml | grep -A 10 readinessProbe
```

**Verification**:
- Probe configuration restored
- Pods pass readiness checks
- All pods Ready

**Rollback Duration**: < 60 seconds

## Rollback Verification

After executing rollback, verify that the system has returned to a stable state.

### Verification Checklist

1. **Resource State**
   - [ ] Replica count matches pre-operation state
   - [ ] All pods Running and Ready
   - [ ] No CrashLoopBackOff or Error states

2. **Performance Metrics**
   - [ ] CPU utilization within acceptable range
   - [ ] Memory utilization within acceptable range
   - [ ] Latency meets blueprint target
   - [ ] Error rate below threshold

3. **Health Checks**
   - [ ] Readiness probes passing
   - [ ] Liveness probes passing
   - [ ] No pod restarts

4. **Stability**
   - [ ] Metrics stable for 60 seconds
   - [ ] No new errors or warnings
   - [ ] Service responding normally

### Verification Timeline

```
[Rollback Executed]
        ↓
[Wait 30-60s for Stabilization]
        ↓
[Collect Post-Rollback Metrics]
        ↓
[Compare to Pre-Operation State]
        ↓
    ┌───┴───┐
    │       │
[Success] [Failure]
    │       │
[Log]   [Escalate]
    │       │
[Done]  [Manual Intervention]
```

## Rollback Failure Handling

If rollback itself fails, escalate to manual intervention.

### Rollback Failure Scenarios

1. **Insufficient Cluster Capacity**
   - Cannot scale up due to resource constraints
   - **Action**: Alert on-call team, request capacity increase

2. **Image Pull Failure**
   - Cannot pull previous image version
   - **Action**: Verify image registry, check credentials

3. **Configuration Conflict**
   - ConfigMap or Secret missing
   - **Action**: Restore from backup, recreate resources

4. **Persistent Failure**
   - Rollback completes but issues persist
   - **Action**: Investigate root cause, may require deeper rollback

### Escalation Procedure

```json
{
  "escalation_trigger": "rollback_failed",
  "severity": "critical",
  "actions": [
    "Alert on-call team immediately",
    "Create incident ticket",
    "Provide rollback failure details",
    "Suggest manual intervention steps",
    "Monitor system continuously"
  ],
  "notification_channels": [
    "slack://devops-alerts",
    "pagerduty://devops-oncall",
    "email://devops-team@example.com"
  ]
}
```

## Rollback Logging

All rollback operations are logged for audit and analysis.

### Rollback Log Format

```json
{
  "timestamp": "2026-02-10T16:52:30Z",
  "event_type": "rollback_triggered",
  "rollback_id": "rbk-20260210-165230-001",
  "operation_id": "dec-20260210-164500-007",
  "service": "todo-frontend",
  "trigger_reason": "verification_failed",
  "trigger_conditions": [
    "latency_p95 (280ms) > target (200ms)",
    "error_rate (1.2%) > threshold (1%)"
  ],
  "rollback_action": "scale_up",
  "rollback_target": "3 replicas",
  "rollback_command": "kubectl scale deployment todo-frontend --replicas=3",
  "rollback_status": "success",
  "rollback_duration": "65s",
  "post_rollback_metrics": {
    "latency_p95": 145,
    "error_rate": 0.004
  }
}
```

## Best Practices

### For Agents

1. **Trigger Quickly**: Don't wait for prolonged degradation
2. **Verify Thoroughly**: Ensure rollback succeeded
3. **Log Everything**: Complete audit trail of rollback
4. **Learn from Failures**: Update decision logic based on rollback patterns

### For Operators

1. **Monitor Rollbacks**: Track rollback frequency and causes
2. **Investigate Patterns**: Frequent rollbacks indicate issues
3. **Update Blueprints**: Adjust targets if rollbacks are too aggressive
4. **Review Logs**: Understand why operations failed

### For Blueprint Authors

1. **Set Realistic Targets**: Avoid overly strict thresholds
2. **Define Clear Rollback Triggers**: Specify what constitutes failure
3. **Test Rollback Procedures**: Verify rollback works in staging
4. **Document Exceptions**: Note cases where rollback may not work

## Rollback Metrics

### Key Metrics to Track

- **Rollback Rate**: Percentage of operations requiring rollback
- **Rollback Success Rate**: Percentage of successful rollbacks
- **Rollback Duration**: Time from trigger to completion
- **Service Degradation Time**: Time system was degraded before rollback
- **Rollback Failure Rate**: Percentage of failed rollbacks

### Target Metrics

- Rollback Rate: < 5% (most operations should succeed)
- Rollback Success Rate: > 95% (rollback should be reliable)
- Rollback Duration: < 60 seconds (fast recovery)
- Service Degradation Time: < 5 minutes (minimize impact)
- Rollback Failure Rate: < 1% (rollback should rarely fail)

## Troubleshooting

### Problem: Rollback triggered too frequently

**Causes**:
- Blueprint targets too strict
- Verification checks too sensitive
- System naturally variable

**Solutions**:
- Review and adjust blueprint targets
- Add tolerance ranges to verification checks
- Increase stabilization period before verification

### Problem: Rollback takes too long

**Causes**:
- Slow pod startup times
- Image pull delays
- Resource constraints

**Solutions**:
- Optimize container images
- Use image pull policies effectively
- Ensure sufficient cluster capacity

### Problem: Rollback doesn't restore stability

**Causes**:
- Root cause not addressed by rollback
- External dependency issues
- Configuration drift

**Solutions**:
- Investigate root cause
- Check external dependencies
- Verify configuration consistency

## See Also

- [Verification Engine Documentation](./VERIFICATION_ENGINE.md) - How verification triggers rollback
- [Decision Engine Documentation](./DECISION_ENGINE.md) - How decisions are made
- [Audit Logging Documentation](./AUDIT_LOGGING.md) - How rollbacks are logged
