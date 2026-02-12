# Quick Start Guide

## Overview

This guide will help you get started with Spec-Driven Infrastructure Automation in 30 minutes.

**What You'll Learn**:
1. Core concepts (blueprints, agents, governance)
2. Create your first blueprint
3. Deploy the agent system
4. See autonomous scaling in action
5. Understand governance and safety

**Prerequisites**:
- Kubernetes cluster (Minikube, kind, or cloud)
- kubectl configured
- Basic Kubernetes knowledge
- 30 minutes

---

## Step 1: Understand Core Concepts (5 minutes)

### What is Spec-Driven Infrastructure Automation?

Infrastructure operations governed by **blueprints** (YAML specs) and executed autonomously by **AI agents**.

### The Three Key Components

#### 1. Blueprints (The "What")

YAML files defining policies:
```yaml
spec:
  scaling:
    min_replicas: 1
    max_replicas: 5
    target_cpu_utilization: 70%
    scale_up_threshold: 80%
```

#### 2. Agents (The "How")

Five agents that work together:
- **Blueprint Parser**: Loads blueprints
- **Decision Engine**: Analyzes metrics, makes decisions
- **Governance Enforcer**: Validates operations
- **Execution Engine**: Executes operations
- **Verification Engine**: Verifies outcomes, triggers rollbacks

#### 3. Governance (The "Rules")

Three operation classifications:
- **Allowed**: Execute autonomously
- **Restricted**: Require approval
- **Forbidden**: Blocked immediately

### How It Works

```
Metrics → Decision → Governance → Execution → Verification
```

**Example**: High CPU detected → Scale up decision → Governance allows → Execute scale → Verify success

---

## Step 2: Deploy Agent System (5 minutes)

### Option A: Quick Deploy (Recommended for Testing)

```bash
# Clone repository
git clone https://github.com/example/spec-driven-automation
cd spec-driven-automation

# Deploy agent system
kubectl apply -f deployments/agent-system.yaml

# Verify agents running
kubectl get pods -n agent-system

# Expected output:
# NAME                                READY   STATUS    RESTARTS   AGE
# blueprint-parser-xxx                1/1     Running   0          30s
# decision-engine-xxx                 1/1     Running   0          30s
# governance-enforcer-xxx             1/1     Running   0          30s
# execution-engine-xxx                1/1     Running   0          30s
# verification-engine-xxx             1/1     Running   0          30s
```

### Option B: Helm Install (Recommended for Production)

```bash
# Add Helm repository
helm repo add spec-driven https://charts.example.com/spec-driven
helm repo update

# Install
helm install agent-system spec-driven/agent-system \
  --namespace agent-system \
  --create-namespace

# Verify
helm status agent-system -n agent-system
```

### Verify Installation

```bash
# Check agent health
curl http://localhost:8080/api/health

# Expected output:
{
  "status": "healthy",
  "agents": {
    "blueprint-parser": "healthy",
    "decision-engine": "healthy",
    "governance-enforcer": "healthy",
    "execution-engine": "healthy",
    "verification-engine": "healthy"
  }
}
```

---

## Step 3: Create Your First Blueprint (10 minutes)

### Deploy Sample Application

First, deploy a sample application to manage:

```bash
# Deploy todo-frontend
kubectl create namespace todo-app

kubectl create deployment todo-frontend \
  --image=nginx:alpine \
  --replicas=2 \
  -n todo-app

kubectl set resources deployment todo-frontend \
  --requests=cpu=50m,memory=128Mi \
  --limits=cpu=200m,memory=512Mi \
  -n todo-app

# Verify deployment
kubectl get deployment todo-frontend -n todo-app
```

### Create Blueprint Directory

```bash
mkdir -p blueprints/todo-frontend
```

### Create Your First Blueprint

Create `blueprints/todo-frontend/blueprint.yaml`:

