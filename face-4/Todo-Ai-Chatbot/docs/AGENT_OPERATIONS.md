# Agent Operations Guide

## Overview

This guide documents how all five agents in the Spec-Driven Infrastructure Automation system work together to manage Kubernetes infrastructure autonomously.

**The Five Agents**:
1. **Blueprint Parser** - Loads and validates blueprints
2. **Decision Engine** - Analyzes metrics and makes decisions
3. **Governance Enforcer** - Validates operations against policies
4. **Execution Engine** - Executes approved operations
5. **Verification Engine** - Verifies outcomes and triggers rollbacks

**Key Principle**: Each agent has a single, well-defined responsibility. Agents communicate through structured data formats.

---

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring System                         │
│              (Collects metrics from Kubernetes)              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Metrics
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Blueprint Parser                           │
│  • Loads blueprint YAML                                      │
│  • Validates schema                                          │
│  • Extracts policies                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Parsed Blueprint
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Decision Engine                            │
│  • Analyzes metrics against blueprint                        │
│  • Calculates weighted utilization                           │
│  • Proposes operations (scale, optimize, recover)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Decision
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Governance Enforcer                          │
│  • Classifies operation (allowed/restricted/forbidden)       │
│  • Checks safety mechanisms (circuit breaker, cooldown)      │
│  • Generates approval requests if needed                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Governance Result
                            ▼
                    ┌───────┴────────┐
                    │                │
            Allowed │                │ Restricted
                    ▼                ▼
        ┌──────────────┐    ┌──────────────┐
        │  Execution   │    │   Approval   │
        │   Engine     │    │   Workflow   │
        └──────────────┘    └──────────────┘
                    │                │
                    │                │ After Approval
                    └────────┬───────┘
                             │
                             │ Operation Result
                             ▼
        ┌─────────────────────────────────────┐
        │       Verification Engine            │
        │  • Waits for stabilization           │
        │  • Runs verification checks          │
        │  • Triggers rollback if failure      │
        └─────────────────────────────────────┘
                             │
                             │ Verification Result
                             ▼
                    ┌────────┴────────┐
                    │                 │
            Success │                 │ Failure
                    ▼                 ▼
        ┌──────────────┐    ┌──────────────┐
        │   Complete   │    │   Rollback   │
        │   (Done)     │    │   (Retry)    │
        └──────────────┘    └──────────────┘
```

---

## Agent 1: Blueprint Parser

### Responsibility

Load, validate, and parse blueprint YAML files into structured data that other agents can use.

### Inputs

- **Blueprint File Path**: Path to YAML file (e.g., `blueprints/frontend/blueprint.yaml`)
- **Schema Definition**: JSON Schema for validation

### Outputs

- **Parsed Blueprint**: Structured JSON object with all blueprint data
- **Validation Result**: Success/failure with error details

### Operations

#### 1. Load Blueprint

```python
def load_blueprint(file_path: str) -> dict:
    """
    Load blueprint YAML file.

    Args:
        file_path: Path to blueprint YAML

    Returns:
        Raw blueprint dictionary
    """
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)
```

#### 2. Validate Schema

```python
def validate_schema(blueprint: dict, schema: dict) -> ValidationResult:
    """
    Validate blueprint against JSON Schema.

    Args:
        blueprint: Raw blueprint dictionary
        schema: JSON Schema definition

    Returns:
        ValidationResult with success/errors
    """
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(blueprint))

    if errors:
        return ValidationResult(
            success=False,
            errors=[e.message for e in errors]
        )

    return ValidationResult(success=True)
```

#### 3. Parse and Extract

```python
def parse_blueprint(blueprint: dict) -> ParsedBlueprint:
    """
    Parse blueprint and extract computed values.

    Args:
        blueprint: Validated blueprint dictionary

    Returns:
        ParsedBlueprint with computed values
    """
    return ParsedBlueprint(
        metadata=blueprint['metadata'],
        spec=blueprint['spec'],
        governance=blueprint['governance'],

        # Computed values
        headroom={
            'cpu': blueprint['spec']['scaling']['target_cpu_utilization'] - 0.10,
            'memory': blueprint['spec']['scaling']['target_memory_utilization'] - 0.10
        },

        autonomy_ratio=calculate_autonomy_ratio(blueprint['governance']),

        # Readiness flags
        ready_for_decision_engine=True,
        ready_for_governance_enforcer=True,
        ready_for_execution_engine=True
    )
