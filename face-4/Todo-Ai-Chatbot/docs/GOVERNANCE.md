# Governance Enforcer Documentation

## Overview

The Governance Enforcer is the safety agent that validates every operation against blueprint governance rules before execution. It classifies operations into three tiers (Allowed, Restricted, Forbidden) and enforces approval workflows for restricted operations.

**Key Responsibility**: Ensure all agent operations comply with governance policies and prevent unauthorized actions.

## Governance Architecture

```
Decision from Decision Engine
        ↓
[Classify Operation]
        ↓
    ┌───┴───┐
    │       │
Allowed  Restricted  Forbidden
    │       │           │
    │   [Request      [Block]
    │   Approval]       │
    │       │           │
    └───┬───┘           │
        │               │
    [Execute]      [Log & Reject]
```

## Three-Tier Classification

### Tier 1: Allowed Operations (Autonomous)

Operations that agents can execute without human approval.

**Characteristics**:
- Safe and reversible
- Within defined boundaries
- Low risk of service disruption
- Aligned with blueprint targets

**Examples**:
- `scale_within_limits`: Scale between min_replicas and max_replicas
- `restart_failed_pods`: Restart pods with RestartCount > 0
- `adjust_resources_within_10_percent`: Adjust CPU/memory by ≤10%
- `view_logs`: Read-only operations
- `view_metrics`: Read-only operations

**Classification Logic**:
```python
def is_allowed_operation(operation: dict, blueprint: dict) -> bool:
    """
    Check if operation is in allowed list and meets criteria.

    Args:
        operation: Operation details
            {
                'type': 'scale_up',
                'current_replicas': 2,
                'target_replicas': 3
            }
        blueprint: Parsed blueprint with governance rules

    Returns:
        True if operation is allowed, False otherwise
    """
    allowed_ops = blueprint['governance']['allowed_operations']

    # Check operation type
    if operation['type'] == 'scale_up' or operation['type'] == 'scale_down':
        # Check if within limits
        min_replicas = blueprint['scaling']['min_replicas']
        max_replicas = blueprint['scaling']['max_replicas']
        target = operation['target_replicas']

        if min_replicas <= target <= max_replicas:
            return 'scale_within_limits' in allowed_ops
        else:
            return False

    elif operation['type'] == 'adjust_cpu' or operation['type'] == 'adjust_memory':
        # Check if within 10% threshold
        current = operation['current_value']
        target = operation['target_value']
        change_percent = abs(target - current) / current

        if change_percent <= 0.10:
            return 'adjust_resources_within_10_percent' in allowed_ops
        else:
            return False

    elif operation['type'] == 'restart_pod':
        # Check if pod has failures
        restart_count = operation.get('restart_count', 0)

        if restart_count > 0:
            return 'restart_failed_pods' in allowed_ops
        else:
            return False

    else:
        return False
```

### Tier 2: Restricted Operations (Require Approval)

Operations that require human judgment before execution.

**Characteristics**:
- Significant impact on resources or performance
- Beyond defined boundaries
- Moderate risk
- Need human oversight

**Examples**:
- `scale_beyond_limits`: Scale beyond max_replicas or below min_replicas
- `change_resource_limits_beyond_10_percent`: Adjust CPU/memory by >10%
- `modify_deployment_strategy`: Change rolling update parameters
- `change_health_checks`: Modify probe configurations
- `modify_configmaps`: Change application configuration

**Classification Logic**:
```python
def is_restricted_operation(operation: dict, blueprint: dict) -> bool:
    """
    Check if operation requires approval.

    Args:
        operation: Operation details
        blueprint: Parsed blueprint with governance rules

    Returns:
        True if operation requires approval, False otherwise
    """
    restricted_ops = blueprint['governance']['requires_approval']

    # Check operation type
    if operation['type'] == 'scale_up' or operation['type'] == 'scale_down':
        # Check if beyond limits
        min_replicas = blueprint['scaling']['min_replicas']
        max_replicas = blueprint['scaling']['max_replicas']
        target = operation['target_replicas']

        if target > max_replicas or target < min_replicas:
            return 'scale_beyond_limits' in restricted_ops
        else:
            return False

    elif operation['type'] == 'adjust_cpu' or operation['type'] == 'adjust_memory':
        # Check if beyond 10% threshold
        current = operation['current_value']
        target = operation['target_value']
        change_percent = abs(target - current) / current

        if change_percent > 0.10:
            return 'change_resource_limits_beyond_10_percent' in restricted_ops
        else:
            return False

    elif operation['type'] == 'modify_deployment_strategy':
        return 'modify_deployment_strategy' in restricted_ops

    elif operation['type'] == 'change_health_checks':
        return 'change_health_checks' in restricted_ops

    else:
        return False
```

