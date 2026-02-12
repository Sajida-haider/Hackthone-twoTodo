# Blueprint Format Documentation

## Overview

Infrastructure blueprints are YAML documents that define how AI agents should manage infrastructure. They serve as the **single source of truth** for infrastructure requirements, performance targets, scaling policies, and governance rules.

**Key Concept**: Instead of humans making ad-hoc infrastructure decisions, agents read blueprints and make autonomous decisions based on the policies defined within.

## Blueprint Structure

A blueprint consists of four main sections:

```yaml
apiVersion: infra.spec-driven.io/v1
kind: InfrastructureBlueprint

metadata:        # Identifies the blueprint
spec:            # Defines infrastructure requirements
governance:      # Defines agent authority and safety rules
cost:            # Optional cost targets (simulated)
```

## Section 1: Metadata

The metadata section identifies the blueprint and tracks versioning.

```yaml
metadata:
  name: todo-frontend              # Unique name (lowercase, hyphens)
  version: 1.0.0                   # Semantic version
  owner: devops-team               # Responsible team/person
  description: "..."               # Human-readable description
  created: "2026-02-10T00:00:00Z"  # ISO 8601 timestamp
```

**Purpose**: Agents use metadata to identify which blueprint governs which service, track versions for audit logs, and determine ownership for approval workflows.

**Versioning**: Follow semantic versioning (major.minor.patch):
- **Major**: Breaking changes to schema or governance rules
- **Minor**: New policies or targets added
- **Patch**: Value adjustments (e.g., changing threshold from 80% to 85%)

## Section 2: Spec

The spec section defines infrastructure requirements and targets. It has five subsections:

### 2.1 Resources

Defines CPU, memory, and disk requirements.

```yaml
spec:
  resources:
    cpu:
      request: 50m                    # Guaranteed allocation
      limit: 200m                     # Maximum allowed
      target_utilization: 70%         # Target usage
      optimization_threshold: 10%     # When to optimize

    memory:
      request: 128Mi
      limit: 512Mi
      target_utilization: 80%
      optimization_threshold: 10%

    disk:
      ephemeral_storage: 1Gi
```

**How Agents Use This**:
- **Request**: Agents ensure pods get at least this much
- **Limit**: Agents prevent pods from exceeding this
- **Target Utilization**: Agents optimize to achieve this usage level
- **Optimization Threshold**: Agents recommend changes if actual usage differs by more than this percentage

**Example Decision**: If CPU usage is 30% and target is 70%, and the difference (40%) exceeds the optimization threshold (10%), the agent recommends reducing CPU request.

### 2.2 Performance

Defines performance targets that agents must maintain.

```yaml
spec:
  performance:
    latency_p50: 100ms              # 50th percentile target
    latency_p95: 200ms              # 95th percentile target (PRIMARY)
    latency_p99: 500ms              # 99th percentile target
    throughput_min: 100 req/s       # Minimum throughput
    throughput_target: 200 req/s    # Target throughput
    availability: 99.9%             # Availability target
    error_rate_max: 1%              # Maximum error rate
```

**How Agents Use This**:
- Agents monitor these metrics continuously
- If metrics violate targets, agents take action (scale up, rollback, etc.)
- Agents use these targets to verify operations succeeded

**Example Decision**: If latency_p95 exceeds 200ms after scaling down, the agent triggers a rollback.

### 2.3 Scaling

Defines scaling policies for autonomous scaling decisions.

```yaml
spec:
  scaling:
    min_replicas: 1                 # Minimum replicas
    max_replicas: 5                 # Maximum replicas
    target_replicas: 2              # Target under normal load
    scale_up_threshold: 80%         # Scale up when > 80%
    scale_down_threshold: 30%       # Scale down when < 30%
    scale_up_increment: 1           # Add 1 replica at a time
    scale_down_increment: 1         # Remove 1 replica at a time
    cooldown_period: 60s            # Wait between operations
    metrics:
      - type: cpu
        weight: 0.5                 # CPU is 50% of decision
      - type: memory
        weight: 0.3                 # Memory is 30% of decision
      - type: latency
        weight: 0.2                 # Latency is 20% of decision
```