```

### Data Format

**Output: Parsed Blueprint**

```json
{
  "metadata": {
    "name": "todo-frontend",
    "version": "1.0.0"
  },
  "spec": {
    "scaling": {
      "min_replicas": 1,
      "max_replicas": 5,
      "target_cpu_utilization": 0.70,
      "scale_up_threshold": 0.80
    }
  },
  "governance": {
    "agent_authority": {
      "allowed_operations": [...]
    }
  },
  "computed": {
    "headroom": {
      "cpu": 0.60,
      "memory": 0.70
    },
    "autonomy_ratio": 0.85
  }
}
```

### Error Handling

```python
class BlueprintParseError(Exception):
    """Raised when blueprint parsing fails."""
    pass

try:
    blueprint = parser.parse_blueprint(file_path)
except BlueprintParseError as e:
    logger.error(f"Blueprint parsing failed: {e}")
    # Notify operators
    # Do not proceed with decision making
```

---

## Agent 2: Decision Engine

### Responsibility

Analyze metrics against blueprint targets and propose operations (scaling, optimization, recovery).

### Inputs

- **Parsed Blueprint**: From Blueprint Parser
- **Current Metrics**: From monitoring system
- **Current State**: From Kubernetes API

### Outputs

- **Decision**: Proposed operation with rationale
- **Expected Outcome**: Predicted metrics after operation

### Operations

#### 1. Calculate Weighted Utilization

```python
def calculate_weighted_utilization(metrics: dict, blueprint: dict) -> float:
    """
    Calculate weighted utilization score.

    Formula: (CPU * 0.5) + (Memory * 0.3) + (Latency * 0.2)

    Args:
        metrics: Current metrics
        blueprint: Parsed blueprint

    Returns:
        Weighted utilization (0.0 to 1.0+)
    """
    cpu_weight = 0.5
    memory_weight = 0.3
    latency_weight = 0.2

    cpu_util = metrics['cpu_utilization']
    memory_util = metrics['memory_utilization']

    # Normalize latency (0.0 = at target, 1.0 = 2x target)
    latency_target = blueprint['spec']['performance']['latency_p95_target']
    latency_util = metrics['latency_p95'] / latency_target

    weighted = (
        cpu_util * cpu_weight +
        memory_util * memory_weight +
        latency_util * latency_weight
    )

    return weighted
```

#### 2. Make Scaling Decision

```python
def make_scaling_decision(
    metrics: dict,
    blueprint: dict,
    current_state: dict
) -> Decision:
    """
    Decide if scaling is needed.

    Args:
        metrics: Current metrics
        blueprint: Parsed blueprint
        current_state: Current Kubernetes state

    Returns:
        Decision object
    """
    weighted_util = calculate_weighted_utilization(metrics, blueprint)

    scale_up_threshold = blueprint['spec']['scaling']['scale_up_threshold']
    scale_down_threshold = blueprint['spec']['scaling']['scale_down_threshold']

    if weighted_util > scale_up_threshold:
        target_replicas = calculate_target_replicas(
            current_state['replicas'],
            weighted_util,
            blueprint['spec']['scaling']['target_cpu_utilization']
        )

        return Decision(
            decision_id=generate_id(),
            decision_type='scaling',
            action='scale_up',
            current_replicas=current_state['replicas'],
            target_replicas=target_replicas,
            rationale=f"Weighted utilization ({weighted_util:.1%}) exceeds threshold ({scale_up_threshold:.1%})",
            weighted_utilization=weighted_util
        )

    elif weighted_util < scale_down_threshold:
        target_replicas = max(
            blueprint['spec']['scaling']['min_replicas'],
            current_state['replicas'] - 1
        )

        return Decision(
            decision_id=generate_id(),
            decision_type='scaling',
            action='scale_down',
            current_replicas=current_state['replicas'],
            target_replicas=target_replicas,
            rationale=f"Weighted utilization ({weighted_util:.1%}) below threshold ({scale_down_threshold:.1%})",
            weighted_utilization=weighted_util
        )

    else:
        return Decision(
            decision_id=generate_id(),
            decision_type='no_action',
            action='no_action',
            rationale=f"Utilization ({weighted_util:.1%}) within acceptable range"
        )