### Tier 3: Forbidden Operations (Blocked)

Operations that are never allowed for autonomous agents.

**Characteristics**:
- High risk of data loss or service outage
- Security implications
- Irreversible or difficult to recover
- Require manual human execution

**Examples**:
- `delete_deployment`: Delete any deployment
- `delete_service`: Delete any service
- `delete_persistent_volumes`: Delete any PersistentVolume
- `modify_secrets`: Modify any Secret
- `change_network_policies`: Modify NetworkPolicies
- `modify_rbac`: Modify RBAC permissions

**Classification Logic**:
```python
def is_forbidden_operation(operation: dict, blueprint: dict) -> bool:
    """
    Check if operation is forbidden.

    Args:
        operation: Operation details
        blueprint: Parsed blueprint with governance rules

    Returns:
        True if operation is forbidden, False otherwise
    """
    forbidden_ops = blueprint['governance']['forbidden_operations']

    # Check operation type
    if operation['type'] in ['delete_deployment', 'delete_service',
                             'delete_persistent_volumes', 'modify_secrets',
                             'change_network_policies', 'modify_rbac']:
        return operation['type'] in forbidden_ops

    return False
```

## Complete Classification Flow

```python
class GovernanceEnforcer:
    """
    Governance Enforcer Agent

    Validates operations against blueprint governance rules.
    """

    def __init__(self, blueprint: dict):
        """Initialize with parsed blueprint."""
        self.blueprint = blueprint
        self.governance = blueprint['governance']

    def classify_operation(self, operation: dict) -> dict:
        """
        Classify operation into allowed/restricted/forbidden.

        Args:
            operation: Operation details from Decision Engine

        Returns:
            Classification result with action and rationale
        """
        # Step 1: Check if forbidden
        if self.is_forbidden_operation(operation):
            return {
                'classification': 'forbidden',
                'action': 'block',
                'rationale': self.get_forbidden_rationale(operation),
                'blueprint_references': self.get_forbidden_references(operation),
                'alternative_suggestion': self.suggest_alternative(operation)
            }

        # Step 2: Check if restricted (requires approval)
        if self.is_restricted_operation(operation):
            return {
                'classification': 'restricted',
                'action': 'request_approval',
                'rationale': self.get_restricted_rationale(operation),
                'blueprint_references': self.get_restricted_references(operation),
                'approval_workflow': self.get_approval_workflow()
            }

        # Step 3: Check if allowed
        if self.is_allowed_operation(operation):
            return {
                'classification': 'allowed',
                'action': 'execute',
                'rationale': self.get_allowed_rationale(operation),
                'blueprint_references': self.get_allowed_references(operation)
            }

        # Step 4: Unknown operation (default to forbidden)
        return {
            'classification': 'forbidden',
            'action': 'block',
            'rationale': 'Operation type not recognized in governance rules',
            'blueprint_references': ['governance.agent_authority'],
            'recommendation': 'Add operation to blueprint governance rules'
        }
```

## Approval Workflow

When an operation is classified as **restricted**, the Governance Enforcer triggers an approval workflow.

### Approval Request Generation

```python
def generate_approval_request(
    operation: dict,
    classification: dict,
    blueprint: dict
) -> dict:
    """
    Generate approval request for restricted operation.

    Args:
        operation: Operation details
        classification: Classification result
        blueprint: Parsed blueprint

    Returns:
        Approval request object
    """
    return {
        'request_id': generate_request_id(),
        'timestamp': get_current_timestamp(),
        'service': blueprint['metadata']['name'],
        'blueprint_version': blueprint['metadata']['version'],
        'operation': {
            'type': operation['type'],
            'current_state': operation['current_state'],
            'proposed_state': operation['proposed_state']
        },
        'rationale': operation['rationale'],
        'risk_assessment': {
            'risk_level': assess_risk_level(operation),
            'impact': assess_impact(operation),
            'reversibility': assess_reversibility(operation)
        },
        'rollback_plan': generate_rollback_plan(operation),
        'blueprint_references': classification['blueprint_references'],
        'approvers': blueprint['governance']['approval_workflow']['approvers'],
        'timeout': blueprint['governance']['approval_workflow']['timeout'],
        'notification_channels': blueprint['governance']['approval_workflow']['notification_channels']
    }
```

