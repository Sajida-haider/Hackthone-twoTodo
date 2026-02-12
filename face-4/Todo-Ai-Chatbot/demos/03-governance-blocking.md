# Demo 3: Governance Blocking

## Overview

This demonstration shows how the Spec-Driven Infrastructure Automation system blocks forbidden operations immediately, preventing potentially dangerous actions.

**Scenario**: An agent or operator attempts to delete the `todo-frontend` deployment. The Governance Enforcer blocks this operation immediately and suggests safer alternatives.

**Agents Involved**:
- Decision Engine (proposes operation - in this case, triggered by external request)
- Governance Enforcer (classifies operation as "forbidden", blocks immediately)
- Audit Logger (logs the blocked attempt)

**Duration**: < 1 second (immediate blocking)

---

## Step 1: Initial Setup

### Blueprint Configuration

The `todo-frontend` service has the following governance configuration:

```yaml
# blueprints/frontend/blueprint.yaml
metadata:
  name: todo-frontend
  version: 1.0.0

governance:
  agent_authority:
    allowed_operations:
      - operation: scale_within_limits
        condition: target_replicas >= min_replicas AND target_replicas <= max_replicas
        autonomous: true

      - operation: adjust_resources
        condition: cpu_request >= 10m AND memory_request >= 64Mi
        autonomous: true

      - operation: restart_pods
        condition: restart_count < max_restart_count
        autonomous: true

    requires_approval:
      - operation: scale_beyond_limits
        condition: target_replicas > max_replicas
        risk_level: medium

      - operation: change_image
        condition: image_tag != current_image_tag
        risk_level: high

    forbidden_operations:
      - operation: delete_deployment
        rationale: "Deleting deployment causes complete service outage"
        alternatives: ["scale_to_zero", "disable_ingress", "rolling_update"]

      - operation: delete_persistent_volume
        rationale: "Data loss risk - PV deletion is irreversible"
        alternatives: ["backup_first", "manual_deletion_only"]

      - operation: modify_security_context
        rationale: "Security risk - requires security team review"
        alternatives: ["create_security_ticket"]
```

### Current State

```json
{
  "service": "todo-frontend",
  "replicas": 3,
  "pods_running": 3,
  "pods_ready": 3,
  "deployment_exists": true,
  "status": "healthy"
}
```

---

## Step 2: Forbidden Operation Attempt

### Scenario 1: Accidental Agent Decision

An agent (or misconfigured automation) attempts to delete the deployment:

```python
# Hypothetical agent logic (INCORRECT)
def handle_persistent_errors(service):
    if service.error_rate > 0.5:
        # WRONG: This is too aggressive
        return {
            "action": "delete_deployment",
            "rationale": "Service has high error rate, delete and recreate"
        }
```

### Scenario 2: External API Request

An external system sends a delete request:

```bash
# External automation attempt
curl -X POST http://agent-system/api/operations \
  -H "Content-Type: application/json" \
  -d '{
    "service": "todo-frontend",
    "operation": "delete_deployment",
    "rationale": "Cleanup unused deployment"
  }'
```

### Decision Proposal

```json
{
  "decision_id": "dec-20260210-180000-005",
  "decision_type": "deployment_management",
  "action": "delete_deployment",
  "service": "todo-frontend",
  "rationale": "Service experiencing persistent errors, attempting cleanup",
  "proposed_command": "kubectl delete deployment todo-frontend -n todo-app",
  "timestamp": "2026-02-10T18:00:00Z"
}
```

**Note**: This decision is immediately sent to Governance Enforcer before any execution.

---

## Step 3: Governance Check

The Governance Enforcer evaluates the operation:

### Governance Logic

```python
# Pseudocode from Governance Enforcer
def classify_operation(decision, blueprint):
    operation = decision.action

    # Check forbidden operations first (highest priority)
    for forbidden in blueprint.governance.agent_authority.forbidden_operations:
        if operation == forbidden.operation:
            return {
                "classification": "forbidden",
                "requires_approval": False,  # No approval can override
                "blocked": True,
                "rationale": forbidden.rationale,
                "alternatives": forbidden.alternatives,
                "immediate_action": "block_and_log"
            }

    # Check requires_approval
    # ... (not reached in this case)

    # Check allowed_operations
    # ... (not reached in this case)
```

### Governance Output

