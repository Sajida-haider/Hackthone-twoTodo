# Demo 2: Approval Workflow

## Overview

This demonstration shows how the Spec-Driven Infrastructure Automation system handles operations that require human approval before execution.

**Scenario**: The `todo-frontend` service is at maximum capacity (5 replicas) but still experiencing high load. The system needs to scale beyond the configured `max_replicas`, which requires human approval.

**Agents Involved**:
- Decision Engine (decides scaling is needed)
- Governance Enforcer (classifies operation as "restricted", generates approval request)
- Approval System (notifies approvers, collects response)
- Execution Engine (executes after approval)
- Verification Engine (verifies outcome)

**Duration**: ~15 minutes (including human approval time)

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
    max_replicas: 5  # Current limit
    target_cpu_utilization: 70%
    scale_up_threshold: 80%

governance:
  agent_authority:
    allowed_operations:
      - operation: scale_within_limits
        condition: target_replicas >= min_replicas AND target_replicas <= max_replicas
        autonomous: true

    requires_approval:
      - operation: scale_beyond_limits
        condition: target_replicas > max_replicas
        risk_level: medium
        approvers: ["devops-team"]

  approval_workflow:
    approvers: ["devops-team"]
    notification_channels: ["slack://devops-alerts"]
    timeout: 1h
    auto_reject_on_timeout: true
```

### Current State

```json
{
  "service": "todo-frontend",
  "replicas": 5,
  "max_replicas": 5,
  "pods_running": 5,
  "pods_ready": 5,
  "metrics": {
    "cpu_utilization": 0.92,
    "memory_utilization": 0.85,
    "latency_p95": 280,
    "error_rate": 0.012
  }
}
```

**Observation**:
- Service is at maximum capacity (5/5 replicas)
- CPU utilization is 92% (well above 80% threshold)
- Latency is 280ms (exceeds 200ms target)
- Error rate is 1.2% (elevated)

---

## Step 2: Metrics Collection

The monitoring system detects sustained high load:

```bash
# Metrics over 15-minute window
kubectl top pods -n todo-app -l app=todo-frontend

NAME                             CPU(cores)   MEMORY(bytes)
todo-frontend-7d8f9c5b6d-abc12   92m          435Mi
todo-frontend-7d8f9c5b6d-def34   92m          435Mi
todo-frontend-7d8f9c5b6d-ghi56   92m          435Mi
todo-frontend-7d8f9c5b6d-jkl78   92m          435Mi
todo-frontend-7d8f9c5b6d-mno90   92m          435Mi
```

**Calculated Metrics**:
- Average CPU: 92% (sustained for 15 minutes)
- Average Memory: 85%
- Latency P95: 280ms (target: 200ms)
- Error Rate: 1.2% (threshold: 1%)

**Weighted Utilization**: (0.92 × 0.5) + (0.85 × 0.3) + (1.40 × 0.2) = **0.995** (99.5%)

**Critical**: Service is severely overloaded despite being at maximum capacity.

---

## Step 3: Decision Engine Analysis

The Decision Engine analyzes the situation:

### Decision Logic

```python
# Pseudocode from Decision Engine
def make_scaling_decision(metrics, blueprint):
    weighted_util = calculate_weighted_utilization(metrics)
    current_replicas = metrics.replicas
    max_replicas = blueprint.spec.scaling.max_replicas

    if weighted_util > blueprint.scale_up_threshold:
        # Calculate target replicas
        target_replicas = calculate_target_replicas(
            current_replicas,
            weighted_util,
            blueprint.target_cpu_utilization
        )

        # Check if beyond limits
        if target_replicas > max_replicas:
            return {
                "action": "scale_beyond_limits",
                "current_replicas": current_replicas,
                "target_replicas": target_replicas,
                "max_replicas": max_replicas,
                "rationale": f"Service overloaded (util: {weighted_util}), needs scaling beyond max_replicas",
                "urgency": "high"
            }