### Approval Request Example

```json
{
  "request_id": "apr-20260210-160000-001",
  "timestamp": "2026-02-10T16:00:00Z",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "operation": {
    "type": "scale_beyond_limits",
    "current_state": {
      "replicas": 5,
      "max_replicas": 5,
      "cpu_utilization": 95,
      "latency_p95": 300
    },
    "proposed_state": {
      "replicas": 6,
      "max_replicas": 6
    }
  },
  "rationale": "CPU utilization (95%) and latency (300ms) exceed targets. Current replicas (5) at max_replicas limit. Recommend increasing max_replicas to 6 and scaling to 6 replicas.",
  "risk_assessment": {
    "risk_level": "medium",
    "impact": "Increases resource allocation beyond blueprint limits",
    "reversibility": "High - can scale back immediately if needed"
  },
  "rollback_plan": "If performance does not improve or costs exceed budget, scale back to 5 replicas and investigate root cause.",
  "blueprint_references": [
    "spec.scaling.max_replicas",
    "governance.agent_authority.requires_approval[0]"
  ],
  "approvers": ["devops-team"],
  "timeout": "1h",
  "notification_channels": ["slack://devops-alerts"]
}
```

### Approval Workflow States

```
[Request Created]
        ↓
[Notification Sent]
        ↓
    ┌───┴───┐
    │       │
[Approved] [Rejected]  [Timeout]
    │       │           │
[Execute]  [Log]    [Auto-Reject]
    │       │           │
[Verify]  [Done]     [Log]
    │                   │
[Done]              [Done]
```

### Approval Response Handling

```python
def handle_approval_response(
    request_id: str,
    response: dict
) -> dict:
    """
    Handle approval response (approved/rejected/timeout).

    Args:
        request_id: Approval request ID
        response: Approval response
            {
                'status': 'approved' | 'rejected' | 'timeout',
                'approver': 'user@example.com',
                'timestamp': '2026-02-10T16:30:00Z',
                'comment': 'Approved - performance issue confirmed'
            }

    Returns:
        Action to take
    """
    if response['status'] == 'approved':
        return {
            'action': 'execute',
            'rationale': f"Approved by {response['approver']}: {response['comment']}",
            'approved_at': response['timestamp'],
            'approved_by': response['approver']
        }

    elif response['status'] == 'rejected':
        return {
            'action': 'block',
            'rationale': f"Rejected by {response['approver']}: {response['comment']}",
            'rejected_at': response['timestamp'],
            'rejected_by': response['approver']
        }

    elif response['status'] == 'timeout':
        # Check auto_reject_on_timeout policy
        auto_reject = blueprint['governance']['approval_workflow']['auto_reject_on_timeout']

        if auto_reject:
            return {
                'action': 'block',
                'rationale': 'Approval request timed out - auto-rejected per governance policy',
                'timeout_at': response['timestamp']
            }
        else:
            return {
                'action': 'pending',
                'rationale': 'Approval request timed out - awaiting manual review',
                'timeout_at': response['timestamp']
            }
```

## Audit Logging

Every governance check is logged for compliance and debugging.

### Audit Log Format

```json
{
  "timestamp": "2026-02-10T16:00:00Z",
  "agent_id": "governance-enforcer-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "operation": {
    "type": "scale_up",
    "details": {
      "current_replicas": 2,
      "target_replicas": 3
    }
  },
  "governance_check": {
    "classification": "allowed",
    "action": "execute",
    "rationale": "Target replicas (3) is within blueprint limits (min: 1, max: 5)",
    "blueprint_references": [
      "governance.agent_authority.allowed_operations[0]",
      "spec.scaling.min_replicas",
      "spec.scaling.max_replicas"
    ]
  },
  "outcome": "success",
  "execution_duration": "2.5s"
}
```

### Audit Log Storage

```python
def log_governance_check(
    operation: dict,
    classification: dict,
    outcome: dict,
    blueprint: dict
) -> None:
    """
    Log governance check to audit trail.

    Args:
        operation: Operation details
        classification: Classification result
        outcome: Execution outcome
        blueprint: Parsed blueprint
    """
    log_entry = {
        'timestamp': get_current_timestamp(),
        'agent_id': 'governance-enforcer-001',
        'service': blueprint['metadata']['name'],
        'blueprint_version': blueprint['metadata']['version'],
        'operation': {
            'type': operation['type'],
            'details': operation
        },
        'governance_check': {
            'classification': classification['classification'],
            'action': classification['action'],
            'rationale': classification['rationale'],
            'blueprint_references': classification['blueprint_references']
        },
        'outcome': outcome['status'],
        'execution_duration': outcome.get('duration', 'N/A')
    }

    # Write to audit log
    log_destination = blueprint['governance']['audit']['log_destination']
    log_format = blueprint['governance']['audit']['log_format']

    if log_format == 'json':
        write_json_log(log_destination, log_entry)
    else:
        write_text_log(log_destination, log_entry)
```