**How Agents Use This**:
- Agents monitor utilization continuously
- When utilization > scale_up_threshold, agents scale up (if < max_replicas)
- When utilization < scale_down_threshold, agents scale down (if > min_replicas)
- Agents respect cooldown_period to prevent rapid oscillation
- Agents combine metrics using weights to make scaling decisions

**Example Decision**:
```
Current state: 2 replicas, CPU 85%, memory 70%, latency 180ms
Weighted utilization: (0.85 * 0.5) + (0.70 * 0.3) + (0.90 * 0.2) = 0.815 = 81.5%
Decision: 81.5% > 80% threshold → Scale up to 3 replicas
```

### 2.4 Reliability

Defines failure recovery policies.

```yaml
spec:
  reliability:
    max_restart_count: 3            # Max restarts before escalation
    restart_backoff: exponential    # Backoff strategy
    rollback_on_failure: true       # Auto-rollback on failure
    rollback_threshold: 2           # Failures before rollback
    health_check_timeout: 30s       # Health check timeout

    readiness_probe:
      initial_delay: 10s            # Wait before first check
      period: 10s                   # Check frequency
      timeout: 5s                   # Check timeout
      failure_threshold: 3          # Failures before unready

    liveness_probe:
      initial_delay: 30s
      period: 30s
      timeout: 5s
      failure_threshold: 3
```

**How Agents Use This**:
- When pod fails, agents restart it (if RestartCount < max_restart_count)
- If pod fails repeatedly (≥ rollback_threshold), agents trigger rollback
- Agents use probe settings to detect unhealthy pods

**Example Decision**: Pod has RestartCount=2 (< max 3) → Agent restarts pod. Pod has RestartCount=3 (≥ max 3) → Agent escalates to approval workflow.

### 2.5 Deployment

Defines how updates are rolled out.

```yaml
spec:
  deployment:
    strategy: RollingUpdate         # Deployment strategy
    max_surge: 1                    # Max extra pods during update
    max_unavailable: 0              # Max unavailable during update
    min_ready_seconds: 10           # Seconds before considered ready
    revision_history_limit: 5       # Old ReplicaSets to keep
```

**How Agents Use This**:
- Agents use these settings when applying updates
- Agents ensure zero-downtime deployments (max_unavailable: 0)
- Agents keep revision history for rollback capability

## Section 3: Governance

The governance section defines agent authority and safety rules. It has three subsections:

### 3.1 Agent Authority

Defines what agents can and cannot do using a three-tier classification.

```yaml
governance:
  agent_authority:

    # Tier 1: Allowed (autonomous, no approval)
    allowed_operations:
      - scale_within_limits
      - restart_failed_pods
      - adjust_resources_within_10_percent

    # Tier 2: Restricted (require approval)
    requires_approval:
      - scale_beyond_limits
      - change_resource_limits_beyond_10_percent
      - modify_deployment_strategy

    # Tier 3: Forbidden (blocked, never allowed)
    forbidden_operations:
      - delete_deployment
      - delete_service
      - modify_secrets
```

**How Agents Use This**:
1. Before any operation, agents check governance rules
2. **Allowed**: Agent executes autonomously
3. **Restricted**: Agent requests human approval
4. **Forbidden**: Agent blocks operation and suggests alternative

**Example Decision Flow**:
```
Operation: Scale to 3 replicas
Current: 2 replicas, max_replicas: 5
Check: 3 ≤ 5 → within limits
Classification: "scale_within_limits" → Allowed
Action: Execute autonomously
```

```
Operation: Scale to 6 replicas
Current: 2 replicas, max_replicas: 5
Check: 6 > 5 → beyond limits
Classification: "scale_beyond_limits" → Restricted
Action: Request approval from devops-team
```

### 3.2 Approval Workflow

Defines how restricted operations are approved.

