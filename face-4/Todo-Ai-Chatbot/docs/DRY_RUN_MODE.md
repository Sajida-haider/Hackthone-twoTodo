# Dry-Run Mode Documentation

## Overview

Dry-Run Mode is a testing mechanism that simulates operations without executing them. It allows blueprint validation, decision testing, and governance verification without affecting the running system.

**Key Principle**: Test safely before executing in production.

## Purpose

Dry-Run Mode serves multiple purposes:

1. **Blueprint Validation**: Test new blueprints before deployment
2. **Decision Testing**: Verify agent decisions without execution
3. **Governance Testing**: Confirm governance rules work as expected
4. **Training**: Learn how agents work without risk
5. **Debugging**: Troubleshoot issues safely

## How Dry-Run Works

### Execution Flow

```
[Operation Proposed]
        ↓
[Check Dry-Run Flag]
        ↓
    ┌───┴───┐
    │       │
[Dry-Run: ON] [Dry-Run: OFF]
    │              │
[Simulate]    [Execute]
    │              │
[Log Result]  [Real Result]
    │              │
[No Changes]  [System Changed]
```

### Dry-Run Logic

```python
class ExecutionEngine:
    """
    Execution Engine with dry-run support.
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def execute(self, operation: dict) -> dict:
        """
        Execute operation (or simulate if dry-run).

        Args:
            operation: Operation to execute

        Returns:
            Execution result
        """
        if self.dry_run:
            return self.simulate_operation(operation)
        else:
            return self.execute_operation(operation)

    def simulate_operation(self, operation: dict) -> dict:
        """
        Simulate operation without executing.

        Args:
            operation: Operation to simulate

        Returns:
            Simulated result
        """
        # Log simulation
        log_event({
            'event_type': 'operation_simulated',
            'operation_id': operation['operation_id'],
            'operation_type': operation['type'],
            'dry_run': True,
            'would_execute': self.get_command(operation)
        })

        # Simulate success (or failure based on validation)
        validation_result = self.validate_operation(operation)

        if validation_result['valid']:
            return {
                'status': 'simulated_success',
                'dry_run': True,
                'would_execute': self.get_command(operation),
                'expected_outcome': self.predict_outcome(operation),
                'validation': validation_result
            }
        else:
            return {
                'status': 'simulated_failure',
                'dry_run': True,
                'would_fail_because': validation_result['reason'],
                'validation': validation_result
            }

    def execute_operation(self, operation: dict) -> dict:
        """
        Actually execute operation.

        Args:
            operation: Operation to execute

        Returns:
            Real execution result
        """
        # Execute kubectl command
        command = self.get_command(operation)
        result = subprocess.run(command, capture_output=True)

        return {
            'status': 'executed',
            'dry_run': False,
            'command': command,
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    def get_command(self, operation: dict) -> str:
        """
        Generate kubectl command for operation.
        """
        if operation['type'] == 'scale_up' or operation['type'] == 'scale_down':
            return f"kubectl scale deployment {operation['service']} --replicas={operation['target_replicas']} -n {operation['namespace']}"
        elif operation['type'] == 'adjust_resources':
            return f"kubectl set resources deployment {operation['service']} --requests=cpu={operation['cpu_request']},memory={operation['memory_request']} -n {operation['namespace']}"
        # ... other operation types

    def predict_outcome(self, operation: dict) -> dict:
        """
        Predict expected outcome of operation.
        """
        if operation['type'] == 'scale_up':
            return {
                'replicas': operation['target_replicas'],
                'expected_cpu': operation['current_cpu'] / (operation['target_replicas'] / operation['current_replicas']),
                'expected_latency': 'improved'
            }
        # ... other predictions
```

## Enabling Dry-Run Mode

### Command-Line Flag

```bash
# Run agent in dry-run mode
agent --dry-run --blueprint blueprints/frontend/blueprint.yaml

# Run specific operation in dry-run
agent scale --service todo-frontend --replicas 3 --dry-run
```

### Configuration File

```yaml
# agent-config.yaml
dry_run:
  enabled: true
  log_simulations: true
  predict_outcomes: true
```

### Environment Variable

```bash
# Enable dry-run via environment variable
export AGENT_DRY_RUN=true
agent --blueprint blueprints/frontend/blueprint.yaml
```

## Dry-Run Output

### Simulation Result Format