```yaml
# blueprints/todo-frontend/blueprint.yaml
metadata:
  name: todo-frontend
  version: 1.0.0
  description: "Frontend service for Todo application"

spec:
  # Scaling Configuration
  scaling:
    min_replicas: 1          # Minimum replicas (never scale below)
    max_replicas: 5          # Maximum replicas (never scale above)
    target_cpu_utilization: 70%     # Target CPU utilization
    target_memory_utilization: 80%  # Target memory utilization
    scale_up_threshold: 80%         # Scale up when utilization exceeds this
    scale_down_threshold: 40%       # Scale down when utilization below this

  # Resource Configuration
  resources:
    cpu_request: 50m         # CPU request per pod
    cpu_limit: 200m          # CPU limit per pod
    memory_request: 128Mi    # Memory request per pod
    memory_limit: 512Mi      # Memory limit per pod

  # Performance Targets
  performance:
    latency_p95_target: 200ms        # Target P95 latency
    error_rate_threshold: 1%         # Maximum acceptable error rate

# Governance Configuration
governance:
  agent_authority:
    # Operations agents can execute autonomously
    allowed_operations:
      - operation: scale_within_limits
        condition: target_replicas >= min_replicas AND target_replicas <= max_replicas
        autonomous: true
        rationale: "Scaling within configured limits is safe"

    # Operations requiring human approval
    requires_approval:
      - operation: scale_beyond_limits
        condition: target_replicas > max_replicas
        risk_level: medium
        approvers: ["devops-team"]
        rationale: "Scaling beyond max_replicas requires approval"

    # Operations that are forbidden
    forbidden_operations:
      - operation: delete_deployment
        rationale: "Deleting deployment causes complete service outage"
        alternatives: ["scale_to_zero", "disable_ingress"]

  # Approval Workflow
  approval_workflow:
    approvers: ["devops-team"]
    notification_channels: ["slack://devops-alerts"]
    timeout: 1h
    auto_reject_on_timeout: true

  # Safety Mechanisms
  safety_mechanisms:
    circuit_breaker:
      enabled: true
      failure_threshold: 3
      timeout: 3600s

    cooldown_period: 60s

    rate_limiting:
      max_operations_per_hour: 10

# Verification Configuration
verification:
  enabled: true
  stabilization_period: 60s

  checks:
    - name: replica_count
      type: exact_match
      critical: true

    - name: pods_ready
      type: exact_match
      critical: true

    - name: cpu_utilization
      type: threshold
      target: "< 80%"
      critical: false

    - name: latency_p95
      type: threshold
      target: "< 200ms"
      critical: true
      rollback_trigger: true

    - name: error_rate
      type: threshold
      target: "< 1%"
      critical: true
      rollback_trigger: true

  rollback:
    enabled: true
    automatic: true
    trigger_on_critical_failure: true
```

### Validate Blueprint

```bash
# Validate YAML syntax
yamllint blueprints/todo-frontend/blueprint.yaml

# Validate against schema
jsonschema -i blueprints/todo-frontend/blueprint.yaml blueprints/schema.json

# Load blueprint into agent system
curl -X POST http://localhost:8080/api/blueprints/load \
  -H "Content-Type: application/json" \
  -d '{"path": "blueprints/todo-frontend/blueprint.yaml"}'

# Verify blueprint loaded
curl http://localhost:8080/api/blueprints/todo-frontend | jq '.metadata'
```

---

## Step 4: See Autonomous Scaling in Action (5 minutes)

### Enable Dry-Run Mode (Optional)

For testing, enable dry-run mode to simulate operations without executing:

```bash
curl -X POST http://localhost:8080/api/config/dry-run \
  -d '{"enabled": true}'
```

### Simulate High Load

Generate load to trigger scaling:

```bash
# Create load generator
kubectl run load-generator \
  --image=busybox \
  --restart=Never \
  -n todo-app \
  -- /bin/sh -c "while true; do wget -q -O- http://todo-frontend:80; done"

# Watch CPU increase
watch kubectl top pods -n todo-app -l app=todo-frontend
```

### Watch Agent Decisions

```bash
# Watch agent logs
kubectl logs -f -n agent-system -l app=decision-engine

# Expected output:
# [2026-02-10 15:30:00] Metrics collected: CPU 85%, Memory 70%
# [2026-02-10 15:30:00] Weighted utilization: 81.5%
# [2026-02-10 15:30:00] Decision: scale_up from 2 to 3 replicas
# [2026-02-10 15:30:00] Governance: allowed (within limits)
# [2026-02-10 15:30:05] Execution: kubectl scale deployment todo-frontend --replicas=3
# [2026-02-10 15:30:07] Execution: success (exit code 0)
# [2026-02-10 15:31:30] Verification: success (all checks passed)
```