## Safety Mechanisms

### Circuit Breaker

Prevents runaway automation by stopping after consecutive failures.

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
        self.state = 'closed'  # closed, open, half_open

    def record_failure(self) -> None:
        """Record operation failure."""
        self.failures.append(get_current_timestamp())

        # Remove failures outside window
        cutoff = get_current_timestamp() - self.failure_window
        self.failures = [f for f in self.failures if f > cutoff]

        # Check if threshold exceeded
        if len(self.failures) >= self.failure_threshold:
            self.state = 'open'
            self.opened_at = get_current_timestamp()

    def can_execute(self) -> bool:
        """Check if operations are allowed."""
        if self.state == 'closed':
            return True

        elif self.state == 'open':
            # Check if reset timeout elapsed
            if get_current_timestamp() - self.opened_at > self.reset_timeout:
                self.state = 'half_open'
                return True
            else:
                return False

        elif self.state == 'half_open':
            return True
```

### Rate Limiting

Limits number of operations per time period.

```python
class RateLimiter:
    """
    Rate limiter to prevent excessive automation.
    """

    def __init__(self, blueprint: dict):
        self.max_per_hour = blueprint['governance']['safety']['rate_limiting']['max_operations_per_hour']
        self.max_per_day = blueprint['governance']['safety']['rate_limiting']['max_operations_per_day']
        self.operations = []

    def can_execute(self) -> dict:
        """Check if operation is within rate limits."""
        now = get_current_timestamp()

        # Count operations in last hour
        hour_ago = now - 3600
        ops_last_hour = len([op for op in self.operations if op > hour_ago])

        # Count operations in last day
        day_ago = now - 86400
        ops_last_day = len([op for op in self.operations if op > day_ago])

        if ops_last_hour >= self.max_per_hour:
            return {
                'allowed': False,
                'reason': 'hourly_rate_limit_exceeded',
                'limit': self.max_per_hour,
                'current': ops_last_hour
            }

        if ops_last_day >= self.max_per_day:
            return {
                'allowed': False,
                'reason': 'daily_rate_limit_exceeded',
                'limit': self.max_per_day,
                'current': ops_last_day
            }

        return {'allowed': True}

    def record_operation(self) -> None:
        """Record operation execution."""
        self.operations.append(get_current_timestamp())
```

## Best Practices

1. **Always Check Governance First**: Before any operation, check governance rules
2. **Log Everything**: Log all governance checks for audit trail
3. **Provide Clear Rationale**: Explain why operation was allowed/blocked
4. **Reference Blueprint**: Cite specific blueprint sections
5. **Suggest Alternatives**: When blocking, suggest alternative approaches

## Integration Example

```python
# Initialize agents
blueprint_parser = BlueprintParser('blueprints/schema.json')
blueprint = blueprint_parser.parse('blueprints/frontend/blueprint.yaml')

decision_engine = DecisionEngine(blueprint)
governance_enforcer = GovernanceEnforcer(blueprint)
execution_engine = ExecutionEngine()

# Make decision
current_metrics = collect_metrics()
decision = decision_engine.make_decision(current_metrics)

# Check governance
governance_result = governance_enforcer.classify_operation(decision)

# Execute if allowed
if governance_result['classification'] == 'allowed':
    outcome = execution_engine.execute(decision)
    governance_enforcer.log_governance_check(decision, governance_result, outcome, blueprint)

elif governance_result['classification'] == 'restricted':
    approval_request = governance_enforcer.generate_approval_request(decision, governance_result, blueprint)
    send_approval_request(approval_request)

elif governance_result['classification'] == 'forbidden':
    governance_enforcer.log_governance_check(decision, governance_result, {'status': 'blocked'}, blueprint)
    notify_blocked_operation(decision, governance_result)
```

## See Also

- [Blueprint Format Documentation](./BLUEPRINT_FORMAT.md) - Blueprint structure and governance section
- [Decision Engine Documentation](./DECISION_ENGINE.md) - How decisions are made
- [Verification Documentation](./VERIFICATION_ENGINE.md) - How outcomes are verified