```

### Data Format

**Output: Decision**

```json
{
  "decision_id": "dec-20260210-153000-001",
  "decision_type": "scaling",
  "action": "scale_up",
  "current_replicas": 2,
  "target_replicas": 3,
  "rationale": "Weighted utilization (81.5%) exceeds threshold (80%)",
  "weighted_utilization": 0.815,
  "expected_outcome": {
    "replicas": 3,
    "expected_cpu_utilization": 0.57,
    "expected_memory_utilization": 0.47
  },
  "timestamp": "2026-02-10T15:30:00Z"
}
```

---

## Agent 3: Governance Enforcer

### Responsibility

Validate operations against governance policies and classify as allowed/restricted/forbidden.

### Inputs

- **Decision**: From Decision Engine
- **Parsed Blueprint**: From Blueprint Parser
- **Safety State**: Circuit breaker, cooldown, rate limits

### Outputs

- **Governance Result**: Classification and authorization
- **Approval Request**: If operation is restricted

### Operations

#### 1. Classify Operation

```python
def classify_operation(
    decision: Decision,
    blueprint: ParsedBlueprint,
    safety_state: SafetyState
) -> GovernanceResult:
    """
    Classify operation as allowed/restricted/forbidden.

    Args:
        decision: Proposed operation
        blueprint: Parsed blueprint
        safety_state: Current safety mechanism state

    Returns:
        GovernanceResult with classification
    """
    # Check forbidden operations first (highest priority)
    for forbidden in blueprint.governance.agent_authority.forbidden_operations:
        if matches_operation(decision, forbidden):
            return GovernanceResult(
                classification='forbidden',
                blocked=True,
                rationale=forbidden.rationale,
                alternatives=forbidden.alternatives
            )

    # Check safety mechanisms
    if not check_safety_mechanisms(safety_state):
        return GovernanceResult(
            classification='blocked',
            blocked=True,
            rationale='Safety mechanism triggered (circuit breaker or cooldown)'
        )

    # Check requires_approval
    for restricted in blueprint.governance.agent_authority.requires_approval:
        if matches_operation(decision, restricted):
            return GovernanceResult(
                classification='restricted',
                requires_approval=True,
                approvers=restricted.approvers,
                risk_level=restricted.risk_level,
                rationale=f"Operation requires approval: {restricted.condition}"
            )

    # Check allowed_operations
    for allowed in blueprint.governance.agent_authority.allowed_operations:
        if matches_operation(decision, allowed):
            return GovernanceResult(
                classification='allowed',
                requires_approval=False,
                autonomous=True,
                rationale=f"Operation within allowed parameters: {allowed.condition}"
            )

    # Default: requires approval
    return GovernanceResult(
        classification='restricted',
        requires_approval=True,
        rationale='Operation not explicitly allowed, requires approval'
    )
```

#### 2. Check Safety Mechanisms

```python
def check_safety_mechanisms(safety_state: SafetyState) -> bool:
    """
    Check if safety mechanisms allow operation.

    Args:
        safety_state: Current safety state

    Returns:
        True if safe to proceed
    """
    # Check circuit breaker
    if safety_state.circuit_breaker.state == 'open':
        return False

    # Check cooldown period
    if not safety_state.cooldown.elapsed:
        return False

    # Check rate limiting
    if safety_state.rate_limiter.exceeded:
        return False

    return True