### Watch Scaling Happen

```bash
# Watch pods scale up
watch kubectl get pods -n todo-app -l app=todo-frontend

# Expected:
# NAME                             READY   STATUS    RESTARTS   AGE
# todo-frontend-7d8f9c5b6d-abc12   1/1     Running   0          10m
# todo-frontend-7d8f9c5b6d-def34   1/1     Running   0          10m
# todo-frontend-7d8f9c5b6d-ghi56   1/1     Running   0          30s  ← New pod
```

### Check Audit Logs

```bash
# View decision log
cat logs/agent-decisions/$(date +%Y-%m-%d)/decisions.log | \
  jq 'select(.event_type == "decision_made")'

# View operation log
cat logs/agent-decisions/$(date +%Y-%m-%d)/operations.log | \
  jq 'select(.event_type == "operation_executed")'

# View verification log
cat logs/agent-decisions/$(date +%Y-%m-%d)/verifications.log | \
  jq 'select(.event_type == "verification_completed")'
```

### Stop Load Generator

```bash
# Stop load
kubectl delete pod load-generator -n todo-app

# Watch CPU decrease
watch kubectl top pods -n todo-app -l app=todo-frontend

# Agent will eventually scale down (when CPU < 40%)
```

---

## Step 5: Understand Governance (5 minutes)

### Test Allowed Operation

Allowed operations execute autonomously:

```bash
# Trigger scale within limits (2 → 3 replicas)
# This is ALLOWED because 3 is within min_replicas (1) and max_replicas (5)

# Check governance result
cat logs/agent-decisions/$(date +%Y-%m-%d)/governance.log | \
  jq 'select(.classification == "allowed")'

# Output:
{
  "classification": "allowed",
  "requires_approval": false,
  "rationale": "Target replicas (3) within blueprint limits (1-5)"
}
```

### Test Restricted Operation

Restricted operations require approval:

```bash
# Attempt to scale beyond max_replicas (5 → 6 replicas)
# This is RESTRICTED and requires approval

# Manually trigger (for demo)
curl -X POST http://localhost:8080/api/operations \
  -d '{"service": "todo-frontend", "operation": "scale_up", "target_replicas": 6}'

# Check governance result
cat logs/agent-decisions/$(date +%Y-%m-%d)/governance.log | \
  jq 'select(.classification == "restricted")'

# Output:
{
  "classification": "restricted",
  "requires_approval": true,
  "approvers": ["devops-team"],
  "rationale": "Target replicas (6) exceeds max_replicas (5)"
}

# Approval request sent to Slack/email
# Operation waits for approval (timeout: 1 hour)
```

### Test Forbidden Operation

Forbidden operations are blocked immediately:

```bash
# Attempt to delete deployment
curl -X POST http://localhost:8080/api/operations \
  -d '{"service": "todo-frontend", "operation": "delete_deployment"}'

# Response:
{
  "status": "blocked",
  "code": 403,
  "classification": "forbidden",
  "rationale": "Deleting deployment causes complete service outage",
  "alternatives": [
    "scale_to_zero",
    "disable_ingress"
  ]
}

# Operation blocked, not executed
```

---

## Step 6: Explore Demonstrations (Optional)

### Demo 1: Autonomous Scaling

See complete walkthrough of autonomous scaling:

```bash
cat demos/01-autonomous-scaling.md
```

**What you'll learn**:
- How metrics trigger decisions
- How governance validates operations
- How verification confirms success

### Demo 2: Approval Workflow

See how approval workflow handles operations beyond limits:

```bash
cat demos/02-approval-workflow.md
```

**What you'll learn**:
- When approval is required
- How approval requests are generated
- How to approve/reject operations

### Demo 3: Governance Blocking

See how forbidden operations are blocked:

```bash
cat demos/03-governance-blocking.md
```

**What you'll learn**:
- What operations are forbidden
- Why they're blocked
- What alternatives are suggested

### Demo 4: Rollback on Failure

See automatic rollback when verification fails:

```bash
cat demos/04-rollback-verification.md
```

**What you'll learn**:
- When rollback is triggered
- How rollback is executed
- How service is restored

### Demo 5: Multi-Service Management

See independent management of multiple services:

