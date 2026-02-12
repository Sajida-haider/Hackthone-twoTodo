# Approval Workflow Documentation

## Overview

The Approval Workflow is triggered when agents propose **restricted operations** that require human judgment before execution. This document explains how approval requests are generated, presented, processed, and logged.

**Key Principle**: Restricted operations are not forbidden—they're legitimate actions that need human oversight due to their impact or scope.

## When Approval Workflow is Triggered

The approval workflow activates when the Governance Enforcer classifies an operation as **restricted** (Tier 2).

### Common Restricted Operations

1. **Scale Beyond Limits**
   - Scaling above `max_replicas` or below `min_replicas`
   - Requires capacity planning review

2. **Resource Changes > 10%**
   - CPU/memory adjustments exceeding ±10% of current values
   - Requires performance impact assessment

3. **Deployment Strategy Changes**
   - Modifying `maxSurge`, `maxUnavailable`, or rollout strategy
   - Requires availability impact review

4. **Health Check Modifications**
   - Changing probe configurations (readiness, liveness)
   - Requires reliability impact assessment

5. **ConfigMap Updates**
   - Modifying application configuration
   - Requires behavior change review

## Approval Request Generation

When a restricted operation is detected, the Governance Enforcer generates a structured approval request.

### Approval Request Structure

```json
{
  "request_id": "apr-YYYYMMDD-HHMMSS-NNN",
  "created_at": "ISO 8601 timestamp",
  "service": "service-name",
  "blueprint_version": "1.0.0",

  "operation_details": {
    "type": "operation_type",
    "current_state": { /* current system state */ },
    "proposed_state": { /* proposed state after operation */ }
  },

  "rationale": {
    "problem": "What issue triggered this operation?",
    "proposed_solution": "How will this operation solve it?",
    "why_approval_needed": "Why can't this be executed autonomously?",
    "blueprint_references": ["spec.section.field"]
  },

  "risk_assessment": {
    "risk_level": "low | medium | high",
    "impact_analysis": { /* performance, cost, availability */ },
    "reversibility": "high | medium | low",
    "blast_radius": "single_service | multiple_services | cluster",
    "failure_scenarios": ["scenario1", "scenario2"]
  },

  "cost_impact": {
    "current_monthly_cost": "$100",
    "proposed_monthly_cost": "$120",
    "increase": "$20/month (20%)",
    "budget_status": "within | exceeds budget"
  },

  "rollback_plan": {
    "trigger_conditions": ["condition1", "condition2"],
    "rollback_action": "description",
    "rollback_command": "kubectl command",
    "rollback_duration": "< 30 seconds"
  },

  "alternative_options": [
    {
      "description": "Alternative approach",
      "pros": "Benefits",
      "cons": "Drawbacks",
      "recommendation": "Why this is/isn't preferred"
    }
  ],

  "approval_workflow": {
    "approvers": ["devops-team"],
    "notification_channels": ["slack://devops-alerts"],
    "timeout": "1h",
    "auto_reject_on_timeout": true
  }
}
```

### Required Information

Every approval request must include:

1. **Context**: What is the current state and what's being proposed?
2. **Rationale**: Why is this operation needed?
3. **Risk Assessment**: What could go wrong?
4. **Cost Impact**: What are the financial implications?
5. **Rollback Plan**: How can we undo this if it fails?
6. **Alternatives**: What other options were considered?

## Approval Request Presentation

### Notification Channels

Approval requests are sent to configured notification channels:

- **Slack**: `slack://devops-alerts`
- **Email**: `email://devops-team@example.com`
- **PagerDuty**: `pagerduty://devops-oncall`
- **Web Dashboard**: `https://approval-system.example.com`

### Notification Format

```
🔔 Approval Required: [Operation Type]

Service: todo-frontend
Operation: scale_beyond_limits
Current: 5 replicas (at max)
Proposed: 6 replicas
Reason: Sustained high load (92% utilization), latency 280ms > 200ms target
Cost Impact: +$20/month (20% increase)
Risk: Medium
Timeout: 1 hour

Actions:
✅ Approve: [approval-url]
❌ Reject: [rejection-url]
📋 View Details: [details-url]
```

### Approval Interface

Approvers can respond through:

