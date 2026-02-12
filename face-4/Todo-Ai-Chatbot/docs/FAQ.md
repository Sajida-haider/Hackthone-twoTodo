# Frequently Asked Questions (FAQ)

## Overview

This FAQ answers common questions about the Spec-Driven Infrastructure Automation system.

**Topics**:
- [General Concepts](#general-concepts)
- [Blueprints](#blueprints)
- [Agents](#agents)
- [Governance](#governance)
- [Safety Mechanisms](#safety-mechanisms)
- [Operations](#operations)
- [Verification and Rollback](#verification-and-rollback)
- [Multi-Service Management](#multi-service-management)

---

## General Concepts

### What is Spec-Driven Infrastructure Automation?

Spec-Driven Infrastructure Automation is an approach where infrastructure operations are governed by declarative specifications (blueprints) and executed autonomously by AI agents.

**Key Principles**:
- **Blueprint as Source of Truth**: All policies defined in YAML blueprints
- **Agent Autonomy**: Agents make decisions within blueprint boundaries
- **Governance First**: All operations validated against governance policies
- **Safety by Default**: Circuit breakers, cooldowns, and verification built-in

### How is this different from traditional automation?

**Traditional Automation**:
- Scripts execute predefined actions
- No decision-making capability
- Manual intervention for edge cases
- Limited safety mechanisms

**Spec-Driven Automation**:
- Agents analyze metrics and make decisions
- Autonomous within governance boundaries
- Automatic handling of edge cases
- Built-in safety mechanisms (circuit breakers, rollbacks)

### What problems does this solve?

1. **Manual Operations**: Eliminates manual scaling and resource adjustments
2. **Slow Response**: Responds to issues in seconds, not minutes/hours
3. **Human Error**: Consistent, policy-driven decisions
4. **Lack of Governance**: All operations validated against policies
5. **No Audit Trail**: Complete audit log of all decisions and operations

---

## Blueprints

### What is a blueprint?

A blueprint is a YAML file that defines:
- **Scaling policies**: When and how to scale
- **Resource limits**: CPU, memory boundaries
- **Performance targets**: Latency, error rate thresholds
- **Governance rules**: What agents can/cannot do
- **Verification checks**: How to verify operations succeeded

### Do I need a separate blueprint for each service?

**Yes**, each service should have its own blueprint. This enables:
- Service-specific policies
- Independent scaling decisions
- Different governance rules
- Optimized resource allocation

### Can I use the same blueprint for multiple services?

**Not recommended**. While technically possible, each service has unique characteristics:
- Different traffic patterns
- Different resource requirements
- Different criticality levels
- Different performance targets

### How do I create a blueprint?

1. **Start with template**:
```bash
cp blueprints/schema.yaml blueprints/my-service/blueprint.yaml
```

2. **Customize for your service**:
```yaml
metadata:
  name: my-service
  version: 1.0.0

spec:
  scaling:
    min_replicas: 2
    max_replicas: 10
    target_cpu_utilization: 70%
```

3. **Validate**:
```bash
jsonschema -i blueprints/my-service/blueprint.yaml blueprints/schema.json
```

4. **Test in staging first**

### How often should I update blueprints?

**Update when**:
- Service requirements change
- Performance targets change
- Governance policies change
- After capacity planning reviews

**Best Practice**: Review blueprints quarterly, update as needed.

### Can blueprints be version controlled?

**Yes, absolutely**. Blueprints should be:
- Stored in Git
- Reviewed via pull requests
- Tested in staging before production
- Deployed with CI/CD pipelines

---

## Agents

### What are the five agents?

1. **Blueprint Parser**: Loads and validates blueprints
2. **Decision Engine**: Analyzes metrics, makes decisions
3. **Governance Enforcer**: Validates operations against policies
4. **Execution Engine**: Executes approved operations
5. **Verification Engine**: Verifies outcomes, triggers rollbacks

### How do agents communicate?

Agents communicate through **structured JSON messages**:
```json
{
  "message_id": "msg-xxx",
  "source_agent": "decision-engine",
  "target_agent": "governance-enforcer",
  "payload": { "decision": {...} }
}
```

### Can I disable specific agents?

**Not recommended**. All five agents are required for safe operation:
- Without Decision Engine: No decisions made
- Without Governance Enforcer: No safety checks
- Without Execution Engine: No operations executed
- Without Verification Engine: No rollback capability

### How do I monitor agent health?

```bash
# Check all agents
curl http://agent-system/api/health

# Check specific agent
curl http://agent-system/api/agents/decision-engine/health

# View agent logs
kubectl logs -n agent-system -l app=decision-engine
```

### What happens if an agent fails?

**Agent Failure Handling**:
- Agent restarts automatically (Kubernetes)
- Operations pause until agent recovers
- No partial operations executed
- Audit log records failure

**Recovery**:
- Agent resumes from last known state
- No data loss (all state persisted)
- Operations resume after recovery

---

## Governance

### What are the three operation classifications?

1. **Allowed**: Execute autonomously, no approval needed
   - Example: Scale within min/max limits

2. **Restricted**: Requires human approval before execution
   - Example: Scale beyond max_replicas

3. **Forbidden**: Blocked immediately, cannot be approved
   - Example: Delete deployment

### How do I make an operation allowed?

Add to `allowed_operations` in blueprint:
```yaml
governance:
  agent_authority:
    allowed_operations:
      - operation: scale_within_limits
        condition: target_replicas >= min_replicas AND target_replicas <= max_replicas
        autonomous: true
```

### How do I require approval for an operation?

Add to `requires_approval` in blueprint:
```yaml
governance:
  agent_authority:
    requires_approval:
      - operation: scale_beyond_limits
        condition: target_replicas > max_replicas
        risk_level: medium
        approvers: ["devops-team"]
```

### How do I forbid an operation?

Add to `forbidden_operations` in blueprint:
```yaml
governance:
  agent_authority:
    forbidden_operations:
      - operation: delete_deployment
        rationale: "Causes complete service outage"
        alternatives: ["scale_to_zero", "disable_ingress"]
```

### Can I override a forbidden operation?

**No**. Forbidden operations cannot be overridden, even with approval.

**Workarounds**:
1. Use suggested alternatives
2. Execute manually (outside agent system)
3. Update blueprint to move operation to `requires_approval`

### How long do approval requests wait?

**Default**: 1 hour (configurable in blueprint)

```yaml
governance:
  approval_workflow:
    timeout: 2h  # Adjust as needed
    auto_reject_on_timeout: true
```

### Who can approve operations?

**Approvers** are defined in blueprint:
```yaml
governance:
  approval_workflow:
    approvers: ["devops-team", "platform-team"]
```

Approvers receive notifications via:
- Slack
- Email
- PagerDuty
- Custom webhooks

---

## Safety Mechanisms

### What is a circuit breaker?

A circuit breaker prevents repeated failures by temporarily blocking operations after consecutive failures.

**States**:
- **Closed**: Normal operation
- **Open**: Operations blocked (after failures)
- **Half-Open**: Testing if issue resolved

**Configuration**:
```yaml
governance:
  safety_mechanisms:
    circuit_breaker:
      failure_threshold: 3  # Open after 3 failures
      timeout: 3600s  # Stay open for 1 hour
```

### What is a cooldown period?

A cooldown period is a mandatory wait time between operations to prevent oscillation.

**Purpose**: Allow system to stabilize before next operation

**Configuration**:
```yaml
governance:
  safety_mechanisms:
    cooldown_period: 60s  # Wait 60s between operations
```

### What is rate limiting?

Rate limiting restricts the number of operations within a time window.

**Purpose**: Prevent too many operations in short time

**Configuration**:
```yaml
governance:
  safety_mechanisms:
    rate_limiting:
      max_operations_per_hour: 10
```

### How do I reset a circuit breaker?

**Automatic**: Circuit breaker resets after timeout

**Manual**:
```bash
curl -X POST http://agent-system/api/safety/circuit-breaker/reset
```

### Can I disable safety mechanisms?

**Not recommended**. Safety mechanisms prevent:
- Repeated failures
- Oscillation (scale up/down loops)
- Too many operations
- System instability

**If you must**:
```yaml
governance:
  safety_mechanisms:
    circuit_breaker:
      enabled: false  # Use with extreme caution
```

---

## Operations

### What operations can agents perform?

**Scaling**:
- Scale up (increase replicas)
- Scale down (decrease replicas)

**Resource Optimization**:
- Adjust CPU requests/limits
- Adjust memory requests/limits

**Failure Recovery**:
- Restart pods
- Rollback deployments

**Configuration**:
- Update environment variables
- Update config maps

### How long does an operation take?

**Typical Durations**:
- Decision: < 1 second
- Governance check: < 1 second
- Execution: 2-5 seconds
- Stabilization: 60 seconds
- Verification: 5-10 seconds

**Total**: ~2 minutes for autonomous operation

### Can I see what operations were executed?

**Yes**, check audit logs:
```bash
# All operations today
cat logs/agent-decisions/$(date +%Y-%m-%d)/operations.log

# Specific operation
cat logs/agent-decisions/$(date +%Y-%m-%d)/operations.log | \
  jq 'select(.operation_id == "dec-xxx")'
```

### Can I execute operations manually?

**Yes**, but operations outside the agent system:
- Won't be logged in agent audit trail
- Won't be verified by Verification Engine
- Won't trigger rollback if they fail
- May conflict with agent decisions

**Recommendation**: Use agent system for all operations

### What if I need to perform an emergency operation?

**Option 1**: Request approval (if operation is restricted)

**Option 2**: Execute manually with kubectl
```bash
kubectl scale deployment my-service --replicas=10 -n my-namespace
```

**Option 3**: Temporarily update blueprint to allow operation

---

## Verification and Rollback

### What is verification?

Verification is the process of checking that an operation achieved its intended outcome.

**Checks**:
- Replica count matches target
- All pods are ready
- CPU utilization within target
- Latency within target
- Error rate within threshold

### When does verification run?

**After stabilization period** (default: 60 seconds)

This allows:
- New pods to start
- Load to redistribute
- Metrics to stabilize

### What happens if verification fails?

**Automatic Rollback**:
1. Verification Engine detects failure
2. Rollback decision generated
3. Execution Engine executes rollback
4. Verification Engine verifies rollback
5. Service restored to pre-operation state

### How long does rollback take?

**Typical Rollback Duration**:
- Rollback decision: < 1 second
- Rollback execution: 2-5 seconds
- Pod startup: 30-60 seconds
- Verification: 60 seconds

**Total**: ~2-3 minutes

### Can I disable automatic rollback?

**Not recommended**, but possible:
```yaml
verification:
  rollback:
    enabled: false  # Disables automatic rollback
```

**Risk**: Service remains degraded if operation fails

### Can I manually trigger a rollback?

**Yes**:
```bash
# Trigger rollback for specific operation
curl -X POST http://agent-system/api/rollback \
  -d '{"operation_id": "dec-xxx"}'
```

### What if rollback fails?

**Escalation**:
1. Rollback failure logged
2. DevOps team notified
3. Manual intervention required

**Manual Rollback**:
```bash
# Restore to previous state manually
kubectl scale deployment my-service --replicas=3 -n my-namespace
```

---

## Multi-Service Management

### Can agents manage multiple services?

**Yes**. The Multi-Service Coordinator manages multiple services independently.

**Each service**:
- Has its own blueprint
- Makes independent decisions
- Has separate governance
- Scales independently

### Do services interfere with each other?

**No**. Services are completely isolated:
- Separate metrics
- Separate decisions
- Separate governance
- Separate execution

### What if both services need scaling but cluster capacity is limited?

**Conflict Resolution**:
1. Detect resource conflict
2. Prioritize by service criticality
3. Execute high-priority service first
4. Defer low-priority service
5. Retry deferred service when capacity available

### How do I set service priority?

In blueprint metadata:
```yaml
metadata:
  name: my-service
  priority: high  # high, medium, low
  criticality: critical  # critical, standard
```

### Can I manage services in different namespaces?

**Yes**. Each blueprint specifies its namespace:
```yaml
metadata:
  name: my-service
  namespace: my-namespace
```

---

## Best Practices

### Should I start with conservative or aggressive thresholds?

**Start conservative**:
```yaml
spec:
  scaling:
    scale_up_threshold: 85%  # Conservative (higher)
    scale_down_threshold: 35%  # Conservative (lower)
```

**Adjust based on observation**:
- Monitor for 1-2 weeks
- Adjust thresholds gradually
- Test in staging first

### How often should agents make decisions?

**Recommendation**: Every 1-5 minutes

**Configuration**:
```yaml
decision_engine:
  evaluation_interval: 300s  # 5 minutes
```

**Trade-offs**:
- More frequent: Faster response, more operations
- Less frequent: Slower response, fewer operations

### Should I use dry-run mode?

**Yes, for**:
- Testing new blueprints
- Validating decision logic
- Training new team members
- Debugging issues

**Enable dry-run**:
```yaml
execution:
  dry_run: true  # Simulate operations without executing
```

### How do I test blueprint changes?

1. **Update blueprint in staging**
2. **Monitor for 24 hours**
3. **Review audit logs**
4. **Verify expected behavior**
5. **Deploy to production**

### What metrics should I monitor?

**Agent Metrics**:
- Decisions per minute
- Operations per minute
- Verification success rate
- Rollback rate

**Service Metrics**:
- CPU utilization
- Memory utilization
- Latency (p50, p95, p99)
- Error rate
- Throughput

---

## Troubleshooting

### Where do I start when something goes wrong?

1. **Check agent health**:
```bash
curl http://agent-system/api/health
```

2. **Review recent decisions**:
```bash
cat logs/agent-decisions/$(date +%Y-%m-%d)/decisions.log | tail -10
```

3. **Check governance results**:
```bash
cat logs/agent-decisions/$(date +%Y-%m-%d)/governance.log | tail -10
```

4. **Review verification results**:
```bash
cat logs/agent-decisions/$(date +%Y-%m-%d)/verifications.log | tail -10
```

### Where can I find more help?

- **Troubleshooting Guide**: `docs/TROUBLESHOOTING.md`
- **Agent Operations Guide**: `docs/AGENT_OPERATIONS.md`
- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`
- **Examples**: `examples/` directory
- **Demos**: `demos/` directory

---

## Advanced Topics

### Can I customize the weighted utilization formula?

**Yes**, in blueprint:
```yaml
decision_engine:
  weighted_utilization:
    cpu_weight: 0.5
    memory_weight: 0.3
    latency_weight: 0.2
```

### Can I add custom verification checks?

**Yes**, in blueprint:
```yaml
verification:
  checks:
    - name: custom_metric
      type: threshold
      target: "< 100"
      critical: true
      rollback_trigger: true
```

### Can I integrate with external systems?

**Yes**, via webhooks:
```yaml
governance:
  approval_workflow:
    notification_channels:
      - slack://devops-alerts
      - webhook://https://my-system.com/notify
```

### Can I use custom decision logic?

**Not directly**. Decision logic is built into Decision Engine.

**Workarounds**:
- Adjust blueprint thresholds
- Use custom metrics in weighted utilization
- Extend Decision Engine (requires code changes)

---

## Getting Started

### What's the quickest way to get started?

1. **Deploy agent system**:
```bash
kubectl apply -f deployments/agent-system.yaml
```

2. **Create blueprint from template**:
```bash
cp blueprints/schema.yaml blueprints/my-service/blueprint.yaml
```

3. **Customize blueprint** for your service

4. **Enable dry-run mode** for testing

5. **Monitor for 24 hours**

6. **Disable dry-run** when confident

### What's the minimum viable blueprint?

```yaml
metadata:
  name: my-service
  version: 1.0.0

spec:
  scaling:
    min_replicas: 1
    max_replicas: 5
    target_cpu_utilization: 70%
    scale_up_threshold: 80%
    scale_down_threshold: 40%

governance:
  agent_authority:
    allowed_operations:
      - operation: scale_within_limits
        condition: target_replicas >= min_replicas AND target_replicas <= max_replicas
        autonomous: true
```

### Do I need to modify my application?

**No**. Spec-Driven Infrastructure Automation works with any Kubernetes application. No code changes required.

---

## See Also

- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`
- **Agent Operations**: `docs/AGENT_OPERATIONS.md`
- **Governance**: `docs/GOVERNANCE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Examples**: `examples/` directory
- **Demos**: `demos/` directory