```

### Data Format

**Output: Governance Result**

```json
{
  "governance_check_id": "gov-20260210-153030-001",
  "decision_id": "dec-20260210-153000-001",
  "classification": "allowed",
  "requires_approval": false,
  "blocked": false,
  "rationale": "Target replicas (3) within blueprint limits (1-5)",
  "blueprint_references": [
    "spec.scaling.min_replicas",
    "spec.scaling.max_replicas"
  ],
  "safety_checks": {
    "circuit_breaker": "closed",
    "cooldown_elapsed": true,
    "rate_limit_ok": true
  },
  "timestamp": "2026-02-10T15:30:30Z"
}
```

---

## Agent 4: Execution Engine

### Responsibility

Execute approved operations against Kubernetes cluster.

### Inputs

- **Decision**: From Decision Engine
- **Governance Result**: From Governance Enforcer (must be "allowed" or approved)

### Outputs

- **Operation Result**: Success/failure with execution details
- **Post-Operation State**: Kubernetes state after operation

### Operations

#### 1. Execute Operation

```python
def execute_operation(
    decision: Decision,
    governance_result: GovernanceResult
) -> OperationResult:
    """
    Execute approved operation.

    Args:
        decision: Approved decision
        governance_result: Governance authorization

    Returns:
        OperationResult with execution details
    """
    # Verify authorization
    if governance_result.classification == 'forbidden':
        raise OperationBlockedError("Operation is forbidden")

    if governance_result.classification == 'restricted' and not governance_result.approved:
        raise OperationBlockedError("Operation requires approval")

    # Capture pre-operation state
    pre_state = capture_current_state(decision.service)

    # Build command
    command = build_kubectl_command(decision)

    # Execute
    start_time = time.time()
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=30
    )
    duration = time.time() - start_time

    # Capture post-operation state
    post_state = capture_current_state(decision.service)

    return OperationResult(
        operation_id=decision.decision_id,
        operation_type=decision.action,
        execution={
            'started_at': start_time,
            'completed_at': time.time(),
            'duration': duration,
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        },
        pre_operation_state=pre_state,
        post_operation_state=post_state,
        success=result.returncode == 0
    )
```

#### 2. Build Kubectl Command

```python
def build_kubectl_command(decision: Decision) -> list:
    """
    Build kubectl command from decision.

    Args:
        decision: Decision object

    Returns:
        Command as list of strings
    """
    if decision.action == 'scale_up' or decision.action == 'scale_down':
        return [
            'kubectl', 'scale',
            'deployment', decision.service,
            f'--replicas={decision.target_replicas}',
            '-n', decision.namespace
        ]

    elif decision.action == 'adjust_resources':
        return [
            'kubectl', 'set', 'resources',
            'deployment', decision.service,
            f'--requests=cpu={decision.cpu_request},memory={decision.memory_request}',
            f'--limits=cpu={decision.cpu_limit},memory={decision.memory_limit}',
            '-n', decision.namespace
        ]

    else:
        raise ValueError(f"Unknown action: {decision.action}")
```

### Data Format

**Output: Operation Result**

```json
{
  "operation_id": "dec-20260210-153000-001",
  "operation_type": "scale_up",
  "execution": {
    "started_at": "2026-02-10T15:30:45Z",
    "completed_at": "2026-02-10T15:30:47Z",
    "duration": "2.3s",
    "exit_code": 0,
    "stdout": "deployment.apps/todo-frontend scaled",
    "stderr": ""
  },
  "pre_operation_state": {
    "replicas": 2,
    "pods_running": 2,
    "pods_ready": 2
  },
  "post_operation_state": {
    "replicas": 3,
    "pods_running": 2,
    "pods_ready": 2,
    "pods_pending": 1
  },
  "success": true
}
```

---

## Agent 5: Verification Engine

### Responsibility

Verify operation outcomes and trigger rollbacks if verification fails.

### Inputs

- **Operation Result**: From Execution Engine
- **Parsed Blueprint**: From Blueprint Parser
- **Current Metrics**: From monitoring system (after stabilization)

### Outputs

- **Verification Result**: Success/failure with check details
- **Rollback Decision**: If verification fails

### Operations

#### 1. Verify Operation

```python
def verify_operation(
    operation_result: OperationResult,
    blueprint: ParsedBlueprint,
    stabilization_period: int = 60
) -> VerificationResult:
    """
    Verify operation outcome.

    Args:
        operation_result: Result from execution
        blueprint: Parsed blueprint
        stabilization_period: Seconds to wait before checking

    Returns:
        VerificationResult with check details
    """
    # Wait for stabilization
    time.sleep(stabilization_period)

    # Collect current metrics
    metrics = collect_metrics(operation_result.service)
    state = get_current_state(operation_result.service)

    # Run verification checks
    checks = []

    # Check 1: Replica count
    checks.append(verify_replica_count(
        expected=operation_result.decision.target_replicas,
        actual=state.replicas
    ))

    # Check 2: Pods ready
    checks.append(verify_pods_ready(
        expected=operation_result.decision.target_replicas,
        actual=state.pods_ready
    ))

    # Check 3: CPU utilization
    checks.append(verify_cpu_utilization(
        actual=metrics.cpu_utilization,
        target=blueprint.spec.scaling.target_cpu_utilization
    ))

    # Check 4: Latency (CRITICAL)
    latency_check = verify_latency(
        actual=metrics.latency_p95,
        target=blueprint.spec.performance.latency_p95_target
    )
    checks.append(latency_check)

    # Check 5: Error rate (CRITICAL)
    error_check = verify_error_rate(
        actual=metrics.error_rate,
        threshold=blueprint.spec.performance.error_rate_threshold
    )
    checks.append(error_check)

    # Determine outcome
    critical_failures = [c for c in checks if not c.passed and c.critical]

    if critical_failures:
        return VerificationResult(
            outcome='failure',
            checks=checks,
            rollback_required=True,
            rollback_reason=f"Critical checks failed: {[c.name for c in critical_failures]}"
        )

    return VerificationResult(
        outcome='success',
        checks=checks,
        rollback_required=False
    )