1. **Web Interface**: Click approve/reject links in notification
2. **CLI Command**: `kubectl approve apr-20260210-170000-002`
3. **API Call**: `POST /api/approvals/{request_id}/approve`
4. **Slack Button**: Interactive Slack message with approve/reject buttons

## Approval Response Handling

### Approved Response

When an approver approves the request:

```json
{
  "request_id": "apr-20260210-170000-002",
  "status": "approved",
  "approver": "john.doe@example.com",
  "approved_at": "2026-02-10T17:15:00Z",
  "comment": "Approved - performance issue confirmed, cost increase justified"
}
```

**Next Steps**:
1. Log approval with approver details
2. Pass operation to Execution Engine
3. Execute operation
4. Monitor and verify outcome
5. Log execution result

### Rejected Response

When an approver rejects the request:

```json
{
  "request_id": "apr-20260210-170000-002",
  "status": "rejected",
  "approver": "jane.smith@example.com",
  "rejected_at": "2026-02-10T17:20:00Z",
  "comment": "Rejected - prefer code optimization over scaling. Create ticket for performance investigation."
}
```

**Next Steps**:
1. Log rejection with reason
2. Do NOT execute operation
3. Notify Decision Engine of rejection
4. Consider alternative approaches
5. Continue monitoring system

### Timeout Response

If no response within timeout period (default: 1 hour):

```json
{
  "request_id": "apr-20260210-170000-002",
  "status": "timeout",
  "timeout_at": "2026-02-10T18:00:00Z",
  "auto_reject": true,
  "comment": "No response within 1 hour - auto-rejected per governance policy"
}
```

**Next Steps**:
1. Auto-reject per blueprint policy (`auto_reject_on_timeout: true`)
2. Log timeout event
3. Alert on-call team about unresolved issue
4. Do NOT execute operation
5. Escalate if system remains in degraded state

## Timeout Configuration

### Blueprint Configuration

```yaml
governance:
  approval_workflow:
    timeout: 1h                      # Approval timeout
    auto_reject_on_timeout: true     # Auto-reject if no response
```

### Timeout Behavior

| Setting | Behavior |
|---------|----------|
| `auto_reject_on_timeout: true` | Operation is rejected if no response within timeout |
| `auto_reject_on_timeout: false` | Operation remains pending, requires manual review |

**Recommendation**: Use `auto_reject_on_timeout: true` to prevent indefinite blocking.

### Timeout Rationale

- **1 hour**: Reasonable time for human response during business hours
- **Auto-reject**: Prevents operations from blocking indefinitely
- **Escalation**: Timeout triggers alert to on-call team

## Approval Logging

### Approval Request Log

```json
{
  "timestamp": "2026-02-10T17:00:00Z",
  "event_type": "approval_request_created",
  "request_id": "apr-20260210-170000-002",
  "service": "todo-frontend",
  "operation": "scale_beyond_limits",
  "approvers": ["devops-team"],
  "timeout": "1h",
  "notification_sent": true
}
```

### Approval Response Log

```json
{
  "timestamp": "2026-02-10T17:15:00Z",
  "event_type": "approval_granted",
  "request_id": "apr-20260210-170000-002",
  "approver": "john.doe@example.com",
  "response_time": "15 minutes",
  "comment": "Approved - performance issue confirmed"
}
```

### Execution Log (Post-Approval)

```json
{
  "timestamp": "2026-02-10T17:15:30Z",
  "event_type": "operation_executed",
  "request_id": "apr-20260210-170000-002",
  "operation": "scale_up",
  "target_replicas": 6,
  "execution_result": "success",
  "verification_status": "passed"
}
```

## Approval Workflow States

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

## Best Practices

### For Agents

1. **Provide Complete Context**: Include all relevant information in approval request
2. **Clear Rationale**: Explain why operation is needed and why approval is required
3. **Risk Assessment**: Be honest about risks and potential failures
4. **Alternatives**: Show that other options were considered
5. **Rollback Plan**: Always include a clear rollback strategy

### For Approvers

1. **Review Promptly**: Respond within timeout period to avoid auto-rejection
2. **Check Context**: Verify current state matches approval request
3. **Assess Risk**: Consider impact on users, cost, and availability
4. **Provide Feedback**: Include comments explaining approval/rejection decision
5. **Follow Up**: Monitor execution and verify outcome after approval