```

### Decision Output

```json
{
  "decision_id": "dec-20260210-165500-004",
  "decision_type": "scaling",
  "action": "scale_beyond_limits",
  "current_replicas": 5,
  "target_replicas": 6,
  "max_replicas": 5,
  "rationale": "Sustained high load (92% CPU) for 15 minutes. Latency (280ms) exceeds target (200ms). Error rate (1.2%) above threshold. Need to scale beyond current max_replicas.",
  "weighted_utilization": 0.995,
  "urgency": "high",
  "expected_outcome": {
    "replicas": 6,
    "expected_cpu_utilization": 0.77,
    "expected_memory_utilization": 0.71,
    "expected_latency_p95": 200
  }
}
```

**Decision**: Scale from 5 to 6 replicas (beyond max_replicas of 5).

---

## Step 4: Governance Check

The Governance Enforcer validates the decision:

### Governance Logic

```python
# Pseudocode from Governance Enforcer
def classify_operation(decision, blueprint):
    target_replicas = decision.target_replicas
    max_replicas = blueprint.spec.scaling.max_replicas

    # Check if beyond limits
    if target_replicas > max_replicas:
        # Check requires_approval rules
        for rule in blueprint.governance.agent_authority.requires_approval:
            if rule.operation == "scale_beyond_limits":
                return {
                    "classification": "restricted",
                    "requires_approval": True,
                    "approvers": rule.approvers,
                    "risk_level": rule.risk_level,
                    "rationale": f"Target replicas ({target_replicas}) exceeds max_replicas ({max_replicas})"
                }
```

### Governance Output

```json
{
  "governance_check_id": "gov-20260210-170000-002",
  "decision_id": "dec-20260210-165500-004",
  "classification": "restricted",
  "requires_approval": true,
  "rationale": "Target replicas (6) exceeds max_replicas (5). Operation requires human approval.",
  "blueprint_references": [
    "spec.scaling.max_replicas",
    "governance.agent_authority.requires_approval[0]"
  ],
  "risk_assessment": {
    "risk_level": "medium",
    "cost_impact": "+$20/month (20% increase)",
    "performance_impact": "Expected improvement in latency and error rate",
    "reversibility": "high"
  }
}
```

**Result**: Operation is **RESTRICTED** - requires approval before execution.

**Reference**: See `examples/governance-restricted.json` for complete governance check.

---

## Step 5: Approval Request Generation

The Governance Enforcer generates an approval request:

### Approval Request

```json
{
  "approval_request_id": "apr-20260210-170000-002",
  "created_at": "2026-02-10T17:00:00Z",
  "decision_id": "dec-20260210-165500-004",
  "service": "todo-frontend",
  "operation": "scale_beyond_limits",

  "current_state": {
    "replicas": 5,
    "max_replicas": 5,
    "cpu_utilization": 0.92,
    "latency_p95": 280,
    "error_rate": 0.012
  },

  "proposed_change": {
    "action": "scale_up",
    "from_replicas": 5,
    "to_replicas": 6,
    "requires_blueprint_update": true,
    "new_max_replicas": 6
  },

  "rationale": "Service experiencing sustained high load for 15 minutes. CPU at 92%, latency 280ms (target 200ms), error rate 1.2% (threshold 1%). Current max_replicas (5) insufficient. Recommend scaling to 6 replicas.",

  "risk_assessment": {
    "risk_level": "medium",
    "cost_impact": "+$20/month (20% increase)",
    "performance_impact": "Expected 15% CPU reduction, latency improvement to ~200ms",
    "reversibility": "high - can scale down if load decreases",
    "blast_radius": "single service (todo-frontend)"
  },

  "alternatives_considered": [
    {
      "option": "Optimize code",
      "timeline": "days-weeks",
      "rejected_reason": "Too slow for immediate issue"
    },
    {
      "option": "Increase resource limits",
      "impact": "May not solve replica-level bottlenecks",
      "rejected_reason": "Scaling more effective for distributed load"
    }
  ],

  "approval_workflow": {
    "approvers": ["devops-team"],
    "timeout": "1h",
    "timeout_at": "2026-02-10T18:00:00Z",
    "auto_reject_on_timeout": true
  }
}
```

---

## Step 6: Notification to Approvers

The system sends notifications to the DevOps team:

### Slack Notification

```
🚨 Approval Required: Scale todo-frontend beyond limits

