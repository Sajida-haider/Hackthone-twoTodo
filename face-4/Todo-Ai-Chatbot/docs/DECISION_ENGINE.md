# Decision Engine Documentation

## Overview

The Decision Engine is the core agent that compares current system state to blueprint targets and recommends actions. It reads parsed blueprint policies and current metrics, applies decision rules, and generates recommendations with clear rationale and blueprint references.

**Key Responsibility**: Make autonomous infrastructure decisions based on blueprint policies, not human judgment.

## Decision Engine Architecture

```
Parsed Blueprint Policies + Current Metrics
                ↓
        [Collect Metrics]
                ↓
        [Compare to Targets]
                ↓
        [Apply Decision Rules]
                ↓
        [Generate Rationale]
                ↓
Recommended Action + Blueprint References
```

## Decision Types

The Decision Engine handles three types of decisions:

1. **Scaling Decisions**: When to scale up/down based on utilization
2. **Resource Optimization**: When to adjust CPU/memory requests/limits
3. **Failure Recovery**: When to restart pods or trigger rollback

## 1. Scaling Decisions

### Scaling Decision Logic

```python
def make_scaling_decision(
    current_metrics: dict,
    scaling_policy: ScalingPolicy
) -> dict:
    """
    Determine if scaling is needed based on current metrics and blueprint policy.

    Args:
        current_metrics: Current system state
            {
                'replicas': 2,
                'cpu_utilization': 0.85,
                'memory_utilization': 0.70,
                'latency_p95': 180
            }
        scaling_policy: Scaling policy from blueprint
            {
                'min_replicas': 1,
                'max_replicas': 5,
                'scale_up_threshold': 0.80,
                'scale_down_threshold': 0.30,
                'cooldown_period': 60,
                'metrics': [
                    {'type': 'cpu', 'weight': 0.5},
                    {'type': 'memory', 'weight': 0.3},
                    {'type': 'latency', 'weight': 0.2}
                ]
            }

    Returns:
        Decision dictionary with action, rationale, and blueprint references
    """
    # Step 1: Calculate weighted utilization
    weighted_utilization = calculate_weighted_utilization(
        current_metrics,
        scaling_policy['metrics']
    )

    # Step 2: Check cooldown period
    if not cooldown_elapsed(scaling_policy['cooldown_period']):
        return {
            'action': 'no_action',
            'reason': 'cooldown_period_not_elapsed',
            'rationale': f"Last scaling operation was {seconds_since_last_operation}s ago, "
                        f"cooldown period is {scaling_policy['cooldown_period']}s",
            'blueprint_references': ['spec.scaling.cooldown_period']
        }

    # Step 3: Determine scaling action
    current_replicas = current_metrics['replicas']

    # Scale up logic
    if weighted_utilization > scaling_policy['scale_up_threshold']:
        if current_replicas < scaling_policy['max_replicas']:
            target_replicas = current_replicas + 1
            return {
                'action': 'scale_up',
                'current_replicas': current_replicas,
                'target_replicas': target_replicas,
                'rationale': (
                    f"Weighted utilization ({weighted_utilization:.2%}) exceeds "
                    f"scale_up_threshold ({scaling_policy['scale_up_threshold']:.2%}). "
                    f"Current replicas ({current_replicas}) < max_replicas "
                    f"({scaling_policy['max_replicas']}). Scaling to {target_replicas}."
                ),
                'blueprint_references': [
                    'spec.scaling.scale_up_threshold',
                    'spec.scaling.max_replicas'
                ],
                'metrics_breakdown': {
                    'cpu': current_metrics['cpu_utilization'],
                    'memory': current_metrics['memory_utilization'],
                    'weighted': weighted_utilization
                }
            }
        else:
            return {
                'action': 'no_action',
                'reason': 'at_max_replicas',
                'rationale': (
                    f"Weighted utilization ({weighted_utilization:.2%}) exceeds threshold, "
                    f"but already at max_replicas ({scaling_policy['max_replicas']}). "
                    f"Cannot scale further."
                ),
                'blueprint_references': ['spec.scaling.max_replicas'],
                'recommendation': 'Consider increasing max_replicas if sustained high utilization'
            }

    # Scale down logic
    elif weighted_utilization < scaling_policy['scale_down_threshold']:
        if current_replicas > scaling_policy['min_replicas']:
            target_replicas = current_replicas - 1
            return {
                'action': 'scale_down',
                'current_replicas': current_replicas,
                'target_replicas': target_replicas,
                'rationale': (
                    f"Weighted utilization ({weighted_utilization:.2%}) below "
                    f"scale_down_threshold ({scaling_policy['scale_down_threshold']:.2%}). "
                    f"Current replicas ({current_replicas}) > min_replicas "
                    f"({scaling_policy['min_replicas']}). Scaling to {target_replicas}."
                ),
                'blueprint_references': [
                    'spec.scaling.scale_down_threshold',
                    'spec.scaling.min_replicas'
                ],
                'metrics_breakdown': {
                    'cpu': current_metrics['cpu_utilization'],
                    'memory': current_metrics['memory_utilization'],
                    'weighted': weighted_utilization
                }
            }
        else:
            return {
                'action': 'no_action',
                'reason': 'at_min_replicas',
                'rationale': (
                    f"Weighted utilization ({weighted_utilization:.2%}) below threshold, "
                    f"but already at min_replicas ({scaling_policy['min_replicas']}). "
                    f"Cannot scale further."
                ),
                'blueprint_references': ['spec.scaling.min_replicas']
            }

    # No scaling needed
    else:
        return {
            'action': 'no_action',
            'reason': 'within_thresholds',
            'rationale': (
                f"Weighted utilization ({weighted_utilization:.2%}) is between "
                f"scale_down_threshold ({scaling_policy['scale_down_threshold']:.2%}) and "
                f"scale_up_threshold ({scaling_policy['scale_up_threshold']:.2%}). "
                f"No scaling needed."
            ),
            'blueprint_references': [
                'spec.scaling.scale_up_threshold',
                'spec.scaling.scale_down_threshold'
            ]
        }
```

