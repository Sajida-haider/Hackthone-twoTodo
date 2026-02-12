# Audit Logging Documentation

## Overview

Audit logging provides a complete, immutable record of all agent decisions, operations, and governance checks. Logs are structured in JSON format for easy analysis and compliance.

**Key Principle**: Every decision and operation must be logged with complete context and rationale.

## Log Format

All audit logs use structured JSON format with consistent fields.

### Standard Log Structure

```json
{
  "timestamp": "ISO 8601 timestamp",
  "event_type": "event_category",
  "agent_id": "agent_identifier",
  "service": "service_name",
  "blueprint_version": "version",
  "event_details": { /* event-specific data */ },
  "outcome": "success | failure | blocked",
  "duration": "execution_time_ms"
}
```

## Log Types

### 1. Decision Logs

Record agent decisions with rationale and blueprint references.

**Format**:
```json
{
  "timestamp": "2026-02-10T15:30:00Z",
  "event_type": "decision_made",
  "agent_id": "decision-engine-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "decision": {
    "decision_id": "dec-20260210-153000-001",
    "decision_type": "scaling",
    "current_state": {
      "replicas": 2,
      "cpu_utilization": 0.85,
      "memory_utilization": 0.70
    },
    "recommended_action": {
      "action": "scale_up",
      "target_replicas": 3
    },
    "rationale": "Weighted utilization (81.5%) exceeds scale_up_threshold (80%)",
    "blueprint_references": [
      "spec.scaling.scale_up_threshold",
      "spec.scaling.max_replicas"
    ],
    "metrics_breakdown": {
      "cpu": 0.85,
      "memory": 0.70,
      "weighted": 0.815
    }
  },
  "outcome": "decision_made"
}
```

### 2. Operation Logs

Record operation execution with commands and results.

**Format**:
```json
{
  "timestamp": "2026-02-10T15:30:45Z",
  "event_type": "operation_executed",
  "agent_id": "execution-engine-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "operation": {
    "operation_id": "dec-20260210-153000-001",
    "operation_type": "scale_up",
    "command": "kubectl scale deployment todo-frontend --replicas=3 -n todo-app",
    "execution_method": "kubectl",
    "dry_run": false
  },
  "result": {
    "exit_code": 0,
    "stdout": "deployment.apps/todo-frontend scaled",
    "stderr": ""
  },
  "outcome": "success",
  "duration": "2.3s"
}
```

### 3. Governance Logs

Record governance checks and classifications.

**Format**:
```json
{
  "timestamp": "2026-02-10T15:30:30Z",
  "event_type": "governance_check",
  "agent_id": "governance-enforcer-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "governance": {
    "check_id": "gov-20260210-153030-001",
    "operation_id": "dec-20260210-153000-001",
    "operation_type": "scale_up",
    "classification": "allowed",
    "tier": 1,
    "requires_approval": false,
    "rationale": "Target replicas (3) within blueprint limits (1-5)",
    "blueprint_references": [
      "governance.agent_authority.allowed_operations[0]",
      "spec.scaling.min_replicas",
      "spec.scaling.max_replicas"
    ]
  },
  "outcome": "allowed"
}
```

### 4. Verification Logs

Record post-operation verification results.

**Format**:
```json
{
  "timestamp": "2026-02-10T15:32:00Z",
  "event_type": "verification_completed",
  "agent_id": "verification-engine-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "verification": {
    "verification_id": "ver-20260210-153200-001",
    "operation_id": "dec-20260210-153000-001",
    "verification_status": "passed",
    "checks_performed": 8,
    "checks_passed": 8,
    "checks_failed": 0,
    "post_operation_metrics": {
      "cpu_utilization": 0.60,
      "memory_utilization": 0.50,
      "latency_p95": 150
    },
    "targets_met": true,
    "rollback_triggered": false
  },
  "outcome": "success",
  "duration": "62s"
}
```

### 5. Approval Logs

Record approval requests and responses.

**Format**:
```json
{
  "timestamp": "2026-02-10T17:00:00Z",
  "event_type": "approval_requested",
  "agent_id": "governance-enforcer-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "approval": {
    "request_id": "apr-20260210-170000-001",
    "operation_type": "scale_beyond_limits",
    "current_state": {"replicas": 5, "max_replicas": 5},
    "proposed_state": {"replicas": 6},
    "rationale": "High load (92% utilization), need to exceed max_replicas",
    "approvers": ["devops-team"],
    "timeout": "1h"
  },
  "outcome": "pending"
}
```

### 6. Rollback Logs

Record rollback triggers and execution.

**Format**:
```json
{
  "timestamp": "2026-02-10T16:52:30Z",
  "event_type": "rollback_triggered",
  "agent_id": "verification-engine-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "rollback": {
    "rollback_id": "rbk-20260210-165230-001",
    "operation_id": "dec-20260210-164500-007",
    "trigger_reason": "verification_failed",
    "failed_checks": ["latency_p95", "error_rate"],
    "rollback_action": "scale_up",
    "rollback_command": "kubectl scale deployment todo-frontend --replicas=3",
    "rollback_status": "success"
  },
  "outcome": "success",
  "duration": "65s"
}
```

## Required Fields

Every log entry must include:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `timestamp` | ISO 8601 | When event occurred | Yes |
| `event_type` | String | Type of event | Yes |
| `agent_id` | String | Which agent logged event | Yes |
| `service` | String | Which service affected | Yes |
| `blueprint_version` | String | Blueprint version used | Yes |
| `outcome` | String | Result of event | Yes |