```

#### 2. Trigger Rollback

```python
def trigger_rollback(
    verification_result: VerificationResult,
    operation_result: OperationResult
) -> RollbackDecision:
    """
    Trigger automatic rollback.

    Args:
        verification_result: Failed verification
        operation_result: Original operation

    Returns:
        RollbackDecision
    """
    return RollbackDecision(
        rollback_id=generate_id(),
        triggered_by='verification-engine',
        trigger_reason='critical_verification_failure',
        original_operation_id=operation_result.operation_id,
        rollback_plan={
            'action': reverse_action(operation_result.operation_type),
            'from_replicas': operation_result.post_operation_state.replicas,
            'to_replicas': operation_result.pre_operation_state.replicas,
            'rationale': 'Restore to pre-operation state due to verification failure'
        },
        automatic=True
    )
```

### Data Format

**Output: Verification Result**

```json
{
  "verification_id": "ver-20260210-153200-001",
  "operation_id": "dec-20260210-153000-001",
  "verification_timestamp": "2026-02-10T15:32:00Z",
  "outcome": "success",
  "checks": [
    {
      "check": "replica_count",
      "expected": 3,
      "actual": 3,
      "status": "passed",
      "critical": true
    },
    {
      "check": "cpu_utilization",
      "expected": "< 70%",
      "actual": "60%",
      "status": "passed",
      "improvement": "25% reduction"
    }
  ],
  "summary": {
    "total_checks": 6,
    "passed": 6,
    "failed": 0,
    "verification_result": "success"
  },
  "rollback_required": false
}
```

---

## Complete Workflow

### Scenario: Autonomous Scaling

```
1. Monitoring System → Metrics
   ↓
2. Blueprint Parser → Parsed Blueprint
   ↓
3. Decision Engine → Decision (scale_up)
   ↓
4. Governance Enforcer → Governance Result (allowed)
   ↓
5. Execution Engine → Operation Result (success)
   ↓
6. Verification Engine → Verification Result (success)
   ↓
7. Complete
```

### Scenario: Approval Required

```
1. Monitoring System → Metrics
   ↓
2. Blueprint Parser → Parsed Blueprint
   ↓
3. Decision Engine → Decision (scale_beyond_limits)
   ↓
4. Governance Enforcer → Governance Result (restricted)
   ↓
5. Approval Workflow → Approval Request
   ↓
6. Human Approver → Approval Response
   ↓
7. Execution Engine → Operation Result (success)
   ↓
8. Verification Engine → Verification Result (success)
   ↓
9. Complete
```

### Scenario: Rollback on Failure

```
1. Monitoring System → Metrics
   ↓
2. Blueprint Parser → Parsed Blueprint
   ↓
3. Decision Engine → Decision (scale_down)
   ↓
4. Governance Enforcer → Governance Result (allowed)
   ↓
5. Execution Engine → Operation Result (success)
   ↓
6. Verification Engine → Verification Result (failure)
   ↓
7. Verification Engine → Rollback Decision
   ↓
8. Execution Engine → Rollback Operation (success)
   ↓
9. Verification Engine → Rollback Verification (success)
   ↓
10. Complete (Rolled Back)
```

---

## Data Flow Between Agents

### Agent Communication Protocol

All agents communicate through structured JSON messages:

```python
class AgentMessage:
    """Base class for agent messages."""
    message_id: str
    timestamp: datetime
    source_agent: str
    target_agent: str
    message_type: str
    payload: dict