### Weighted Utilization Calculation

```python
def calculate_weighted_utilization(
    current_metrics: dict,
    metric_weights: list
) -> float:
    """
    Calculate weighted utilization across multiple metrics.

    Args:
        current_metrics: Current metric values
        metric_weights: Metric types and weights from blueprint

    Returns:
        Weighted utilization as decimal (0.0 to 1.0)
    """
    weighted_sum = 0.0

    for metric in metric_weights:
        metric_type = metric['type']
        weight = metric['weight']

        if metric_type == 'cpu':
            value = current_metrics['cpu_utilization']
        elif metric_type == 'memory':
            value = current_metrics['memory_utilization']
        elif metric_type == 'latency':
            # Normalize latency to 0-1 scale
            # If latency > target, utilization = 1.0 (needs scaling)
            # If latency <= target, utilization = latency / target
            target_latency = current_metrics.get('latency_p95_target', 200)
            actual_latency = current_metrics.get('latency_p95', 0)
            value = min(actual_latency / target_latency, 1.0)
        else:
            value = 0.0

        weighted_sum += value * weight

    return weighted_sum
```

### Scaling Decision Examples

**Example 1: Scale Up (High CPU)**

```
Input:
  current_metrics: {replicas: 2, cpu: 85%, memory: 70%, latency_p95: 180ms}
  scaling_policy: {min: 1, max: 5, scale_up: 80%, scale_down: 30%, cooldown: 60s}
  metrics: [{cpu: 0.5}, {memory: 0.3}, {latency: 0.2}]

Calculation:
  weighted_utilization = (0.85 * 0.5) + (0.70 * 0.3) + (0.90 * 0.2)
                       = 0.425 + 0.210 + 0.180
                       = 0.815 = 81.5%

Decision:
  81.5% > 80% (scale_up_threshold) → Scale up
  2 < 5 (current < max) → Can scale
  Target: 3 replicas

Output:
  {
    "action": "scale_up",
    "current_replicas": 2,
    "target_replicas": 3,
    "rationale": "Weighted utilization (81.5%) exceeds scale_up_threshold (80%). Scaling to 3 replicas.",
    "blueprint_references": ["spec.scaling.scale_up_threshold", "spec.scaling.max_replicas"]
  }
```

**Example 2: Scale Down (Low Utilization)**

```
Input:
  current_metrics: {replicas: 3, cpu: 25%, memory: 20%, latency_p95: 100ms}
  scaling_policy: {min: 1, max: 5, scale_up: 80%, scale_down: 30%, cooldown: 60s}

Calculation:
  weighted_utilization = (0.25 * 0.5) + (0.20 * 0.3) + (0.50 * 0.2)
                       = 0.125 + 0.060 + 0.100
                       = 0.285 = 28.5%

Decision:
  28.5% < 30% (scale_down_threshold) → Scale down
  3 > 1 (current > min) → Can scale
  Target: 2 replicas

Output:
  {
    "action": "scale_down",
    "current_replicas": 3,
    "target_replicas": 2,
    "rationale": "Weighted utilization (28.5%) below scale_down_threshold (30%). Scaling to 2 replicas.",
    "blueprint_references": ["spec.scaling.scale_down_threshold", "spec.scaling.min_replicas"]
  }
```

**Example 3: No Action (Within Thresholds)**

