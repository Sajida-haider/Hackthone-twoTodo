# Troubleshooting Guide

## Overview

This guide provides solutions to common issues encountered when using the Spec-Driven Infrastructure Automation system.

**Quick Links**:
- [Blueprint Issues](#blueprint-issues)
- [Agent Decision Issues](#agent-decision-issues)
- [Governance Issues](#governance-issues)
- [Execution Issues](#execution-issues)
- [Verification Issues](#verification-issues)
- [Rollback Issues](#rollback-issues)
- [Multi-Service Issues](#multi-service-issues)

---

## Blueprint Issues

### Issue: Blueprint validation fails

**Symptoms**:
```
Error: Blueprint validation failed
- spec.scaling.min_replicas: must be >= 1
- spec.scaling.max_replicas: must be > min_replicas
```

**Causes**:
- Invalid YAML syntax
- Missing required fields
- Values outside allowed ranges
- Type mismatches

**Solutions**:

1. **Validate YAML syntax**:
```bash
# Check YAML syntax
yamllint blueprints/frontend/blueprint.yaml

# Or use Python
python -c "import yaml; yaml.safe_load(open('blueprints/frontend/blueprint.yaml'))"
```

2. **Validate against schema**:
```bash
# Validate against JSON Schema
jsonschema -i blueprints/frontend/blueprint.yaml blueprints/schema.json
```

3. **Check required fields**:
```yaml
# Minimum required fields
metadata:
  name: service-name
  version: 1.0.0

spec:
  scaling:
    min_replicas: 1
    max_replicas: 5
    target_cpu_utilization: 70%

governance:
  agent_authority:
    allowed_operations: []
```

4. **Fix common validation errors**:
```yaml
# WRONG: min_replicas = 0
spec:
  scaling:
    min_replicas: 0  # ❌ Must be >= 1

# CORRECT:
spec:
  scaling:
    min_replicas: 1  # ✅

# WRONG: max_replicas < min_replicas
spec:
  scaling:
    min_replicas: 5
    max_replicas: 3  # ❌ Must be > min_replicas

# CORRECT:
spec:
  scaling:
    min_replicas: 3
    max_replicas: 5  # ✅
```

---

### Issue: Blueprint not loading

**Symptoms**:
```
Error: Blueprint file not found: blueprints/frontend/blueprint.yaml
```

**Causes**:
- File path incorrect
- File permissions
- File not committed to repository

**Solutions**:

1. **Check file exists**:
```bash
ls -la blueprints/frontend/blueprint.yaml
```

2. **Check file permissions**:
```bash
chmod 644 blueprints/frontend/blueprint.yaml
```

3. **Verify file path in configuration**:
```yaml
# config.yaml
blueprints:
  frontend: blueprints/frontend/blueprint.yaml  # Must match actual path
```

4. **Check if file is committed**:
```bash
git status blueprints/frontend/blueprint.yaml
```

---

### Issue: Blueprint changes not taking effect

**Symptoms**:
- Updated blueprint but agent still using old values
- Changes not reflected in decisions

**Causes**:
- Blueprint not reloaded
- Cached blueprint
- Wrong blueprint file being used

**Solutions**:

1. **Reload blueprint**:
```bash
# Trigger blueprint reload
curl -X POST http://agent-system/api/blueprints/reload

# Or restart agent
kubectl rollout restart deployment agent-system -n agent-system
```

2. **Clear blueprint cache**:
```bash
# Clear cache
curl -X DELETE http://agent-system/api/blueprints/cache

# Verify new blueprint loaded
curl http://agent-system/api/blueprints/frontend | jq '.version'
```

3. **Check which blueprint is loaded**:
```bash
# Get loaded blueprint
curl http://agent-system/api/blueprints/frontend | jq '.metadata'

# Compare with file
cat blueprints/frontend/blueprint.yaml | grep version
```

---

## Agent Decision Issues

### Issue: Agent not making decisions

**Symptoms**:
- No decisions in logs
- Service not scaling despite high load
- Agent appears idle

**Causes**:
- Metrics not being collected
- Blueprint not loaded
- Agent not running
- Circuit breaker open

**Solutions**:

1. **Check agent health**:
```bash
# Check agent status
kubectl get pods -n agent-system -l app=decision-engine

# Check agent logs
kubectl logs -n agent-system -l app=decision-engine --tail=100
```

2. **Verify metrics collection**:
```bash
# Check if metrics are being collected
curl http://agent-system/api/metrics/todo-frontend

# Should return:
{
  "cpu_utilization": 0.85,
  "memory_utilization": 0.70,
  "latency_p95": 180
}
```

3. **Check circuit breaker**:
```bash
# Get circuit breaker state
curl http://agent-system/api/safety/circuit-breaker

# If open, reset it
curl -X POST http://agent-system/api/safety/circuit-breaker/reset
```

4. **Check cooldown period**:
```bash
# Get cooldown status
curl http://agent-system/api/safety/cooldown

# If active, wait for it to elapse
# Or adjust cooldown period in blueprint
```

---

### Issue: Agent making wrong decisions

**Symptoms**:
- Scaling up when CPU is low
- Scaling down when CPU is high
- Unexpected operations

**Causes**:
- Incorrect blueprint thresholds
- Weighted utilization calculation error
- Metrics collection error

**Solutions**:

1. **Review decision logic**:
```bash
# Get last decision with rationale
cat logs/agent-decisions/$(date +%Y-%m-%d)/decisions.log | \
  jq 'select(.event_type == "decision_made") | {action, rationale, weighted_utilization}'
```

2. **Verify weighted utilization calculation**:
```python
# Manual calculation
cpu_util = 0.85
memory_util = 0.70
latency_util = 180 / 200  # actual / target = 0.90

weighted = (cpu_util * 0.5) + (memory_util * 0.3) + (latency_util * 0.2)
# = 0.425 + 0.210 + 0.180 = 0.815

# Should match agent's calculation
```

3. **Adjust blueprint thresholds**:
```yaml
# If scaling too aggressively
spec:
  scaling:
    scale_up_threshold: 85%  # Increase from 80%
    scale_down_threshold: 35%  # Decrease from 40%
```

4. **Check metrics accuracy**:
```bash
# Compare agent metrics with kubectl
kubectl top pods -n todo-app -l app=todo-frontend

# Compare with agent metrics
curl http://agent-system/api/metrics/todo-frontend
```

---

## Governance Issues

### Issue: Operations being blocked unexpectedly

**Symptoms**:
```
Error: Operation blocked by governance policy
Classification: forbidden
```

**Causes**:
- Operation in forbidden_operations list
- Circuit breaker open
- Cooldown period active
- Rate limit exceeded

**Solutions**:

1. **Check governance classification**:
```bash
# Get governance result
cat logs/agent-decisions/$(date +%Y-%m-%d)/governance.log | \
  jq 'select(.classification == "forbidden")'
```

2. **Review forbidden operations**:
```yaml
# Check blueprint
governance:
  agent_authority:
    forbidden_operations:
      - operation: delete_deployment  # Is your operation here?
```

3. **Check safety mechanisms**:
```bash
# Circuit breaker
curl http://agent-system/api/safety/circuit-breaker
# If open, reset or wait for timeout

# Cooldown
curl http://agent-system/api/safety/cooldown
# If active, wait for it to elapse

# Rate limit
curl http://agent-system/api/safety/rate-limit
# If exceeded, wait for window to reset
```

4. **Use suggested alternatives**:
```bash
# Governance provides alternatives
cat logs/agent-decisions/$(date +%Y-%m-%d)/governance.log | \
  jq '.alternatives_suggested'

# Example: Instead of delete_deployment, use scale_to_zero
kubectl scale deployment todo-frontend --replicas=0 -n todo-app
```

---

### Issue: Approval requests timing out

**Symptoms**:
```
Error: Approval request timed out
Status: auto_rejected
```

**Causes**:
- Approvers not notified
- Notification channels misconfigured
- Timeout too short
- Approvers unavailable

**Solutions**:

1. **Check notification delivery**:
```bash
# Verify notification sent
cat logs/agent-decisions/$(date +%Y-%m-%d)/approvals.log | \
  jq '.notification_sent_at'

# Check Slack/email logs
```

2. **Increase timeout**:
```yaml
# In blueprint
governance:
  approval_workflow:
    timeout: 2h  # Increase from 1h
```

3. **Add more approvers**:
```yaml
# In blueprint
governance:
  approval_workflow:
    approvers: ["devops-team", "platform-team"]  # Multiple teams
```

4. **Disable auto-reject**:
```yaml
# In blueprint (use with caution)
governance:
  approval_workflow:
    auto_reject_on_timeout: false  # Manual intervention required
```

---

## Execution Issues

### Issue: kubectl commands failing

**Symptoms**:
```
Error: kubectl scale failed
Exit code: 1
Stderr: Error from server (NotFound): deployments.apps "todo-frontend" not found
```

**Causes**:
- Deployment doesn't exist
- Wrong namespace
- Insufficient permissions
- Kubernetes API unreachable

**Solutions**:

1. **Verify deployment exists**:
```bash
kubectl get deployment todo-frontend -n todo-app
```

2. **Check namespace**:
```bash
# List all deployments
kubectl get deployments --all-namespaces | grep todo-frontend

# Update blueprint with correct namespace
```

3. **Check permissions**:
```bash
# Check service account permissions
kubectl auth can-i scale deployment --as=system:serviceaccount:agent-system:agent-sa -n todo-app

# If false, add RBAC permissions
kubectl create rolebinding agent-scale \
  --clusterrole=edit \
  --serviceaccount=agent-system:agent-sa \
  -n todo-app
```

4. **Check Kubernetes API**:
```bash
# Test API connectivity
kubectl cluster-info

# Check agent can reach API
kubectl logs -n agent-system -l app=execution-engine | grep "connection refused"
```

---

### Issue: Operations executing but not taking effect

**Symptoms**:
- kubectl command succeeds (exit code 0)
- But deployment not actually scaled
- Replica count unchanged

**Causes**:
- Deployment has HPA (Horizontal Pod Autoscaler)
- Resource quotas exceeded
- Node capacity insufficient

**Solutions**:

1. **Check for HPA**:
```bash
# List HPAs
kubectl get hpa -n todo-app

# If HPA exists, it will override manual scaling
# Either delete HPA or adjust HPA settings
kubectl delete hpa todo-frontend -n todo-app
```

2. **Check resource quotas**:
```bash
# Check quotas
kubectl get resourcequota -n todo-app

# Check if quota exceeded
kubectl describe resourcequota -n todo-app
```

3. **Check node capacity**:
```bash
# Check node resources
kubectl top nodes

# Check if nodes have capacity
kubectl describe nodes | grep -A 5 "Allocated resources"
```

---

## Verification Issues

### Issue: Verification always failing

**Symptoms**:
- Operations execute successfully
- But verification always fails
- Frequent rollbacks

**Causes**:
- Verification checks too strict
- Stabilization period too short
- Metrics not updating
- Unrealistic targets

**Solutions**:

1. **Review failed checks**:
```bash
# Get failed verifications
cat logs/agent-decisions/$(date +%Y-%m-%d)/verifications.log | \
  jq 'select(.outcome == "failure") | .checks[] | select(.status == "FAILED")'
```

2. **Increase stabilization period**:
```yaml
# In blueprint
verification:
  stabilization_period: 120s  # Increase from 60s
```

3. **Relax verification thresholds**:
```yaml
# In blueprint
spec:
  performance:
    latency_p95_target: 250ms  # Increase from 200ms
    error_rate_threshold: 1.5%  # Increase from 1%
```

4. **Make checks non-critical**:
```yaml
# In blueprint
verification:
  checks:
    - name: latency_p95
      critical: false  # Change from true
      rollback_trigger: false  # Don't trigger rollback
```

---

### Issue: Verification not running

**Symptoms**:
- Operations execute
- No verification logs
- No rollbacks even when service degraded

**Causes**:
- Verification Engine not running
- Verification disabled in blueprint
- Metrics collection failing

**Solutions**:

1. **Check Verification Engine**:
```bash
# Check agent status
kubectl get pods -n agent-system -l app=verification-engine

# Check logs
kubectl logs -n agent-system -l app=verification-engine --tail=100
```

2. **Enable verification in blueprint**:
```yaml
# In blueprint
verification:
  enabled: true  # Ensure this is true
  stabilization_period: 60s
```

3. **Check metrics collection**:
```bash
# Verify metrics available after operation
curl http://agent-system/api/metrics/todo-frontend

# Check timestamp is recent
```

---

## Rollback Issues

### Issue: Rollback not triggering

**Symptoms**:
- Verification fails
- But no rollback executed
- Service remains degraded

**Causes**:
- Rollback disabled in blueprint
- Rollback not configured for check
- Manual rollback required

**Solutions**:

1. **Enable automatic rollback**:
```yaml
# In blueprint
verification:
  rollback:
    enabled: true
    automatic: true
    trigger_on_critical_failure: true
```

2. **Configure rollback triggers**:
```yaml
# In blueprint
verification:
  checks:
    - name: latency_p95
      critical: true
      rollback_trigger: true  # Enable rollback for this check
```

3. **Check rollback logs**:
```bash
# Check if rollback was attempted
cat logs/agent-decisions/$(date +%Y-%m-%d)/rollbacks.log | \
  jq 'select(.event_type == "rollback_triggered")'
```

---

### Issue: Rollback failing

**Symptoms**:
```
Error: Rollback failed
Rollback verification: failure
```

**Causes**:
- Rollback command failed
- Rollback verification failed
- State cannot be restored

**Solutions**:

1. **Check rollback execution**:
```bash
# Get rollback details
cat logs/agent-decisions/$(date +%Y-%m-%d)/rollbacks.log | \
  jq 'select(.rollback_id == "rb-xxx") | .execution'
```

2. **Manual rollback**:
```bash
# If automatic rollback failed, rollback manually
kubectl scale deployment todo-frontend --replicas=3 -n todo-app

# Verify service restored
kubectl get pods -n todo-app -l app=todo-frontend
```

3. **Check rollback verification**:
```bash
# Get rollback verification result
cat logs/agent-decisions/$(date +%Y-%m-%d)/verifications.log | \
  jq 'select(.rollback_id == "rb-xxx")'
```

---

### Issue: Rollback loop

**Symptoms**:
- Operation executes
- Verification fails, rollback triggered
- Rollback executes
- Operation executes again
- Cycle repeats

**Causes**:
- Decision Engine still sees high load
- Cooldown period too short
- Circuit breaker not opening

**Solutions**:

1. **Increase cooldown period**:
```yaml
# In blueprint
governance:
  safety_mechanisms:
    cooldown_period: 300s  # Increase from 60s
```

2. **Configure circuit breaker**:
```yaml
# In blueprint
governance:
  safety_mechanisms:
    circuit_breaker:
      failure_threshold: 2  # Open after 2 failures
      timeout: 600s  # Stay open for 10 minutes
```

3. **Adjust decision thresholds**:
```yaml
# In blueprint
spec:
  scaling:
    scale_down_threshold: 30%  # Lower threshold to prevent immediate scale-down
```

---

## Multi-Service Issues

### Issue: Services interfering with each other

**Symptoms**:
- Frontend scales, backend also scales
- One service's decision affects another
- Unexpected cross-service behavior

**Causes**:
- Shared blueprint (wrong approach)
- Shared resources exhausted
- Configuration error

**Solutions**:

1. **Use separate blueprints**:
```bash
# Verify separate blueprints
ls blueprints/
# Should see:
# frontend/blueprint.yaml
# backend/blueprint.yaml
```

2. **Check service isolation**:
```bash
# Verify independent decisions
cat logs/agent-decisions/$(date +%Y-%m-%d)/multi-service.log | \
  jq '.independence_verification'
```

3. **Review resource conflicts**:
```bash
# Check for resource conflicts
cat logs/agent-decisions/$(date +%Y-%m-%d)/multi-service.log | \
  jq '.resource_conflict_check'
```

---

### Issue: Resource conflicts not resolving

**Symptoms**:
- Both services need scaling
- Cluster capacity insufficient
- Neither service scales

**Causes**:
- Conflict resolution not configured
- Priority not assigned
- Cluster capacity exhausted

**Solutions**:

1. **Assign service priorities**:
```yaml
# In backend blueprint
metadata:
  priority: high
  criticality: critical

# In frontend blueprint
metadata:
  priority: medium
  criticality: standard
```

2. **Increase cluster capacity**:
```bash
# Add nodes to cluster
# (Cloud-specific command)

# Or scale down non-critical services
kubectl scale deployment non-critical-service --replicas=0
```

3. **Configure conflict resolution**:
```yaml
# In global governance
governance:
  conflict_resolution:
    strategy: prioritize_by_criticality
    defer_duration: 5m
```

---

## Common Error Messages

### "Blueprint validation failed"

**Meaning**: Blueprint YAML doesn't match schema

**Fix**: Validate YAML syntax and required fields

---

### "Operation blocked by governance policy"

**Meaning**: Operation classified as forbidden or restricted without approval

**Fix**: Check governance rules, use alternatives, or request approval

---

### "Circuit breaker open"

**Meaning**: Too many failures, operations temporarily blocked

**Fix**: Wait for timeout or manually reset circuit breaker

---

### "Cooldown period active"

**Meaning**: Recent operation executed, waiting before next operation

**Fix**: Wait for cooldown to elapse or adjust cooldown period

---

### "Verification failed: latency_p95"

**Meaning**: Latency exceeded target after operation

**Fix**: Rollback triggered automatically, review capacity planning

---

### "Approval request timeout"

**Meaning**: No approval received within timeout period

**Fix**: Check notifications, increase timeout, or add more approvers

---

## Debugging Tools

### 1. Check Agent Health

```bash
# All agents
curl http://agent-system/api/health

# Specific agent
curl http://agent-system/api/agents/decision-engine/health
```

### 2. View Recent Decisions

```bash
# Last 10 decisions
cat logs/agent-decisions/$(date +%Y-%m-%d)/decisions.log | \
  jq 'select(.event_type == "decision_made")' | \
  tail -10
```

### 3. Check Governance Results

```bash
# Recent governance checks
cat logs/agent-decisions/$(date +%Y-%m-%d)/governance.log | \
  jq '{classification, rationale}' | \
  tail -10
```

### 4. View Verification Results

```bash
# Recent verifications
cat logs/agent-decisions/$(date +%Y-%m-%d)/verifications.log | \
  jq '{outcome, checks}' | \
  tail -10
```

### 5. Monitor Safety Mechanisms

```bash
# Circuit breaker state
curl http://agent-system/api/safety/circuit-breaker

# Cooldown status
curl http://agent-system/api/safety/cooldown

# Rate limit status
curl http://agent-system/api/safety/rate-limit
```

---

## Getting Help

### 1. Check Documentation

- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`
- **Agent Operations**: `docs/AGENT_OPERATIONS.md`
- **Governance**: `docs/GOVERNANCE.md`
- **FAQ**: `docs/FAQ.md`

### 2. Review Examples

- **Examples Directory**: `examples/`
- **Demo Walkthroughs**: `demos/`

### 3. Check Logs

```bash
# Agent logs
kubectl logs -n agent-system -l app=agent-system --tail=100

# Audit logs
cat logs/agent-decisions/$(date +%Y-%m-%d)/*.log
```

### 4. Contact Support

- **GitHub Issues**: Report bugs and feature requests
- **Slack Channel**: #spec-driven-automation
- **Email**: support@example.com

---

## Prevention Tips

### 1. Test in Staging First

✅ Always test blueprint changes in staging before production

### 2. Start Conservative

✅ Start with conservative thresholds, adjust based on observation

### 3. Monitor Closely

✅ Monitor agent decisions and outcomes for first 24 hours

### 4. Use Dry-Run Mode

✅ Test decisions without execution using dry-run mode

### 5. Review Audit Logs

✅ Regularly review audit logs for unexpected behavior

---

## See Also

- **Agent Operations Guide**: `docs/AGENT_OPERATIONS.md`
- **FAQ**: `docs/FAQ.md`
- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`
- **Governance Documentation**: `docs/GOVERNANCE.md`