```yaml
governance:
  approval_workflow:
    approvers:
      - devops-team                 # Who can approve
    timeout: 1h                     # Approval timeout
    auto_reject_on_timeout: true    # Reject if no response
    notification_channels:
      - slack://devops-alerts       # Where to notify
```

**How Agents Use This**:
- When operation requires approval, agent generates approval request
- Agent sends notification to specified channels
- Agent waits for approval (up to timeout)
- If approved: agent executes operation
- If rejected or timeout: agent logs rejection and does not execute

**Approval Request Format**:
```json
{
  "service": "todo-frontend",
  "operation": "scale_beyond_limits",
  "current_state": {"replicas": 2, "max_replicas": 5},
  "proposed_state": {"replicas": 6},
  "rationale": "CPU utilization 95%, latency 300ms (exceeds target 200ms)",
  "blueprint_references": ["spec.scaling.max_replicas"],
  "risk_assessment": "Medium - requires increasing max_replicas",
  "rollback_plan": "Scale back to 2 replicas if performance degrades"
}
```

### 3.3 Audit

Defines how decisions and operations are logged.

```yaml
governance:
  audit:
    log_all_decisions: true         # Log every decision
    log_all_operations: true        # Log every operation
    retention_period: 90d           # Keep logs 90 days
    log_format: json                # JSON format
    log_destination: logs/agent-decisions/
```

**How Agents Use This**:
- Agents log every decision with blueprint version and rule references
- Agents log every operation with command, result, duration
- Logs are structured JSON for analysis

**Log Example**:
```json
{
  "timestamp": "2026-02-10T15:30:00Z",
  "agent_id": "decision-engine-001",
  "service": "todo-frontend",
  "blueprint_version": "1.0.0",
  "decision": {
    "type": "scale_up",
    "rationale": "CPU 85% > threshold 80%",
    "blueprint_references": ["spec.scaling.scale_up_threshold"]
  },
  "governance": {"classification": "allowed"},
  "outcome": "success"
}
```

## Section 4: Cost (Optional)

Simulated cost targets for demo purposes.

```yaml
cost:
  monthly_budget: 100 USD           # Monthly budget
  cost_per_replica: 20 USD          # Cost per replica
  optimization_priority: balanced   # balanced|cost|performance
```

**How Agents Use This**:
- Agents consider cost when making optimization recommendations
- If priority is "cost", agents favor cost reduction over performance
- If priority is "performance", agents favor performance over cost
- If priority is "balanced", agents balance both

## Blueprint Validation

Before agents use a blueprint, it must be validated against the JSON Schema.

**Validation Checks**:
1. **Schema compliance**: All required fields present, correct types
2. **Value constraints**: min_replicas ≤ max_replicas, percentages 0-100%, etc.
3. **Logical consistency**: scale_up_threshold > scale_down_threshold
4. **Governance completeness**: At least one allowed operation, at least one forbidden operation

**Validation Tools**:
```bash
# Validate blueprint against JSON Schema
jsonschema -i blueprints/frontend/blueprint.yaml blueprints/schema.json
```

**Common Validation Errors**:
- Missing required field: Add the field
- Invalid format: Check pattern (e.g., "50m" for CPU, "128Mi" for memory)
- Logical inconsistency: Fix values (e.g., ensure min < max)

## Blueprint Versioning

Blueprints should be version-controlled (Git) and follow semantic versioning.

**When to Increment Version**:
- **Patch (1.0.0 → 1.0.1)**: Adjust threshold values, change replica counts
- **Minor (1.0.0 → 1.1.0)**: Add new policies, add new metrics
- **Major (1.0.0 → 2.0.0)**: Change governance rules, remove policies

**Version History**:
```
blueprints/frontend/
├── blueprint.yaml          # Current version (1.0.0)
└── history/
    ├── v1.0.0.yaml        # Historical version
    └── v0.9.0.yaml        # Historical version
```

## Blueprint Change Detection

Agents watch the blueprints directory for changes and re-evaluate decisions when blueprints are updated.

**Change Detection Flow**:
1. Blueprint file modified (version 1.0.0 → 1.1.0)
2. Agent detects change (file watcher or polling)
3. Agent validates new blueprint
4. Agent re-evaluates current state against new blueprint
5. Agent makes decisions based on new policies