```json
{
  "governance_check_id": "gov-20260210-180000-003",
  "decision_id": "dec-20260210-180000-005",
  "timestamp": "2026-02-10T18:00:00.123Z",
  "classification": "forbidden",
  "requires_approval": false,
  "blocked": true,
  "execution_prevented": true,

  "rationale": "Deleting deployment causes complete service outage. This operation is forbidden by blueprint governance policy.",

  "blueprint_references": [
    "governance.agent_authority.forbidden_operations[0]"
  ],

  "risk_assessment": {
    "risk_level": "critical",
    "impact": "Complete service outage affecting all users",
    "data_loss_risk": false,
    "reversibility": "medium - requires redeployment",
    "blast_radius": "entire service"
  },

  "alternatives_suggested": [
    {
      "operation": "scale_to_zero",
      "description": "Scale deployment to 0 replicas instead of deleting",
      "command": "kubectl scale deployment todo-frontend --replicas=0 -n todo-app",
      "impact": "Service unavailable but deployment preserved",
      "reversibility": "high - can scale back up immediately",
      "rationale": "Achieves similar outcome without losing deployment configuration"
    },
    {
      "operation": "disable_ingress",
      "description": "Remove ingress rules to stop external traffic",
      "command": "kubectl delete ingress todo-frontend -n todo-app",
      "impact": "External traffic blocked, internal traffic still possible",
      "reversibility": "high - can recreate ingress",
      "rationale": "Stops traffic without affecting deployment"
    },
    {
      "operation": "rolling_update",
      "description": "Deploy new version with fixes instead of deleting",
      "command": "kubectl set image deployment/todo-frontend frontend=todo-frontend:v2 -n todo-app",
      "impact": "Zero-downtime update to new version",
      "reversibility": "high - can rollback",
      "rationale": "Fixes issues without service disruption"
    }
  ],

  "immediate_action": "block_and_log",
  "execution_status": "blocked",
  "notification_sent": true
}
```

**Result**: Operation is **FORBIDDEN** - blocked immediately, no execution possible.

**Reference**: See `examples/governance-forbidden.json` for complete governance check.

---

## Step 4: Blocking Response

The system immediately returns a blocking response:

### API Response (if triggered via API)

```json
{
  "status": "blocked",
  "code": 403,
  "message": "Operation forbidden by governance policy",
  "details": {
    "operation": "delete_deployment",
    "service": "todo-frontend",
    "classification": "forbidden",
    "rationale": "Deleting deployment causes complete service outage",
    "governance_check_id": "gov-20260210-180000-003"
  },
  "alternatives": [
    {
      "operation": "scale_to_zero",
      "description": "Scale deployment to 0 replicas instead of deleting",
      "recommended": true
    },
    {
      "operation": "disable_ingress",
      "description": "Remove ingress rules to stop external traffic"
    },
    {
      "operation": "rolling_update",
      "description": "Deploy new version with fixes instead of deleting"
    }
  ],
  "documentation": "https://docs.example.com/governance/forbidden-operations"
}
```

### Agent Response (if triggered by agent)

```python
# Agent receives blocking response
response = governance_enforcer.classify_operation(decision)

if response.classification == "forbidden":
    logger.error(f"Operation blocked: {response.rationale}")
    logger.info(f"Alternatives: {response.alternatives}")
    # Agent does NOT proceed with execution
    return {
        "status": "blocked",
        "reason": response.rationale,
        "alternatives": response.alternatives
    }
```

**Key Point**: No execution occurs. The operation is stopped at the governance check stage.

---

## Step 5: Audit Logging

The blocked attempt is logged for security audit:

### Audit Log Entry

```json
{
  "timestamp": "2026-02-10T18:00:00.123Z",
  "event_type": "operation_blocked",
  "log_id": "log-20260210-180000-006",
  "agent_id": "governance-enforcer-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",

  "blocked_operation": {
    "decision_id": "dec-20260210-180000-005",
    "operation": "delete_deployment",
    "proposed_command": "kubectl delete deployment todo-frontend -n todo-app",
    "rationale": "Service experiencing persistent errors, attempting cleanup"
  },

  "governance_decision": {
    "classification": "forbidden",
    "blocked": true,
    "rationale": "Deleting deployment causes complete service outage",
    "blueprint_reference": "governance.agent_authority.forbidden_operations[0]"
  },

  "source": {
    "trigger_type": "external_api",
    "source_ip": "10.0.1.50",
    "user_agent": "automation-script/1.0",
    "authenticated_user": "automation-service-account"
  },

  "alternatives_provided": [
    "scale_to_zero",
    "disable_ingress",
    "rolling_update"
  ],

  "security_impact": {
    "severity": "high",
    "potential_impact": "complete_service_outage",
    "prevented": true
  },

  "notification": {
    "security_team_notified": true,
    "notification_sent_at": "2026-02-10T18:00:00.200Z",
    "notification_channels": ["slack://security-alerts", "email://security@example.com"]
  },

  "outcome": "blocked",
  "execution_prevented": true
}
```

