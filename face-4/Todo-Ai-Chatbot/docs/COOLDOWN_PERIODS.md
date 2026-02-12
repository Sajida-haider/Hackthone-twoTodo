# Cooldown Period Documentation

## Overview

Cooldown periods are safety mechanisms that enforce minimum time intervals between operations. They prevent rapid oscillation (scale up → scale down → scale up) and allow the system to stabilize before making new decisions.

**Key Principle**: Give the system time to stabilize before making another change.

## Purpose

Cooldown periods serve multiple purposes:

1. **Prevent Oscillation**: Stop rapid back-and-forth changes
2. **Allow Stabilization**: Give metrics time to reflect operation impact
3. **Reduce Churn**: Minimize unnecessary operations
4. **Improve Stability**: Ensure system reaches steady state

## How Cooldown Works

### Basic Logic

```
[Operation Executed]
        ↓
[Record Timestamp]
        ↓
[Start Cooldown Timer]
        ↓
    ┌───┴───┐
    │       │
[Time < Cooldown] [Time ≥ Cooldown]
    │                   │
[Block Operation]   [Allow Operation]
```

### Cooldown Enforcement

```python
class CooldownEnforcer:
    """
    Enforce cooldown periods between operations.
    """

    def __init__(self, blueprint: dict):
        self.cooldown_period = blueprint['spec']['scaling']['cooldown_period']
        self.last_operation_time = None
        self.last_operation_type = None

    def can_execute(self, operation: dict) -> dict:
        """
        Check if operation can execute based on cooldown.

        Args:
            operation: Proposed operation

        Returns:
            Dictionary with allowed status and reason
        """
        # No previous operation - allow
        if self.last_operation_time is None:
            return {
                'allowed': True,
                'reason': 'no_previous_operation',
                'cooldown_elapsed': True
            }

        # Calculate time since last operation
        current_time = get_current_timestamp()
        time_elapsed = current_time - self.last_operation_time

        # Check if cooldown period has elapsed
        if time_elapsed >= self.cooldown_period:
            return {
                'allowed': True,
                'reason': 'cooldown_elapsed',
                'cooldown_elapsed': True,
                'time_elapsed': time_elapsed,
                'cooldown_required': self.cooldown_period
            }
        else:
            return {
                'allowed': False,
                'reason': 'cooldown_not_elapsed',
                'cooldown_elapsed': False,
                'time_elapsed': time_elapsed,
                'cooldown_required': self.cooldown_period,
                'time_remaining': self.cooldown_period - time_elapsed
            }

    def record_operation(self, operation: dict) -> None:
        """
        Record operation execution and start cooldown timer.

        Args:
            operation: Executed operation
        """
        self.last_operation_time = get_current_timestamp()
        self.last_operation_type = operation['type']

        log_event({
            'event_type': 'cooldown_started',
            'timestamp': self.last_operation_time,
            'operation_type': operation['type'],
            'cooldown_period': self.cooldown_period
        })
```

## Configuration

### Blueprint Configuration

```yaml
spec:
  scaling:
    cooldown_period: 60s    # 60 second cooldown between operations
```

### Cooldown Duration Guidelines

| Service Type | Recommended Cooldown | Rationale |
|--------------|---------------------|-----------|
| Frontend (stateless) | 60s | Fast startup, quick stabilization |
| Backend (stateless) | 90s | May have connection pools to warm up |
| Database | 180s | Slow startup, needs time to stabilize |
| Cache | 120s | Needs time to warm up cache |
| Message Queue | 60s | Fast startup, quick stabilization |

### Tuning Cooldown Period

**Too Short (< 30s)**:
- Risk of oscillation
- Metrics may not reflect operation impact
- Increased operational churn

**Too Long (> 300s)**:
- Slow response to load changes
- May miss scaling opportunities
- Reduced system responsiveness

**Optimal (60-120s)**:
- Balances stability and responsiveness
- Allows metrics to stabilize
- Prevents oscillation

## Cooldown Scenarios

### Scenario 1: Cooldown Prevents Oscillation

**Timeline**:
```
15:30:00 - Scale up from 2 to 3 replicas (CPU 85%)
15:30:45 - CPU drops to 55% (load distributed)
15:31:00 - Decision Engine: "CPU 55% < 80%, should scale down"
15:31:00 - Cooldown Check: BLOCKED (only 60s elapsed, need 60s)
15:31:30 - Decision Engine: "CPU still 55%, should scale down"
15:31:30 - Cooldown Check: ALLOWED (90s elapsed > 60s required)
15:31:30 - Scale down from 3 to 2 replicas
```

**Without Cooldown**:
```
15:30:00 - Scale up to 3 replicas
15:30:45 - Scale down to 2 replicas (oscillation!)
15:31:30 - Scale up to 3 replicas (oscillation!)
15:32:15 - Scale down to 2 replicas (oscillation!)
```

### Scenario 2: Cooldown Allows Stabilization

**Timeline**:
```
16:00:00 - Scale up from 2 to 3 replicas
16:00:00 - Cooldown starts (60s)
16:00:30 - New pod starting (not ready yet)
16:00:45 - New pod ready, receiving traffic
16:01:00 - Metrics stabilize, cooldown elapsed
16:01:00 - Next operation can proceed if needed
```

**Benefit**: Metrics at 16:01:00 accurately reflect the impact of scaling to 3 replicas.

### Scenario 3: Cooldown Defers Non-Urgent Operation

**Timeline**:
```
17:00:00 - Scale up from 2 to 3 replicas (high load)
17:00:30 - Decision Engine: "CPU 60%, could optimize resources"
17:00:30 - Cooldown Check: BLOCKED (30s elapsed, need 60s)
17:00:30 - Operation deferred (not urgent)
17:01:00 - Cooldown elapsed
17:01:00 - Decision Engine re-evaluates: "CPU still 60%, optimize"
17:01:00 - Resource optimization proceeds
```

**Benefit**: Non-urgent optimization waits for system to stabilize.

## Cooldown vs. Other Safety Mechanisms

### Cooldown vs. Circuit Breaker

| Aspect | Cooldown | Circuit Breaker |
|--------|----------|-----------------|
| Purpose | Prevent rapid changes | Stop after failures |
| Trigger | Time-based | Failure-based |
| Duration | Fixed (60s) | Variable (1h+) |
| Reset | Automatic | Manual |
| Severity | Low | High |

### Cooldown vs. Rate Limiting

| Aspect | Cooldown | Rate Limiting |
|--------|----------|---------------|
| Scope | Per service | Global |
| Measure | Time between ops | Ops per hour/day |
| Purpose | Stabilization | Prevent excessive automation |
| Enforcement | Between operations | Across operations |

## Cooldown Bypass

In rare cases, cooldown may need to be bypassed for urgent operations.

### Bypass Criteria

Cooldown can be bypassed if:
1. **Critical Failure**: Service is down or severely degraded
2. **Manual Override**: Human operator explicitly bypasses
3. **Emergency Scaling**: Extreme load requires immediate action

### Bypass Logic

```python
def can_bypass_cooldown(operation: dict, current_state: dict) -> bool:
    """
    Determine if cooldown can be bypassed.

    Returns True only for critical situations.
    """
    # Check for critical failure
    if current_state['availability'] < 0.90:  # < 90% availability
        return True

    # Check for extreme load
    if current_state['cpu_utilization'] > 0.95:  # > 95% CPU
        return True

    # Check for manual override
    if operation.get('bypass_cooldown') and operation.get('authorized_by'):
        return True

    return False
```

### Bypass Logging

All cooldown bypasses are logged for audit:

```json
{
  "timestamp": "2026-02-10T18:00:00Z",
  "event_type": "cooldown_bypassed",
  "operation_id": "dec-20260210-180000-001",
  "bypass_reason": "critical_failure",
  "current_availability": 0.85,
  "authorized_by": "system_automatic",
  "cooldown_remaining": "45s"
}
```

## Cooldown Monitoring

### Key Metrics

- **Cooldown Blocks**: Number of operations blocked by cooldown
- **Cooldown Bypasses**: Number of cooldown bypasses
- **Average Time Between Operations**: Actual time between operations
- **Cooldown Effectiveness**: Reduction in oscillation

### Monitoring Dashboard

```
Cooldown Status
├── Last Operation: 2026-02-10T17:30:00Z (scale_up)
├── Cooldown Period: 60s
├── Time Elapsed: 45s
├── Time Remaining: 15s
└── Next Operation Allowed: 2026-02-10T17:31:00Z

Recent Activity (1h)
├── Operations Executed: 3
├── Operations Blocked: 2 (cooldown)
├── Cooldown Bypasses: 0
└── Average Time Between Ops: 18 minutes
```

## Cooldown Tuning

### Signs Cooldown is Too Short

- Frequent oscillation (scale up/down/up)
- Operations execute before metrics stabilize
- High operational churn
- Metrics show instability

**Solution**: Increase cooldown period (e.g., 60s → 90s)

### Signs Cooldown is Too Long

- Slow response to load changes
- System remains overloaded during cooldown
- Missed scaling opportunities
- User experience degraded

**Solution**: Decrease cooldown period (e.g., 90s → 60s)

### Optimal Cooldown

Optimal cooldown balances:
- Fast enough to respond to load changes
- Slow enough to prevent oscillation
- Allows metrics to stabilize
- Matches pod startup time

**Formula**: `cooldown_period ≥ pod_startup_time + metric_collection_interval`

**Example**:
- Pod startup time: 30s
- Metric collection interval: 15s
- Minimum cooldown: 45s
- Recommended cooldown: 60s (with buffer)

## Best Practices

1. **Set Appropriate Cooldown**: Match pod startup time and metric collection
2. **Monitor Oscillation**: Track scale up/down patterns
3. **Log Cooldown Blocks**: Understand when operations are deferred
4. **Rare Bypasses**: Cooldown bypass should be exceptional
5. **Tune Based on Behavior**: Adjust cooldown based on observed patterns

## Troubleshooting

### Problem: Operations blocked too frequently

**Causes**:
- Cooldown too long
- Operations triggered too frequently
- Decision logic too aggressive

**Solutions**:
- Reduce cooldown period
- Adjust decision thresholds
- Review decision logic

### Problem: Oscillation still occurring

**Causes**:
- Cooldown too short
- Metrics not stabilizing
- Decision thresholds too tight

**Solutions**:
- Increase cooldown period
- Increase metric collection interval
- Widen decision threshold gap

### Problem: Slow response to load spikes

**Causes**:
- Cooldown too long
- No bypass for critical situations

**Solutions**:
- Reduce cooldown period
- Implement cooldown bypass for critical failures
- Use faster pod startup times

## See Also

- [Decision Engine Documentation](./DECISION_ENGINE.md) - How decisions respect cooldown
- [Circuit Breaker Documentation](./CIRCUIT_BREAKER.md) - Related safety mechanism
- [Governance Documentation](./GOVERNANCE.md) - Safety mechanisms overview