```

### Example: Decision Engine → Governance Enforcer

```json
{
  "message_id": "msg-20260210-153000-001",
  "timestamp": "2026-02-10T15:30:00Z",
  "source_agent": "decision-engine-001",
  "target_agent": "governance-enforcer-001",
  "message_type": "decision_for_governance_check",
  "payload": {
    "decision_id": "dec-20260210-153000-001",
    "action": "scale_up",
    "target_replicas": 3
  }
}
```

---

## Error Handling

### Agent-Level Errors

Each agent handles its own errors:

```python
try:
    decision = decision_engine.make_decision(metrics, blueprint)
except DecisionEngineError as e:
    logger.error(f"Decision engine failed: {e}")
    # Notify operators
    # Do not proceed to governance check
    return ErrorResult(
        agent='decision-engine',
        error=str(e),
        recovery_action='retry_after_delay'
    )
```

### Cross-Agent Error Propagation

Errors propagate through the workflow:

```python
# If Blueprint Parser fails
if not blueprint_result.success:
    # Decision Engine cannot proceed
    # Governance Enforcer cannot proceed
    # Entire workflow stops
    return WorkflowError(
        stage='blueprint_parsing',
        error=blueprint_result.error
    )
```

---

## Monitoring and Observability

### Agent Health Checks

```python
def health_check() -> HealthStatus:
    """Check agent health."""
    return HealthStatus(
        agent_id='decision-engine-001',
        status='healthy',
        last_decision='2026-02-10T15:30:00Z',
        decisions_last_hour=12,
        errors_last_hour=0
    )
```

### Agent Metrics

- **Decisions per minute**: Rate of decisions made
- **Governance checks per minute**: Rate of governance evaluations
- **Operations per minute**: Rate of executions
- **Verification success rate**: Percentage of successful verifications
- **Rollback rate**: Percentage of operations requiring rollback

---

## Best Practices

### 1. Single Responsibility

✅ **Each agent has one job**
- Blueprint Parser: Parse blueprints
- Decision Engine: Make decisions
- Governance Enforcer: Enforce policies
- Execution Engine: Execute operations
- Verification Engine: Verify outcomes

### 2. Structured Communication

✅ **Use structured data formats**
- JSON for all inter-agent communication
- Well-defined schemas
- Versioned message formats

### 3. Error Isolation

✅ **Isolate errors per agent**
- Agent errors don't crash other agents
- Graceful degradation
- Clear error propagation

### 4. Audit Everything

✅ **Log all agent actions**
- Every decision logged
- Every governance check logged
- Every operation logged
- Every verification logged

### 5. Idempotency

✅ **Operations should be idempotent**
- Safe to retry
- Same result if executed multiple times
- No side effects from retries

---

## Troubleshooting

### Problem: Decision Engine not making decisions

**Check**:
- Blueprint Parser successfully loaded blueprint?
- Metrics being collected?
- Decision Engine health check passing?

**Solution**:
```bash
# Check Blueprint Parser
curl http://agent-system/api/agents/blueprint-parser/health

# Check metrics
curl http://agent-system/api/metrics/todo-frontend

# Check Decision Engine logs
kubectl logs -l app=decision-engine
```

### Problem: Operations not executing

**Check**:
- Governance Enforcer allowing operation?
- Circuit breaker open?
- Cooldown period active?

**Solution**:
```bash
# Check governance result
cat logs/agent-decisions/$(date +%Y-%m-%d)/governance.log | \
  jq '.classification'

# Check safety mechanisms
curl http://agent-system/api/safety/circuit-breaker
curl http://agent-system/api/safety/cooldown
```

### Problem: Frequent rollbacks

**Check**:
- Verification checks too strict?
- Stabilization period too short?
- Blueprint targets unrealistic?

**Solution**:
```bash
# Review verification failures
cat logs/agent-decisions/$(date +%Y-%m-%d)/verifications.log | \
  jq 'select(.outcome == "failure")'

# Adjust blueprint
# Increase stabilization_period
# Relax verification thresholds
```

---

## See Also

- **Blueprint Format**: `docs/BLUEPRINT_FORMAT.md`
- **Decision Engine**: `docs/DECISION_ENGINE.md`
- **Governance**: `docs/GOVERNANCE.md`
- **Verification**: `docs/VERIFICATION_ENGINE.md`
- **Audit Logging**: `docs/AUDIT_LOGGING.md`