```json
{
  "simulation_id": "sim-20260210-180000-001",
  "timestamp": "2026-02-10T18:00:00Z",
  "dry_run": true,
  "operation": {
    "operation_id": "dec-20260210-175500-001",
    "type": "scale_up",
    "service": "todo-frontend",
    "current_replicas": 2,
    "target_replicas": 3
  },
  "simulation_result": {
    "status": "simulated_success",
    "would_execute": "kubectl scale deployment todo-frontend --replicas=3 -n todo-app",
    "expected_outcome": {
      "replicas": 3,
      "expected_cpu_utilization": 0.57,
      "expected_memory_utilization": 0.47,
      "expected_latency_p95": 150,
      "expected_improvement": "CPU reduced from 85% to 57%"
    },
    "governance_check": {
      "classification": "allowed",
      "would_execute_autonomously": true
    },
    "validation": {
      "valid": true,
      "checks_passed": [
        "Target replicas (3) within limits (1-5)",
        "Sufficient cluster capacity",
        "Cooldown period elapsed",
        "Circuit breaker closed"
      ]
    }
  },
  "actual_execution": "NOT EXECUTED (dry-run mode)",
  "system_unchanged": true
}
```

## Use Cases

### Use Case 1: Test New Blueprint

**Scenario**: Created new blueprint, want to verify it works

**Procedure**:
```bash
# 1. Enable dry-run mode
export AGENT_DRY_RUN=true

# 2. Run agent with new blueprint
agent --blueprint blueprints/frontend/blueprint-v2.yaml

# 3. Review simulation logs
cat logs/agent-decisions/simulations.log

# 4. Verify expected behavior
# - Check decision logic
# - Verify governance classification
# - Confirm expected outcomes

# 5. If satisfied, disable dry-run and deploy
export AGENT_DRY_RUN=false
agent --blueprint blueprints/frontend/blueprint-v2.yaml
```

**Benefits**:
- Catch blueprint errors before production
- Verify decision logic works as expected
- Test governance rules

### Use Case 2: Debug Decision Logic

**Scenario**: Agent making unexpected decisions, want to understand why

**Procedure**:
```bash
# 1. Enable dry-run with verbose logging
agent --dry-run --verbose --blueprint blueprints/frontend/blueprint.yaml

# 2. Trigger decision scenario
# (simulate high load, low utilization, etc.)

# 3. Review decision logs
cat logs/agent-decisions/decisions.log | jq '.decision_logic'

# 4. Analyze why decision was made
# - Check metric values
# - Verify threshold comparisons
# - Confirm governance classification

# 5. Adjust blueprint if needed
```

**Benefits**:
- Understand decision logic without affecting system
- Debug unexpected behavior safely
- Validate fixes before production

### Use Case 3: Train New Team Members

**Scenario**: New team member learning how agents work

**Procedure**:
```bash
# 1. Set up dry-run environment
export AGENT_DRY_RUN=true

# 2. Run through scenarios
agent scale --service todo-frontend --replicas 3 --dry-run
agent scale --service todo-frontend --replicas 6 --dry-run  # Beyond limits
agent optimize --service todo-frontend --dry-run

# 3. Review what would happen
cat logs/agent-decisions/simulations.log

# 4. Experiment safely
# - Try different operations
# - Test governance rules
# - Learn decision logic
```

**Benefits**:
- Safe learning environment
- No risk to production
- Hands-on experience

### Use Case 4: Validate Governance Rules

**Scenario**: Updated governance rules, want to verify they work

**Procedure**:
```bash
# 1. Enable dry-run
export AGENT_DRY_RUN=true

# 2. Test allowed operations
agent scale --service todo-frontend --replicas 3 --dry-run
# Expected: simulated_success, classification: allowed

# 3. Test restricted operations
agent scale --service todo-frontend --replicas 6 --dry-run
# Expected: simulated_success, classification: restricted, approval_required: true

# 4. Test forbidden operations
agent delete --service todo-frontend --dry-run
# Expected: simulated_failure, classification: forbidden, blocked: true

# 5. Verify governance working correctly
```

**Benefits**:
- Verify governance rules before production
- Test approval workflow
- Confirm forbidden operations blocked

## Dry-Run Limitations

### What Dry-Run Can Test

✅ Decision logic correctness
✅ Governance classification
✅ Blueprint validation
✅ Command generation
✅ Expected outcomes (predicted)