Service: todo-frontend
Current: 5 replicas (at max_replicas limit)
Proposed: 6 replicas (requires increasing max_replicas)

Reason: Sustained high load (92% CPU, 280ms latency, 1.2% errors)

Risk: Medium
Cost: +$20/month (20% increase)
Reversibility: High

[Approve] [Reject] [View Details]

Timeout: 1 hour (auto-reject if no response)
Request ID: apr-20260210-170000-002
```

### Email Notification

```
Subject: [Action Required] Approval Request: Scale todo-frontend

The agent system has requested approval to scale todo-frontend beyond configured limits.

Current State:
- Replicas: 5/5 (at maximum)
- CPU: 92% (sustained for 15 minutes)
- Latency: 280ms (target: 200ms)
- Error Rate: 1.2% (threshold: 1%)

Proposed Action:
- Scale from 5 to 6 replicas
- Update max_replicas from 5 to 6

Risk Assessment:
- Risk Level: Medium
- Cost Impact: +$20/month (20% increase)
- Performance Impact: Expected 15% CPU reduction
- Reversibility: High (can scale down later)

Please review and approve/reject within 1 hour.

[Approve] [Reject] [View Full Details]
```

**Notification Sent**: 2026-02-10T17:00:05Z (5 seconds after request created)

---

## Step 7: Human Review and Approval

A DevOps engineer reviews the request:

### Review Process

1. **Check Metrics**: Verify CPU, latency, error rate in monitoring dashboard
2. **Review History**: Check if this is a recurring pattern or one-time spike
3. **Assess Cost**: Confirm $20/month increase is acceptable
4. **Consider Alternatives**: Verify alternatives were considered
5. **Make Decision**: Approve or reject based on analysis

### Approval Response

```json
{
  "approval_response_id": "apr-resp-20260210-171500-001",
  "approval_request_id": "apr-20260210-170000-002",
  "status": "approved",
  "approver": "john.doe@example.com",
  "approver_role": "devops-team",
  "approved_at": "2026-02-10T17:15:00Z",
  "response_time": "15 minutes",
  "comment": "Approved - performance issue confirmed, cost increase justified. Monitor closely after scaling.",
  "approval_method": "slack_button"
}
```

**Decision**: **APPROVED** by john.doe@example.com at 17:15:00Z (15 minutes after request)

**Reference**: See `examples/audit-approval.json` for complete approval log.

---

## Step 8: Blueprint Update

Before execution, the blueprint is updated to reflect the new limit:

### Blueprint Update

```yaml
# blueprints/frontend/blueprint.yaml (updated)
spec:
  scaling:
    min_replicas: 1
    max_replicas: 6  # Updated from 5 to 6
    target_cpu_utilization: 70%
```

### Update Log

```json
{
  "blueprint_update_id": "bp-update-20260210-171500-001",
  "timestamp": "2026-02-10T17:15:05Z",
  "service": "todo-frontend",
  "changes": [
    {
      "field": "spec.scaling.max_replicas",
      "old_value": 5,
      "new_value": 6,
      "reason": "Approved scaling beyond previous limit"
    }
  ],
  "approved_by": "john.doe@example.com",
  "approval_id": "apr-20260210-170000-002"
}
```

**Note**: Blueprint update is permanent, not temporary. Future scaling to 6 replicas will be autonomous.

---

## Step 9: Execution

The Execution Engine executes the scaling operation:

### Execution Command

```bash
kubectl scale deployment todo-frontend --replicas=6 -n todo-app
```

### Execution Output

```json
{
  "operation_id": "dec-20260210-165500-004",
  "operation_type": "scale_beyond_limits",
  "execution": {
    "started_at": "2026-02-10T17:15:10Z",
    "completed_at": "2026-02-10T17:15:12Z",
    "duration": "2.1s",
    "exit_code": 0,
    "stdout": "deployment.apps/todo-frontend scaled",
    "stderr": ""
  },
  "authorization": {
    "approval_id": "apr-20260210-170000-002",
    "approved_by": "john.doe@example.com",
    "approved_at": "2026-02-10T17:15:00Z"
  },
  "post_operation_state": {
    "replicas": 6,
    "pods_running": 5,
    "pods_ready": 5,
    "pods_pending": 1
  }
}
```

**Result**: Deployment scaled successfully. New pod is starting.

---

## Step 10: Stabilization Period

The system waits 60 seconds for the new pod to start:

```bash
# Watch pod status
kubectl get pods -n todo-app -l app=todo-frontend -w