```bash
cat demos/05-multi-service.md
```

**What you'll learn**:
- How services are managed independently
- How conflicts are detected and resolved
- How priorities are used

---

## Next Steps

### Learn More

**Core Documentation**:
- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md` - Complete blueprint reference
- **Agent Operations**: `docs/AGENT_OPERATIONS.md` - How agents work together
- **Governance**: `docs/GOVERNANCE.md` - Governance rules and policies
- **FAQ**: `docs/FAQ.md` - Frequently asked questions

**Troubleshooting**:
- **Troubleshooting Guide**: `docs/TROUBLESHOOTING.md` - Common issues and solutions

**Examples**:
- **Examples Directory**: `examples/` - Complete examples of decisions, operations, governance

### Customize Your Blueprint

1. **Adjust thresholds** based on your service:
```yaml
spec:
  scaling:
    scale_up_threshold: 85%  # Adjust based on observation
    scale_down_threshold: 35%
```

2. **Set performance targets**:
```yaml
spec:
  performance:
    latency_p95_target: 150ms  # Your service's target
    error_rate_threshold: 0.5%
```

3. **Configure governance**:
```yaml
governance:
  agent_authority:
    allowed_operations:
      - operation: your_operation
        condition: your_condition
```

### Deploy to Production

1. **Test in staging first**
2. **Monitor for 24-48 hours**
3. **Review audit logs**
4. **Adjust thresholds as needed**
5. **Deploy to production**

### Add More Services

Create blueprints for other services:

```bash
# Create blueprint for backend
mkdir -p blueprints/todo-backend
cp blueprints/todo-frontend/blueprint.yaml blueprints/todo-backend/blueprint.yaml

# Customize for backend
vim blueprints/todo-backend/blueprint.yaml

# Load blueprint
curl -X POST http://localhost:8080/api/blueprints/load \
  -d '{"path": "blueprints/todo-backend/blueprint.yaml"}'
```

### Enable Notifications

Configure Slack/email notifications:

```yaml
governance:
  approval_workflow:
    notification_channels:
      - slack://devops-alerts
      - email://devops@example.com
```

### Monitor Agent Health

Set up monitoring:

```bash
# Prometheus metrics
curl http://localhost:8080/metrics

# Grafana dashboard
# Import dashboard from dashboards/agent-system.json
```

---

## Common Questions

### How often do agents make decisions?

**Default**: Every 5 minutes (configurable)

### Can I disable automatic operations?

**Yes**, enable dry-run mode:
```bash
curl -X POST http://localhost:8080/api/config/dry-run -d '{"enabled": true}'
```

### What if I need to scale manually?

**You can**, but:
- Won't be logged in agent audit trail
- Won't be verified by agents
- May conflict with agent decisions

**Recommendation**: Use agent system for all operations

### How do I see what agents are doing?

**Check logs**:
```bash
# Agent logs
kubectl logs -n agent-system -l app=decision-engine

# Audit logs
cat logs/agent-decisions/$(date +%Y-%m-%d)/*.log
```

### Can I modify blueprints while agents are running?

**Yes**, reload blueprint:
```bash
curl -X POST http://localhost:8080/api/blueprints/reload
```

---

## Summary

**What You Learned**:
1. ✅ Core concepts (blueprints, agents, governance)
2. ✅ Deployed agent system
3. ✅ Created first blueprint
4. ✅ Saw autonomous scaling in action
5. ✅ Understood governance classifications

**What You Can Do Now**:
- Create blueprints for your services
- Let agents manage infrastructure autonomously
- Monitor decisions and operations
- Customize governance policies
- Scale with confidence

**Next Steps**:
- Read detailed documentation
- Explore demonstrations
- Customize blueprints
- Deploy to production

---

## Getting Help

**Documentation**:
- `docs/` - Complete documentation
- `examples/` - Working examples
- `demos/` - Step-by-step demonstrations

**Support**:
- GitHub Issues: Report bugs
- Slack: #spec-driven-automation
- Email: support@example.com

**Resources**:
- Website: https://spec-driven-automation.example.com
- Blog: https://blog.example.com/spec-driven
- Videos: https://youtube.com/spec-driven-automation

---

**Congratulations!** You've completed the Quick Start Guide. You're now ready to use Spec-Driven Infrastructure Automation for your services.