### What Dry-Run Cannot Test

❌ Actual system behavior
❌ Real performance impact
❌ Cluster capacity constraints
❌ Network issues
❌ Timing-dependent behavior

### Important Notes

1. **Predictions May Differ**: Expected outcomes are predictions, actual results may vary
2. **No Real Verification**: Cannot verify actual post-operation metrics
3. **No Rollback Testing**: Cannot test rollback since nothing was executed
4. **Limited Validation**: Some validations require real execution

## Dry-Run Best Practices

### For Blueprint Authors

1. **Always Test First**: Run dry-run before deploying new blueprints
2. **Test All Scenarios**: Test allowed, restricted, and forbidden operations
3. **Verify Predictions**: Check if predicted outcomes make sense
4. **Review Logs**: Examine simulation logs for unexpected behavior

### For Operators

1. **Use for Training**: Train new team members with dry-run
2. **Debug Safely**: Use dry-run to debug issues without risk
3. **Validate Changes**: Test blueprint changes before production
4. **Document Results**: Keep dry-run logs for reference

### For Developers

1. **Test Decision Logic**: Verify decision logic with dry-run
2. **Validate Governance**: Confirm governance rules work correctly
3. **Check Edge Cases**: Test boundary conditions safely
4. **Automate Testing**: Include dry-run in CI/CD pipeline

## Dry-Run in CI/CD

### Automated Testing

```yaml
# .github/workflows/test-blueprints.yml
name: Test Blueprints

on: [pull_request]

jobs:
  test-blueprints:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Validate Blueprint Schema
        run: |
          jsonschema -i blueprints/frontend/blueprint.yaml blueprints/schema.json

      - name: Test Blueprint in Dry-Run
        run: |
          export AGENT_DRY_RUN=true
          agent --blueprint blueprints/frontend/blueprint.yaml --test-scenarios

      - name: Verify Simulation Results
        run: |
          python scripts/verify-simulations.py logs/agent-decisions/simulations.log

      - name: Check for Errors
        run: |
          if grep -q "simulated_failure" logs/agent-decisions/simulations.log; then
            echo "Simulation failures detected"
            exit 1
          fi
```

## Dry-Run Logging

### Log Format

```json
{
  "timestamp": "2026-02-10T18:00:00Z",
  "event_type": "operation_simulated",
  "simulation_id": "sim-20260210-180000-001",
  "dry_run": true,
  "operation": {
    "type": "scale_up",
    "service": "todo-frontend",
    "target_replicas": 3
  },
  "simulation_result": "simulated_success",
  "would_execute": "kubectl scale deployment todo-frontend --replicas=3",
  "expected_outcome": {
    "cpu_utilization": 0.57,
    "latency_p95": 150
  },
  "governance_check": "allowed",
  "validation": "passed"
}
```

### Log Analysis

```bash
# Count simulated operations
cat logs/simulations.log | jq -r '.event_type' | grep operation_simulated | wc -l

# Check success rate
cat logs/simulations.log | jq -r '.simulation_result' | grep simulated_success | wc -l

# Find governance blocks
cat logs/simulations.log | jq 'select(.governance_check == "forbidden")'

# Analyze expected outcomes
cat logs/simulations.log | jq '.expected_outcome'
```

## Troubleshooting

### Problem: Dry-run predictions don't match reality

**Causes**:
- Prediction logic too simplistic
- Unexpected system behavior
- External factors not considered

**Solutions**:
- Improve prediction algorithms
- Test in staging before production
- Use dry-run as guide, not guarantee

### Problem: Dry-run mode not activating

**Causes**:
- Flag not set correctly
- Configuration override
- Environment variable not exported

**Solutions**:
- Verify dry-run flag: `echo $AGENT_DRY_RUN`
- Check configuration file
- Use explicit command-line flag

### Problem: Simulations too slow

**Causes**:
- Complex prediction logic
- Excessive logging
- Validation overhead

**Solutions**:
- Optimize prediction algorithms
- Reduce log verbosity
- Cache validation results

## See Also

- [Blueprint Validation Documentation](./BLUEPRINT_VALIDATION.md) - How blueprints are validated
- [Testing Guide](./TESTING.md) - Comprehensive testing strategies
- [CI/CD Integration](./CICD.md) - Automated testing in pipelines