```
Input:
  current_metrics: {replicas: 2, cpu: 60%, memory: 55%, latency_p95: 150ms}
  scaling_policy: {min: 1, max: 5, scale_up: 80%, scale_down: 30%, cooldown: 60s}

Calculation:
  weighted_utilization = (0.60 * 0.5) + (0.55 * 0.3) + (0.75 * 0.2)
                       = 0.300 + 0.165 + 0.150
                       = 0.615 = 61.5%

Decision:
  30% < 61.5% < 80% → Within thresholds
  No action needed

Output:
  {
    "action": "no_action",
    "reason": "within_thresholds",
    "rationale": "Weighted utilization (61.5%) is between scale_down_threshold (30%) and scale_up_threshold (80%). No scaling needed."
  }
```

## 2. Resource Optimization Decisions

### Resource Optimization Logic

```python
def make_optimization_decision(
    current_metrics: dict,
    resource_policy: ResourcePolicy
) -> dict:
    """
    Determine if resource optimization is needed.

    Args:
        current_metrics: Current resource usage
            {
                'cpu_request': '50m',
                'cpu_usage': '30m',
                'memory_request': '128Mi',
                'memory_usage': '100Mi'
            }
        resource_policy: Resource policy from blueprint
            {
                'cpu_target_utilization': 0.70,
                'memory_target_utilization': 0.80,
                'optimization_threshold': 0.10
            }

    Returns:
        Optimization recommendation
    """
    recommendations = []

    # Check CPU optimization
    cpu_recommendation = check_resource_optimization(
        resource_type='cpu',
        current_request=parse_cpu(current_metrics['cpu_request']),
        current_usage=parse_cpu(current_metrics['cpu_usage']),
        target_utilization=resource_policy['cpu_target_utilization'],
        optimization_threshold=resource_policy['optimization_threshold']
    )
    if cpu_recommendation:
        recommendations.append(cpu_recommendation)

    # Check memory optimization
    memory_recommendation = check_resource_optimization(
        resource_type='memory',
        current_request=parse_memory(current_metrics['memory_request']),
        current_usage=parse_memory(current_metrics['memory_usage']),
        target_utilization=resource_policy['memory_target_utilization'],
        optimization_threshold=resource_policy['optimization_threshold']
    )
    if memory_recommendation:
        recommendations.append(memory_recommendation)

    if recommendations:
        return {
            'action': 'optimize_resources',
            'recommendations': recommendations,
            'blueprint_references': [
                'spec.resources.cpu.target_utilization',
                'spec.resources.memory.target_utilization',
                'spec.resources.cpu.optimization_threshold'
            ]
        }
    else:
        return {
            'action': 'no_action',
            'reason': 'resources_optimized',
            'rationale': 'Resource usage is within optimization thresholds'
        }


def check_resource_optimization(
    resource_type: str,
    current_request: int,
    current_usage: int,
    target_utilization: float,
    optimization_threshold: float
) -> dict:
    """
    Check if a specific resource needs optimization.

    Returns:
        Optimization recommendation or None
    """
    # Calculate current utilization
    current_utilization = current_usage / current_request

    # Calculate target request (usage / target_utilization)
    target_request = int(current_usage / target_utilization)

    # Calculate difference percentage
    difference = abs(target_request - current_request) / current_request

    # Check if difference exceeds threshold
    if difference > optimization_threshold:
        # Determine if approval is required (>10% change)
        requires_approval = difference > 0.10

        return {
            'resource_type': resource_type,
            'current_request': current_request,
            'current_usage': current_usage,
            'current_utilization': current_utilization,
            'target_request': target_request,
            'target_utilization': target_utilization,
            'difference_percent': difference,
            'requires_approval': requires_approval,
            'rationale': (
                f"{resource_type.upper()} usage ({current_usage}) is "
                f"{current_utilization:.1%} of request ({current_request}). "
                f"Target utilization is {target_utilization:.1%}. "
                f"Recommend adjusting request to {target_request} "
                f"({difference:.1%} change)."
            )
        }
    else:
        return None
```

### Resource Optimization Examples

**Example 1: Over-Provisioned CPU (Autonomous)**

```
Input:
  current: {cpu_request: 100m, cpu_usage: 30m}
  target_utilization: 70%
  optimization_threshold: 10%

Calculation:
  current_utilization = 30m / 100m = 30%
  target_request = 30m / 0.70 = 43m
  difference = |43m - 100m| / 100m = 57%

Decision:
  57% > 10% (optimization_threshold) → Optimize
  57% > 10% → Requires approval

Output:
  {
    "action": "optimize_resources",
    "resource_type": "cpu",
    "current_request": "100m",
    "target_request": "43m",
    "difference": "57%",
    "requires_approval": true,
    "rationale": "CPU usage (30m) is 30% of request (100m). Target utilization is 70%. Recommend adjusting request to 43m (57% reduction)."
  }
```

**Example 2: Under-Provisioned Memory (Autonomous)**

```
Input:
  current: {memory_request: 128Mi, memory_usage: 110Mi}
  target_utilization: 80%
  optimization_threshold: 10%

Calculation:
  current_utilization = 110Mi / 128Mi = 86%
  target_request = 110Mi / 0.80 = 138Mi
  difference = |138Mi - 128Mi| / 128Mi = 8%

Decision:
  8% < 10% (optimization_threshold) → No optimization needed

Output:
  {
    "action": "no_action",
    "reason": "resources_optimized",
    "rationale": "Memory usage is within optimization thresholds (8% difference)"
  }
```

## 3. Failure Recovery Decisions

### Failure Recovery Logic

```python
def make_recovery_decision(
    pod_status: dict,
    reliability_policy: ReliabilityPolicy
) -> dict:
    """
    Determine recovery action for failed pod.

    Args:
        pod_status: Current pod status
            {
                'name': 'todo-backend-abc123',
                'status': 'CrashLoopBackOff',
                'restart_count': 2,
                'last_restart': '2026-02-10T15:25:00Z'
            }
        reliability_policy: Reliability policy from blueprint
            {
                'max_restart_count': 3,
                'rollback_threshold': 2,
                'rollback_on_failure': true
            }

    Returns:
        Recovery decision
    """
    restart_count = pod_status['restart_count']
    max_restart_count = reliability_policy['max_restart_count']
    rollback_threshold = reliability_policy['rollback_threshold']

    # Check if pod has exceeded restart limit
    if restart_count >= max_restart_count:
        # Escalate to approval workflow
        return {
            'action': 'escalate_to_approval',
            'reason': 'max_restarts_exceeded',
            'pod_name': pod_status['name'],
            'restart_count': restart_count,
            'max_restart_count': max_restart_count,
            'rationale': (
                f"Pod {pod_status['name']} has restart_count ({restart_count}) >= "
                f"max_restart_count ({max_restart_count}). Escalating to approval workflow."
            ),
            'blueprint_references': ['spec.reliability.max_restart_count'],
            'recommended_action': 'rollback_deployment'
        }

    # Check if rollback should be triggered
    elif (restart_count >= rollback_threshold and
          reliability_policy['rollback_on_failure']):
        return {
            'action': 'trigger_rollback',
            'reason': 'rollback_threshold_exceeded',
            'pod_name': pod_status['name'],
            'restart_count': restart_count,
            'rollback_threshold': rollback_threshold,
            'rationale': (
                f"Pod {pod_status['name']} has restart_count ({restart_count}) >= "
                f"rollback_threshold ({rollback_threshold}). Triggering automatic rollback."
            ),
            'blueprint_references': [
                'spec.reliability.rollback_threshold',
                'spec.reliability.rollback_on_failure'
            ]
        }

    # Restart pod
    else:
        return {
            'action': 'restart_pod',
            'reason': 'within_restart_limit',
            'pod_name': pod_status['name'],
            'restart_count': restart_count,
            'max_restart_count': max_restart_count,
            'rationale': (
                f"Pod {pod_status['name']} has restart_count ({restart_count}) < "
                f"max_restart_count ({max_restart_count}). Restarting pod."
            ),
            'blueprint_references': ['spec.reliability.max_restart_count']
        }
```

## Decision Engine Integration

The Decision Engine is called by the orchestration layer:

```python
# Initialize Decision Engine with parsed blueprint
decision_engine = DecisionEngine(parsed_blueprint)

# Collect current metrics
current_metrics = metrics_collector.collect()

# Make decision
decision = decision_engine.make_decision(current_metrics)

# Pass decision to Governance Enforcer
governance_result = governance_enforcer.check(decision)

# If allowed, pass to Execution Engine
if governance_result['classification'] == 'allowed':
    execution_result = execution_engine.execute(decision)
```

## Best Practices

1. **Always Include Rationale**: Every decision must explain why
2. **Reference Blueprint**: Cite specific blueprint sections
3. **Show Calculations**: Include metric breakdowns
4. **Consider Edge Cases**: Handle min/max limits, cooldown periods
5. **Provide Alternatives**: Suggest options when action is blocked

## See Also

- [Blueprint Parser Documentation](./BLUEPRINT_PARSER.md) - How blueprints are parsed
- [Governance Documentation](./GOVERNANCE.md) - How decisions are validated
- [Verification Documentation](./VERIFICATION_ENGINE.md) - How outcomes are verified