**Example**: If scale_up_threshold changes from 80% to 75%, and current CPU is 78%, the agent will now scale up (previously it wouldn't have).

## Best Practices

### 1. Start Conservative

Start with conservative values and adjust based on observed behavior:
- Higher thresholds (85% instead of 70%)
- Longer cooldown periods (90s instead of 60s)
- Fewer allowed operations initially

### 2. Document Rationale

Include comments explaining why each value was chosen:
```yaml
scale_up_threshold: 80%     # Scale up when utilization > 80%
                            # Rationale: Proactive scaling before performance degrades
```

### 3. Test with Dry-Run

Test blueprint changes in dry-run mode before applying:
```bash
# Dry-run mode simulates operations without executing
agent --dry-run --blueprint blueprints/frontend/blueprint.yaml
```

### 4. Monitor After Changes

After changing a blueprint, monitor agent decisions closely:
- Check audit logs for unexpected decisions
- Verify performance targets are still met
- Watch for increased approval requests

### 5. Keep Governance Strict

Start with strict governance (more forbidden operations) and relax over time:
- Begin with minimal allowed operations
- Add to allowed list as confidence grows
- Never remove from forbidden list without careful review

## Common Patterns

### Pattern 1: High-Traffic Service

For services with variable traffic:
```yaml
scaling:
  min_replicas: 2              # Always have redundancy
  max_replicas: 10             # Allow significant scaling
  scale_up_threshold: 70%      # Aggressive scaling
  scale_down_threshold: 40%    # Conservative scale-down
  cooldown_period: 30s         # Fast response to traffic
```

### Pattern 2: Critical Backend

For critical services that must stay available:
```yaml
scaling:
  min_replicas: 3              # High redundancy
  max_replicas: 5              # Limited scaling
  scale_up_threshold: 75%      # Proactive scaling
  scale_down_threshold: 50%    # Very conservative scale-down
  cooldown_period: 120s        # Slow, deliberate changes

reliability:
  max_restart_count: 2         # Strict failure handling
  rollback_threshold: 1        # Immediate rollback
```

### Pattern 3: Cost-Optimized Service

For non-critical services where cost matters:
```yaml
scaling:
  min_replicas: 1              # Minimal baseline
  max_replicas: 3              # Limited scaling
  scale_up_threshold: 85%      # Tolerate higher utilization
  scale_down_threshold: 20%    # Aggressive scale-down
  cooldown_period: 180s        # Slow scaling to avoid churn

cost:
  optimization_priority: cost  # Favor cost over performance
```

## Troubleshooting

### Problem: Agent not scaling

**Check**:
1. Current utilization vs thresholds
2. Cooldown period elapsed?
3. Within min/max replica limits?
4. Governance allows operation?

**Solution**: Review audit logs to see agent's decision rationale.

### Problem: Too many approval requests

**Check**:
1. Are thresholds too tight?
2. Are too many operations restricted?

**Solution**: Move some operations from restricted to allowed, or adjust thresholds.

### Problem: Agent making wrong decisions

**Check**:
1. Blueprint values correct?
2. Metrics accurate?
3. Governance rules appropriate?

**Solution**: Review blueprint, validate against schema, check metric collection.

## Examples

See complete examples:
- `blueprints/frontend/blueprint.yaml` - Frontend service blueprint
- `blueprints/backend/blueprint.yaml` - Backend service blueprint
- `blueprints/governance/policies.yaml` - Global governance policies

## Next Steps

1. **Create your first blueprint**: Copy an example and customize
2. **Validate the blueprint**: Use JSON Schema validation
3. **Test in dry-run mode**: Simulate agent decisions
4. **Deploy and monitor**: Watch agent decisions in audit logs
5. **Iterate**: Adjust based on observed behavior

## See Also

- [Agent Operations Guide](./AGENT_OPERATIONS.md) - How agents interpret blueprints
- [Governance Guide](./GOVERNANCE.md) - Governance framework details
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions
