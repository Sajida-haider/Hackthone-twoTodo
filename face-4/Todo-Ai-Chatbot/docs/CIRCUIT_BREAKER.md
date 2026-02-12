# Circuit Breaker Documentation

## Overview

The Circuit Breaker is a safety mechanism that prevents runaway automation by stopping agent operations after consecutive failures. It acts as an automatic "kill switch" that requires manual intervention to reset.

**Key Principle**: Stop automation when it's causing harm, require human review before resuming.

## Circuit Breaker States

The circuit breaker operates in three states:

```
[CLOSED] ──failure──> [OPEN] ──timeout──> [HALF-OPEN] ──success──> [CLOSED]
   │                     │                      │
   │                     │                      └──failure──> [OPEN]
   └──< 3 failures───────┘
```

### State 1: CLOSED (Normal Operation)

**Description**: Circuit is closed, operations flow normally

**Behavior**:
- Agents can execute operations autonomously
- Failures are counted but don't block operations
- System operates normally

**Transition to OPEN**:
- When consecutive failures reach threshold (default: 3)
- Failure window: 5 minutes (only count recent failures)

**Example**:
```json
{
  "state": "closed",
  "consecutive_failures": 0,
  "failure_threshold": 3,
  "operations_allowed": true
}
```

### State 2: OPEN (Circuit Tripped)

**Description**: Circuit is open, operations are blocked

**Behavior**:
- All agent operations are blocked
- Agents cannot execute any operations
- Manual intervention required to reset
- System enters "safe mode"

**Transition to HALF-OPEN**:
- After reset timeout (default: 1 hour)
- Allows one test operation to check if issue resolved

**Example**:
```json
{
  "state": "open",
  "consecutive_failures": 3,
  "failure_threshold": 3,
  "operations_allowed": false,
  "opened_at": "2026-02-10T17:00:00Z",
  "reset_timeout": "1h",
  "manual_reset_required": true
}
```

### State 3: HALF-OPEN (Testing)

**Description**: Circuit is testing if system has recovered

**Behavior**:
- One test operation allowed
- If test succeeds: transition to CLOSED
- If test fails: transition back to OPEN
- Limited operations to test recovery

**Transition to CLOSED**:
- Test operation succeeds
- System appears healthy

**Transition to OPEN**:
- Test operation fails
- System still unhealthy

**Example**:
```json
{
  "state": "half_open",
  "consecutive_failures": 0,
  "test_operation_allowed": true,
  "operations_allowed": false
}
```

## Circuit Breaker Logic

### Failure Counting

```python
class CircuitBreaker:
    """
    Circuit breaker to prevent runaway automation.
    """

    def __init__(self, blueprint: dict):
        self.failure_threshold = blueprint['governance']['safety']['circuit_breaker']['failure_threshold']
        self.reset_timeout = blueprint['governance']['safety']['circuit_breaker']['reset_timeout']
        self.failure_window = blueprint['governance']['safety']['circuit_breaker']['failure_window']
        self.failures = []
        self.state = 'closed'
        self.opened_at = None

    def record_failure(self, operation: dict) -> None:
        """
        Record operation failure and check if threshold exceeded.

        Args:
            operation: Failed operation details
        """
        current_time = get_current_timestamp()

        # Add failure to list
        self.failures.append({
            'timestamp': current_time,
            'operation_id': operation['operation_id'],
            'operation_type': operation['type'],
            'failure_reason': operation['failure_reason']
        })

        # Remove failures outside window (older than 5 minutes)
        cutoff_time = current_time - self.failure_window
        self.failures = [f for f in self.failures if f['timestamp'] > cutoff_time]

        # Check if threshold exceeded
        if len(self.failures) >= self.failure_threshold:
            self.open_circuit()

    def open_circuit(self) -> None:
        """
        Open circuit breaker - block all operations.
        """
        self.state = 'open'
        self.opened_at = get_current_timestamp()

        # Log circuit breaker activation
        log_event({
            'event_type': 'circuit_breaker_opened',
            'timestamp': self.opened_at,
            'consecutive_failures': len(self.failures),
            'failure_threshold': self.failure_threshold,
            'recent_failures': self.failures
        })

        # Send critical alert
        send_alert({
            'severity': 'critical',
            'title': 'Circuit Breaker Activated',
            'message': f'Agent operations blocked after {len(self.failures)} consecutive failures. Manual intervention required.',
            'failures': self.failures
        })

    def can_execute(self) -> dict:
        """
        Check if operations are allowed.

        Returns:
            Dictionary with allowed status and reason
        """
        if self.state == 'closed':
            return {
                'allowed': True,
                'state': 'closed',
                'reason': 'Circuit breaker closed - operations allowed'
            }

        elif self.state == 'open':
            # Check if reset timeout has elapsed
            current_time = get_current_timestamp()
            time_since_opened = current_time - self.opened_at

            if time_since_opened > self.reset_timeout:
                # Transition to half-open
                self.state = 'half_open'
                return {
                    'allowed': True,
                    'state': 'half_open',
                    'reason': 'Circuit breaker half-open - test operation allowed'
                }
            else:
                return {
                    'allowed': False,
                    'state': 'open',
                    'reason': f'Circuit breaker open - operations blocked. Reset in {self.reset_timeout - time_since_opened}s',
                    'manual_reset_required': True
                }

        elif self.state == 'half_open':
            return {
                'allowed': True,
                'state': 'half_open',
                'reason': 'Circuit breaker half-open - test operation allowed'
            }

    def record_success(self) -> None:
        """
        Record successful operation.

        If in half-open state, transition to closed.
        """
        if self.state == 'half_open':
            self.close_circuit()

        # Clear failure history on success
        self.failures = []

    def close_circuit(self) -> None:
        """
        Close circuit breaker - resume normal operations.
        """
        self.state = 'closed'
        self.opened_at = None
        self.failures = []

        log_event({
            'event_type': 'circuit_breaker_closed',
            'timestamp': get_current_timestamp(),
            'reason': 'Test operation succeeded - resuming normal operations'
        })

    def manual_reset(self) -> None:
        """
        Manually reset circuit breaker.

        Requires human authorization.
        """
        self.state = 'closed'
        self.opened_at = None
        self.failures = []

        log_event({
            'event_type': 'circuit_breaker_manual_reset',
            'timestamp': get_current_timestamp(),
            'reset_by': 'human_operator'
        })
```

## Configuration

### Blueprint Configuration

```yaml
governance:
  safety:
    circuit_breaker:
      enabled: true
      failure_threshold: 3        # Open after 3 consecutive failures
      reset_timeout: 1h           # Wait 1 hour before half-open
      failure_window: 5m          # Only count failures within 5 minutes
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `true` | Enable/disable circuit breaker |
| `failure_threshold` | `3` | Number of failures before opening |
| `reset_timeout` | `1h` | Time before transitioning to half-open |
| `failure_window` | `5m` | Time window for counting failures |

### Tuning Guidelines

**Conservative (High Safety)**:
```yaml
failure_threshold: 2      # Open after 2 failures
reset_timeout: 2h         # Wait 2 hours
failure_window: 10m       # Count failures over 10 minutes
```

**Balanced (Default)**:
```yaml
failure_threshold: 3      # Open after 3 failures
reset_timeout: 1h         # Wait 1 hour
failure_window: 5m        # Count failures over 5 minutes
```

**Aggressive (High Availability)**:
```yaml
failure_threshold: 5      # Open after 5 failures
reset_timeout: 30m        # Wait 30 minutes
failure_window: 3m        # Count failures over 3 minutes
```

## Circuit Breaker Activation Example

### Scenario: Three Consecutive Failures

**Failure 1**: Scale-up operation fails
```json
{
  "timestamp": "2026-02-10T17:00:00Z",
  "operation_id": "dec-20260210-170000-001",
  "operation_type": "scale_up",
  "failure_reason": "Insufficient cluster capacity",
  "circuit_breaker_state": "closed",
  "consecutive_failures": 1
}
```

**Failure 2**: Resource optimization fails
```json
{
  "timestamp": "2026-02-10T17:02:00Z",
  "operation_id": "dec-20260210-170200-002",
  "operation_type": "adjust_resources",
  "failure_reason": "Pods failed to restart",
  "circuit_breaker_state": "closed",
  "consecutive_failures": 2
}
```

**Failure 3**: Pod restart fails - Circuit Opens
```json
{
  "timestamp": "2026-02-10T17:04:00Z",
  "operation_id": "dec-20260210-170400-003",
  "operation_type": "restart_pod",
  "failure_reason": "Pod CrashLoopBackOff",
  "circuit_breaker_state": "open",
  "consecutive_failures": 3,
  "circuit_opened_at": "2026-02-10T17:04:00Z",
  "alert_sent": true
}
```

**Blocked Operation**: Subsequent operation blocked
```json
{
  "timestamp": "2026-02-10T17:06:00Z",
  "operation_id": "dec-20260210-170600-004",
  "operation_type": "scale_up",
  "blocked": true,
  "block_reason": "circuit_breaker_open",
  "circuit_breaker_state": "open",
  "manual_reset_required": true
}
```

## Manual Reset Procedure

When circuit breaker opens, manual intervention is required.

### Reset Steps

1. **Investigate Root Cause**
   - Review failure logs
   - Identify why operations are failing
   - Check cluster health, capacity, configuration

2. **Fix Underlying Issue**
   - Address root cause (add capacity, fix config, etc.)
   - Verify fix in staging if possible
   - Ensure issue won't recur

3. **Reset Circuit Breaker**
   ```bash
   # Option 1: CLI command
   kubectl annotate deployment todo-frontend circuit-breaker-reset=true

   # Option 2: API call
   curl -X POST https://agent-api/circuit-breaker/reset \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"service": "todo-frontend", "reset_by": "john.doe@example.com"}'
   ```

4. **Monitor Closely**
   - Watch first few operations after reset
   - Verify operations succeed
   - Be ready to investigate if failures recur

### Reset Authorization

Only authorized personnel can reset circuit breaker:
- DevOps team members
- On-call engineers
- Service owners

Reset requires:
- Investigation of root cause
- Documentation of fix applied
- Approval from team lead (for production)

## Notification

When circuit breaker opens, critical alerts are sent.

### Alert Format

```
🚨 CRITICAL: Circuit Breaker Activated