**Security Alert**: Security team is notified of the blocked attempt.

---

## Step 6: Security Notification

The security team receives an alert:

### Slack Notification

```
🚫 SECURITY ALERT: Forbidden Operation Blocked

Service: todo-frontend
Operation: delete_deployment
Classification: FORBIDDEN

Attempted Action: kubectl delete deployment todo-frontend -n todo-app
Rationale: "Service experiencing persistent errors, attempting cleanup"

Source:
- Trigger: External API
- IP: 10.0.1.50
- User: automation-service-account

Risk: Complete service outage (CRITICAL)
Status: ✅ BLOCKED by governance policy

Alternatives Suggested:
1. Scale to zero (recommended)
2. Disable ingress
3. Rolling update

[View Full Details] [Review Governance Policy]

Governance Check ID: gov-20260210-180000-003
```

### Email Notification

```
Subject: [SECURITY] Forbidden Operation Blocked: delete_deployment on todo-frontend

A forbidden operation was attempted and blocked by the governance system.

Operation Details:
- Service: todo-frontend
- Operation: delete_deployment
- Command: kubectl delete deployment todo-frontend -n todo-app
- Rationale: "Service experiencing persistent errors, attempting cleanup"

Source Information:
- Trigger Type: External API
- Source IP: 10.0.1.50
- User Agent: automation-script/1.0
- Authenticated User: automation-service-account

Governance Decision:
- Classification: FORBIDDEN
- Blocked: YES
- Rationale: Deleting deployment causes complete service outage

Risk Assessment:
- Severity: HIGH
- Potential Impact: Complete service outage affecting all users
- Blast Radius: Entire service
- Execution Prevented: YES

Recommended Alternatives:
1. Scale to zero: kubectl scale deployment todo-frontend --replicas=0 -n todo-app
2. Disable ingress: kubectl delete ingress todo-frontend -n todo-app
3. Rolling update: kubectl set image deployment/todo-frontend frontend=todo-frontend:v2 -n todo-app

Action Required:
- Review the source of this request (automation-service-account)
- Verify if this was intentional or misconfiguration
- Update automation scripts if necessary

[View Full Audit Log] [Review Governance Policy] [Contact Security Team]
```

---

## Step 7: Investigation and Resolution

### Investigation Steps

1. **Identify Source**: Check who/what triggered the delete operation
2. **Review Intent**: Was this intentional or a bug?
3. **Fix Root Cause**: Update automation scripts or agent logic
4. **Verify Governance**: Confirm governance policy is correct

### Example Investigation

```bash
# 1. Check audit logs
cat logs/agent-decisions/2026-02-10/blocked-operations.log | \
  jq '.source'

# Output:
{
  "trigger_type": "external_api",
  "source_ip": "10.0.1.50",
  "authenticated_user": "automation-service-account"
}

# 2. Check automation service account activity
kubectl logs -l app=automation-service -n automation --since=1h | \
  grep "delete_deployment"

# 3. Review automation script
cat /automation/scripts/cleanup.sh
# Found: Overly aggressive cleanup logic

# 4. Fix automation script
# Remove delete_deployment logic, replace with scale_to_zero
```

### Resolution

```bash
# Update automation script to use safer alternative
cat > /automation/scripts/cleanup.sh <<'EOF'
#!/bin/bash
# Safe cleanup: scale to zero instead of delete
kubectl scale deployment $SERVICE --replicas=0 -n $NAMESPACE
EOF

# Test with dry-run
./cleanup.sh --service todo-frontend --namespace todo-app --dry-run

# Verify governance allows scale_to_zero
curl -X POST http://agent-system/api/governance/check \
  -d '{"operation": "scale_to_zero", "service": "todo-frontend"}'
# Response: {"classification": "allowed"}
```

---

## Timeline Summary

```
18:00:00.000 - External API receives delete_deployment request
18:00:00.050 - Decision proposal created
18:00:00.100 - Governance Enforcer evaluates operation
18:00:00.123 - Operation classified as FORBIDDEN
18:00:00.123 - Execution blocked immediately
18:00:00.150 - Audit log entry created
18:00:00.200 - Security team notified
18:00:00.250 - Blocking response returned to caller

Total Duration: 250 milliseconds (immediate blocking)
```

**Key Point**: Entire process takes < 1 second. No execution occurs.

---

## Key Observations

### Immediate Blocking

✅ **No execution possible**
- Operation blocked at governance check stage
- No kubectl command executed
- No changes to cluster state
- Service remains healthy

### No Approval Override