## Log Storage

### Directory Structure

```
logs/
├── agent-decisions/
│   ├── 2026-02-10/
│   │   ├── decisions.log
│   │   ├── operations.log
│   │   ├── governance.log
│   │   └── verifications.log
│   └── 2026-02-11/
│       └── ...
└── archive/
    └── 2025-11/
        └── ...
```

### File Naming Convention

```
logs/agent-decisions/YYYY-MM-DD/event-type.log
```

### Log Rotation

- **Daily Rotation**: New log files created daily
- **Retention**: 90 days (configurable)
- **Archive**: Older logs moved to archive directory
- **Compression**: Archived logs compressed (gzip)

## Log Retention Policy

### Retention Periods

| Log Type | Retention | Rationale |
|----------|-----------|-----------|
| Decision Logs | 90 days | Compliance and analysis |
| Operation Logs | 90 days | Audit trail |
| Governance Logs | 90 days | Security and compliance |
| Verification Logs | 30 days | Operational analysis |
| Approval Logs | 365 days | Long-term audit |

### Retention Configuration

```yaml
governance:
  audit:
    retention_period: 90d
    archive_after: 30d
    compress_archives: true
    delete_after_retention: true
```

## Log Analysis

### Query Examples

**Find all scaling decisions**:
```bash
cat logs/agent-decisions/2026-02-10/decisions.log | \
  jq 'select(.decision.decision_type == "scaling")'
```

**Find failed operations**:
```bash
cat logs/agent-decisions/2026-02-10/operations.log | \
  jq 'select(.outcome == "failure")'
```

**Find approval requests**:
```bash
cat logs/agent-decisions/2026-02-10/governance.log | \
  jq 'select(.event_type == "approval_requested")'
```

**Count operations by type**:
```bash
cat logs/agent-decisions/2026-02-10/operations.log | \
  jq -r '.operation.operation_type' | sort | uniq -c
```

**Find rollbacks**:
```bash
cat logs/agent-decisions/2026-02-10/verifications.log | \
  jq 'select(.event_type == "rollback_triggered")'
```

## Log Aggregation

### Centralized Logging

For production deployments, aggregate logs to centralized system:

**Options**:
- **Elasticsearch**: Full-text search and analysis
- **Splunk**: Enterprise log management
- **CloudWatch**: AWS-native logging
- **Datadog**: Monitoring and logging platform

**Example (Elasticsearch)**:
```bash
# Ship logs to Elasticsearch
filebeat -c filebeat.yml
```

**filebeat.yml**:
```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/agent-decisions/*.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "agent-decisions-%{+yyyy.MM.dd}"
```

## Log Security

### Access Control

- **Read Access**: DevOps team, security team
- **Write Access**: Agent processes only
- **Admin Access**: Platform administrators

### Immutability

- Logs are append-only
- No modification or deletion allowed
- Tampering detection via checksums

### Encryption

- **At Rest**: Logs encrypted on disk
- **In Transit**: TLS for log shipping
- **Backup**: Encrypted backups

## Compliance

### Audit Requirements

Logs must support:
- **SOC 2**: Security and availability controls
- **GDPR**: Data processing records
- **HIPAA**: Access and modification tracking
- **PCI DSS**: Change tracking

### Compliance Fields

```json
{
  "compliance": {
    "data_classification": "internal",
    "retention_required": true,
    "pii_present": false,
    "audit_category": "infrastructure_change"
  }
}
```

## Monitoring and Alerts

### Key Metrics from Logs

- **Decision Rate**: Decisions per hour
- **Operation Success Rate**: % successful operations
- **Approval Request Rate**: Approvals per day
- **Rollback Rate**: % operations rolled back
- **Governance Block Rate**: % operations blocked

### Alert Conditions

```yaml
alerts:
  - name: High Rollback Rate
    condition: rollback_rate > 10%
    severity: warning

  - name: Governance Blocks Increasing
    condition: governance_blocks > 5 per hour
    severity: info

  - name: Operation Failures
    condition: operation_failures > 3 per hour
    severity: critical
```

## Best Practices

1. **Log Everything**: Every decision, operation, and check
2. **Structured Format**: Always use JSON for consistency
3. **Include Context**: Blueprint version, rationale, references
4. **Immutable Logs**: Never modify or delete logs
5. **Regular Analysis**: Review logs weekly for patterns
6. **Secure Storage**: Encrypt and control access
7. **Retention Policy**: Follow compliance requirements
8. **Centralize**: Aggregate logs for analysis

## Troubleshooting

### Problem: Logs growing too large

**Solutions**:
- Enable log rotation
- Compress archived logs
- Reduce log verbosity
- Archive to cold storage

### Problem: Cannot find specific events

**Solutions**:
- Use structured queries (jq)
- Index logs in Elasticsearch
- Add more searchable fields
- Improve log filtering

### Problem: Logs missing events

**Solutions**:
- Verify agent logging configuration
- Check disk space
- Review log rotation settings
- Ensure all agents logging correctly

## See Also

- [Governance Documentation](./GOVERNANCE.md) - What gets logged
- [Decision Engine Documentation](./DECISION_ENGINE.md) - Decision logging
- [Verification Documentation](./VERIFICATION_ENGINE.md) - Verification logging