Service: todo-frontend
Consecutive Failures: 3
Failure Threshold: 3
Circuit State: OPEN
Operations Blocked: YES

Recent Failures:
1. 17:00:00 - scale_up failed: Insufficient cluster capacity
2. 17:02:00 - adjust_resources failed: Pods failed to restart
3. 17:04:00 - restart_pod failed: Pod CrashLoopBackOff

Action Required:
1. Investigate root cause of failures
2. Fix underlying issue
3. Manually reset circuit breaker
4. Monitor operations after reset

Manual Reset: kubectl annotate deployment todo-frontend circuit-breaker-reset=true
```

### Notification Channels

- **Slack**: `slack://devops-alerts` (immediate)
- **PagerDuty**: `pagerduty://devops-oncall` (page on-call)
- **Email**: `email://devops-team@example.com` (backup)

## Metrics and Monitoring

### Key Metrics

- **Circuit Breaker State**: Current state (closed/open/half-open)
- **Failure Count**: Number of recent failures
- **Time Since Opened**: Duration circuit has been open
- **Reset Count**: Number of manual resets (indicates recurring issues)

### Monitoring Dashboard

```
Circuit Breaker Status
├── State: CLOSED ✅
├── Consecutive Failures: 0 / 3
├── Last Failure: None
└── Operations Allowed: YES

Recent History (24h)
├── Circuit Opened: 0 times
├── Manual Resets: 0 times
└── Total Failures: 2 (below threshold)
```

## Best Practices

1. **Investigate Before Reset**: Always understand why circuit opened
2. **Fix Root Cause**: Don't reset without addressing underlying issue
3. **Monitor After Reset**: Watch operations closely after reset
4. **Tune Thresholds**: Adjust based on failure patterns
5. **Document Resets**: Log reason for reset and fix applied

## Troubleshooting

### Problem: Circuit breaker opens too frequently

**Causes**:
- Threshold too low
- Underlying infrastructure issues
- Agent decision logic errors

**Solutions**:
- Increase failure threshold
- Fix infrastructure issues
- Review and improve agent logic

### Problem: Circuit breaker doesn't open when it should

**Causes**:
- Threshold too high
- Failure window too short
- Failures not being counted

**Solutions**:
- Decrease failure threshold
- Increase failure window
- Verify failure recording logic

### Problem: Manual reset doesn't work

**Causes**:
- Authorization issues
- Circuit breaker state not persisted
- Configuration errors

**Solutions**:
- Verify authorization
- Check state persistence
- Review configuration

## See Also

- [Governance Documentation](./GOVERNANCE.md) - Safety mechanisms overview
- [Cooldown Periods Documentation](./COOLDOWN_PERIODS.md) - Related safety mechanism
- [Audit Logging Documentation](./AUDIT_LOGGING.md) - How circuit breaker events are logged