✅ **Forbidden means forbidden**
- Cannot be overridden with approval
- No human can authorize forbidden operations
- Must modify blueprint to change policy
- Ensures critical safety boundaries

### Security Alerting

✅ **Security team notified**
- Immediate notification of blocked attempt
- Source information captured (IP, user, timestamp)
- Audit trail for compliance
- Enables investigation of potential security issues

### Alternative Suggestions

✅ **Helpful guidance provided**
- System suggests safer alternatives
- Each alternative includes description and command
- Alternatives achieve similar outcomes safely
- Reduces frustration from blocking

---

## Comparison: Forbidden vs Restricted vs Allowed

### Forbidden Operation (Demo 3)

- **Classification**: Forbidden
- **Approval**: Not possible (no override)
- **Execution**: Never
- **Duration**: < 1 second (immediate block)
- **Example**: Delete deployment

### Restricted Operation (Demo 2)

- **Classification**: Restricted
- **Approval**: Required
- **Execution**: After approval
- **Duration**: ~15 minutes (depends on approver)
- **Example**: Scale beyond max_replicas

### Allowed Operation (Demo 1)

- **Classification**: Allowed
- **Approval**: Not required
- **Execution**: Immediate
- **Duration**: ~2 minutes (includes verification)
- **Example**: Scale within limits

---

## When to Use Forbidden Operations

### Good Use Cases

✅ **Use forbidden for:**
- Operations causing data loss (delete PV, delete database)
- Operations causing complete outages (delete deployment, delete service)
- Security-sensitive operations (modify RBAC, change security context)
- Irreversible operations (delete backups, purge logs)

### Bad Use Cases

❌ **Don't use forbidden for:**
- Operations that should require approval (use "restricted" instead)
- Operations that are sometimes needed (provide approval path)
- Operations that can be safely automated (use "allowed" with conditions)

### Example: Delete PersistentVolume

```yaml
# GOOD: Forbidden with clear alternatives
forbidden_operations:
  - operation: delete_persistent_volume
    rationale: "Data loss risk - PV deletion is irreversible"
    alternatives: ["backup_first", "manual_deletion_only"]

# BAD: Allowed with approval (still too risky)
requires_approval:
  - operation: delete_persistent_volume  # ❌ Should be forbidden
    risk_level: critical
```

---

## Modifying Forbidden Operations

If a forbidden operation is genuinely needed:

### Option 1: Use Suggested Alternative

```bash
# Instead of: kubectl delete deployment todo-frontend
# Use: kubectl scale deployment todo-frontend --replicas=0
```

### Option 2: Manual Execution (Outside Agent System)

```bash
# Execute manually with proper authorization
kubectl delete deployment todo-frontend -n todo-app --as=admin

# Document in change ticket
# Bypass agent system governance (intentional)
```

### Option 3: Update Blueprint (Permanent Change)

```yaml
# Remove from forbidden_operations
# Add to requires_approval with strict conditions
requires_approval:
  - operation: delete_deployment
    condition: manual_approval_only
    risk_level: critical
    approvers: ["platform-team", "security-team"]
    requires_justification: true
    requires_backup: true
```

**Warning**: Removing forbidden operations should require security review.

---

## Try It Yourself

### Prerequisites

1. Kubernetes cluster with todo-frontend deployed
2. Blueprint with forbidden_operations configured
3. Agent system running
4. Security notifications configured

### Simulation Steps

```bash
# 1. Attempt forbidden operation via API
curl -X POST http://agent-system/api/operations \
  -H "Content-Type: application/json" \
  -d '{
    "service": "todo-frontend",
    "operation": "delete_deployment",
    "rationale": "Testing governance blocking"
  }'

# Expected response: 403 Forbidden

# 2. Check audit logs
cat logs/agent-decisions/$(date +%Y-%m-%d)/blocked-operations.log | \
  jq '.event_type == "operation_blocked"'

# 3. Verify deployment still exists
kubectl get deployment todo-frontend -n todo-app
# Should still exist (not deleted)

# 4. Try suggested alternative
kubectl scale deployment todo-frontend --replicas=0 -n todo-app
# Should succeed (allowed operation)

# 5. Check security notifications
# Check Slack #security-alerts channel
```

---

## Related Documentation

- **Governance**: `docs/GOVERNANCE.md`
- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`
- **Audit Logging**: `docs/AUDIT_LOGGING.md`
- **Security Best Practices**: `docs/SECURITY.md`

---

## Next Demos

- **Demo 4**: Rollback on Failure (automatic rollback when verification fails)
- **Demo 5**: Multi-Service Management (independent management of multiple services)