NAME                             READY   STATUS    RESTARTS   AGE
todo-frontend-7d8f9c5b6d-abc12   1/1     Running   0          30m
todo-frontend-7d8f9c5b6d-def34   1/1     Running   0          30m
todo-frontend-7d8f9c5b6d-ghi56   1/1     Running   0          30m
todo-frontend-7d8f9c5b6d-jkl78   1/1     Running   0          30m
todo-frontend-7d8f9c5b6d-mno90   1/1     Running   0          30m
todo-frontend-7d8f9c5b6d-pqr12   0/1     Pending   0          2s
todo-frontend-7d8f9c5b6d-pqr12   0/1     ContainerCreating   0          5s
todo-frontend-7d8f9c5b6d-pqr12   1/1     Running             0          48s
```

**Stabilization**: 60 seconds configured in blueprint.

---

## Step 11: Verification

The Verification Engine verifies the operation was successful:

### Verification Output

```json
{
  "verification_id": "ver-20260210-171630-007",
  "operation_id": "dec-20260210-165500-004",
  "verification_timestamp": "2026-02-10T17:16:30Z",
  "outcome": "success",

  "checks": [
    {
      "check": "replica_count",
      "expected": 6,
      "actual": 6,
      "status": "passed"
    },
    {
      "check": "pods_ready",
      "expected": 6,
      "actual": 6,
      "status": "passed"
    },
    {
      "check": "cpu_utilization",
      "expected": "< 80%",
      "actual": "77%",
      "status": "passed",
      "improvement": "15% reduction (92% → 77%)"
    },
    {
      "check": "memory_utilization",
      "expected": "< 80%",
      "actual": "71%",
      "status": "passed"
    },
    {
      "check": "latency_p95",
      "expected": "< 200ms",
      "actual": "195ms",
      "status": "passed",
      "improvement": "85ms reduction (280ms → 195ms)"
    },
    {
      "check": "error_rate",
      "expected": "< 1%",
      "actual": "0.4%",
      "status": "passed",
      "improvement": "67% reduction (1.2% → 0.4%)"
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

**Result**: All checks passed. Performance significantly improved.

---

## Step 12: Post-Approval Notification

The approver is notified of the successful execution:

### Slack Notification

```
✅ Approval Executed Successfully: todo-frontend scaled to 6 replicas

Your approval (apr-20260210-170000-002) has been executed.

Results:
- Replicas: 5 → 6 ✓
- CPU: 92% → 77% (15% improvement)
- Latency: 280ms → 195ms (85ms improvement)
- Error Rate: 1.2% → 0.4% (67% improvement)

All verification checks passed.

Blueprint updated: max_replicas increased from 5 to 6.
Future scaling to 6 replicas will be autonomous.

[View Full Report]
```

---

## Timeline Summary

```
17:00:00 - High load detected (92% CPU, 280ms latency)
17:00:00 - Decision Engine: Scale from 5 to 6 replicas (beyond max)
17:00:00 - Governance Enforcer: Operation restricted, requires approval
17:00:00 - Approval request generated
17:00:05 - Notifications sent to DevOps team (Slack, Email)
17:15:00 - Human approval received (john.doe@example.com)
17:15:05 - Blueprint updated (max_replicas: 5 → 6)
17:15:10 - Execution Engine: kubectl scale executed (2.1s)
17:15:12 - New pod starting
17:16:00 - New pod ready (48s startup time)
17:16:30 - Verification Engine: All checks passed
17:16:30 - Approver notified of success

Total Duration: 16.5 minutes (including 15 minutes human approval time)
Automated Duration: 1.5 minutes (excluding human approval)
```

---

## Key Observations

### Human-in-the-Loop

✅ **Approval required for risky operations**
- Operation exceeded blueprint limits
- Governance classified as "restricted"
- Human approval obtained before execution
- Approver provided justification

### Risk Assessment

✅ **Comprehensive risk evaluation**
- Cost impact calculated (+$20/month)
- Performance impact estimated
- Reversibility assessed (high)
- Alternatives considered

### Blueprint Evolution

✅ **Blueprint updated after approval**
- max_replicas increased from 5 to 6
- Change is permanent, not temporary
- Future scaling to 6 replicas will be autonomous
- Blueprint reflects current operational reality

### Audit Trail

✅ **Complete approval workflow logged**
- Approval request with rationale
- Notification delivery confirmed
- Human approval with comment
- Execution authorization
- Verification results
- Post-approval notification

---

## What Makes This Different from Autonomous?

### Autonomous Operation (Demo 1)

- Operation within blueprint limits
- No approval required
- Executes immediately
- Duration: ~2 minutes

### Approval Workflow (Demo 2)

- Operation beyond blueprint limits
- Approval required
- Waits for human decision
- Duration: ~15 minutes (depends on approver availability)

**Key Difference**: Human judgment for operations outside normal parameters.

---

## Approval Decision Factors

### When to Approve

✅ **Approve if:**
- Performance issue is real and sustained
- Cost increase is justified
- No better alternatives available
- Risk is acceptable
- Reversibility is high

### When to Reject

❌ **Reject if:**
- Issue is temporary spike (not sustained)
- Cost increase is too high
- Better alternatives exist (code optimization)
- Risk is too high
- Insufficient justification

### Example Rejection

```json
{
  "status": "rejected",
  "approver": "jane.smith@example.com",
  "rejected_at": "2026-02-10T17:15:00Z",
  "comment": "Rejected - this appears to be a temporary spike. Let's wait 30 minutes to see if load decreases naturally. If sustained, we'll approve then.",
  "alternative_action": "Monitor for 30 minutes, re-evaluate if load remains high"
}
```

---

## Timeout Scenario

If no approval is received within 1 hour:

```json
{
  "approval_request_id": "apr-20260210-170000-002",
  "status": "timeout",
  "timeout_at": "2026-02-10T18:00:00Z",
  "auto_rejected": true,
  "outcome": "Operation not executed due to timeout",
  "escalation": "Alert on-call team about unresolved high load"
}
```

**Result**: Operation blocked, on-call team alerted for manual intervention.

---

## Try It Yourself

### Prerequisites

1. Kubernetes cluster with todo-frontend deployed
2. Blueprint configured with max_replicas limit
3. Agent system running
4. Slack/Email notifications configured

### Simulation Steps

```bash
# 1. Set max_replicas to low value (e.g., 3)
kubectl edit deployment todo-frontend -n todo-app
# Set replicas to 3

# 2. Simulate high load
kubectl run load-generator --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://todo-frontend:3000; done"

# 3. Watch for approval request
# Check Slack channel or email

# 4. Approve via Slack button or API
curl -X POST http://agent-system/api/approvals/apr-xxx/approve \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"approver": "your.email@example.com", "comment": "Approved for demo"}'

# 5. Watch execution
kubectl get pods -n todo-app -l app=todo-frontend -w

# 6. Check audit logs
cat logs/agent-decisions/$(date +%Y-%m-%d)/approvals.log | jq '.'
```

---

## Related Documentation

- **Governance**: `docs/GOVERNANCE.md`
- **Approval Workflow**: `docs/APPROVAL_WORKFLOW.md`
- **Audit Logging**: `docs/AUDIT_LOGGING.md`
- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`

---

## Next Demos

- **Demo 3**: Governance Blocking (forbidden operation blocked immediately)
- **Demo 4**: Rollback on Failure (automatic rollback when verification fails)
- **Demo 5**: Multi-Service Management (independent management of multiple services)