### For Blueprint Authors

1. **Set Appropriate Timeout**: Balance responsiveness with human availability
2. **Configure Auto-Reject**: Prevent indefinite blocking
3. **Define Approvers**: Specify who can approve restricted operations
4. **Multiple Channels**: Use multiple notification channels for redundancy
5. **Review Patterns**: Analyze approval requests to identify capacity planning issues

## Common Approval Scenarios

### Scenario 1: Scale Beyond Limits

**Trigger**: Need to scale beyond `max_replicas`

**Approval Request Includes**:
- Current load metrics (CPU, memory, latency)
- Duration of high load
- Cost impact of additional replicas
- Capacity planning implications

**Approval Decision Factors**:
- Is this a temporary spike or sustained load?
- Is cost increase justified?
- Should `max_replicas` be permanently increased?
- Are there alternative solutions (code optimization)?

### Scenario 2: Resource Changes > 10%

**Trigger**: Need to adjust CPU/memory by more than 10%

**Approval Request Includes**:
- Current vs. proposed resource allocation
- Usage patterns over time
- Performance impact analysis
- Cost implications

**Approval Decision Factors**:
- Is resource change based on sustained usage patterns?
- Will change impact performance or stability?
- Is cost increase acceptable?
- Should blueprint targets be adjusted?

### Scenario 3: Deployment Strategy Change

**Trigger**: Need to modify rolling update parameters

**Approval Request Includes**:
- Current vs. proposed strategy
- Reason for change (faster rollouts, zero downtime)
- Availability impact analysis
- Rollback complexity

**Approval Decision Factors**:
- Does change align with availability requirements?
- Is risk acceptable for this service?
- Should change be permanent or temporary?
- Are there safer alternatives?

## Troubleshooting

### Problem: Approval requests timing out

**Causes**:
- Approvers not receiving notifications
- Timeout too short for human response
- Approvers unavailable (off-hours, vacation)

**Solutions**:
- Verify notification channels are working
- Increase timeout period in blueprint
- Configure multiple approvers for redundancy
- Set up on-call rotation for approvals

### Problem: Too many approval requests

**Causes**:
- Blueprint limits too restrictive
- System frequently exceeding normal bounds
- Capacity planning issues

**Solutions**:
- Review and adjust blueprint limits
- Investigate root cause of frequent limit violations
- Consider moving some operations to "allowed" tier
- Improve capacity planning

### Problem: Approvals granted but operations fail

**Causes**:
- Insufficient cluster capacity
- Configuration errors
- Timing issues (state changed between approval and execution)

**Solutions**:
- Verify cluster capacity before approval
- Validate configuration in approval request
- Implement pre-execution validation checks
- Consider shorter approval timeout to reduce state drift

## Security Considerations

### Approval Authorization

- Only designated approvers can approve requests
- Approver identity must be verified
- Approval actions are logged with approver details
- Approvers must have appropriate RBAC permissions

### Approval Tampering Prevention

- Approval requests are immutable once created
- Approval responses are cryptographically signed (optional)
- All approval actions are logged to immutable audit trail
- Approval URLs include secure tokens to prevent unauthorized access

### Approval Bypass Prevention

- Agents cannot bypass approval workflow
- Restricted operations cannot be reclassified as allowed
- Approval workflow is enforced at governance layer
- Attempts to bypass approval are logged and blocked

## Metrics and Monitoring

### Key Metrics

- **Approval Request Rate**: Requests per day/week
- **Approval Response Time**: Time from request to response
- **Approval Rate**: Percentage of requests approved vs. rejected
- **Timeout Rate**: Percentage of requests timing out
- **Execution Success Rate**: Success rate of approved operations

### Monitoring Alerts

- **High Approval Request Rate**: May indicate capacity planning issues
- **High Timeout Rate**: May indicate approver availability issues
- **High Rejection Rate**: May indicate agent decision quality issues
- **Low Execution Success Rate**: May indicate validation issues

## See Also

- [Governance Documentation](./GOVERNANCE.md) - Three-tier operation classification
- [Blueprint Format Documentation](./BLUEPRINT_FORMAT.md) - Governance section configuration
- [Audit Logging Documentation](./AUDIT_LOGGING.md) - Approval logging requirements
