# Multi-Service Management Documentation

## Overview

Multi-Service Management enables agents to manage multiple services independently, each with its own blueprint, without interference or conflicts. This document explains how agents handle multiple services simultaneously.

**Key Principle**: Each service is managed independently based on its own blueprint, with no cross-service interference.

## Architecture

### Independent Service Management

```
┌─────────────────────────────────────────────────────┐
│              Blueprint Parser                        │
│  Loads and validates multiple blueprints            │
└─────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐              ┌──────▼─────────┐
│ Frontend       │              │ Backend        │
│ Blueprint      │              │ Blueprint      │
│ (todo-frontend)│              │ (todo-backend) │
└───────┬────────┘              └──────┬─────────┘
        │                               │
┌───────▼────────┐              ┌──────▼─────────┐
│ Decision Engine│              │ Decision Engine│
│ (Frontend)     │              │ (Backend)      │
└───────┬────────┘              └──────┬─────────┘
        │                               │
┌───────▼────────┐              ┌──────▼─────────┐
│ Governance     │              │ Governance     │
│ (Frontend)     │              │ (Backend)      │
└───────┬────────┘              └──────┬─────────┘
        │                               │
┌───────▼────────┐              ┌──────▼─────────┐
│ Execution      │              │ Execution      │
│ (Frontend)     │              │ (Backend)      │
└────────────────┘              └────────────────┘
```

## Service Isolation

### Principle: No Cross-Service Interference

Each service is evaluated and managed independently:

1. **Separate Blueprints**: Each service has its own blueprint
2. **Independent Decisions**: Decisions for one service don't affect others
3. **Isolated Metrics**: Metrics collected per service
4. **Separate Cooldowns**: Each service has its own cooldown timer
5. **Independent Governance**: Governance rules applied per service

### Service Isolation Logic

```python
class MultiServiceManager:
    """
    Manage multiple services independently.
    """

    def __init__(self):
        self.services = {}  # service_name -> ServiceManager

    def add_service(self, service_name: str, blueprint_path: str) -> None:
        """
        Add service with its blueprint.

        Args:
            service_name: Name of service (e.g., "todo-frontend")
            blueprint_path: Path to service blueprint
        """
        # Parse blueprint
        blueprint = BlueprintParser().parse(blueprint_path)

        # Create independent service manager
        self.services[service_name] = ServiceManager(
            service_name=service_name,
            blueprint=blueprint,
            decision_engine=DecisionEngine(blueprint),
            governance_enforcer=GovernanceEnforcer(blueprint),
            execution_engine=ExecutionEngine(),
            verification_engine=VerificationEngine(blueprint)
        )

    def evaluate_all_services(self) -> dict:
        """
        Evaluate all services independently.

        Returns:
            Dictionary of decisions per service
        """
        decisions = {}

        for service_name, service_manager in self.services.items():
            # Collect metrics for this service
            metrics = self.collect_metrics(service_name)

            # Make decision for this service
            decision = service_manager.decision_engine.make_decision(metrics)

            # Check governance for this service
            governance_result = service_manager.governance_enforcer.classify_operation(decision)

            # Store decision
            decisions[service_name] = {
                'decision': decision,
                'governance': governance_result,
                'service_manager': service_manager
            }

        return decisions

    def execute_decisions(self, decisions: dict) -> dict:
        """
        Execute allowed decisions for each service.

        Args:
            decisions: Decisions per service

        Returns:
            Execution results per service
        """
        results = {}

        for service_name, decision_data in decisions.items():
            # Only execute if allowed
            if decision_data['governance']['classification'] == 'allowed':
                result = decision_data['service_manager'].execution_engine.execute(
                    decision_data['decision']
                )
                results[service_name] = result

        return results
```

## Independent Decision Making

### Example: Frontend and Backend Evaluated Separately

**Scenario**: Frontend needs scaling, backend is stable

**Frontend Evaluation**:
```json
{
  "service": "todo-frontend",
  "current_state": {
    "replicas": 2,
    "cpu_utilization": 0.85,
    "memory_utilization": 0.70
  },
  "decision": {
    "action": "scale_up",
    "target_replicas": 3,
    "rationale": "CPU 85% > threshold 80%"
  },
  "governance": "allowed",
  "execution": "proceed"
}
```

**Backend Evaluation**:
```json
{
  "service": "todo-backend",
  "current_state": {
    "replicas": 3,
    "cpu_utilization": 0.45,
    "memory_utilization": 0.50
  },
  "decision": {
    "action": "no_action",
    "rationale": "Utilization within acceptable range"
  },
  "governance": "n/a",
  "execution": "no_action"
}
```

**Result**: Frontend scales to 3 replicas, backend remains at 3 replicas. No interference.

## Conflict Detection

While services are managed independently, the system detects potential conflicts.

### Conflict Types

1. **Resource Conflicts**: Both services need resources, cluster capacity limited
2. **Timing Conflicts**: Multiple operations at same time
3. **Dependency Conflicts**: Backend change affects frontend

### Conflict Detection Logic

```python
def detect_conflicts(decisions: dict) -> list:
    """
    Detect potential conflicts between service decisions.

    Args:
        decisions: Decisions for all services

    Returns:
        List of detected conflicts
    """
    conflicts = []

    # Check for resource conflicts
    total_cpu_requested = 0
    total_memory_requested = 0

    for service_name, decision_data in decisions.items():
        if decision_data['decision']['action'] == 'scale_up':
            # Calculate additional resources needed
            additional_replicas = decision_data['decision']['target_replicas'] - decision_data['decision']['current_replicas']
            cpu_per_replica = decision_data['service_manager'].blueprint['resources']['cpu_request']
            memory_per_replica = decision_data['service_manager'].blueprint['resources']['memory_request']

            total_cpu_requested += additional_replicas * cpu_per_replica
            total_memory_requested += additional_replicas * memory_per_replica

    # Check if cluster has capacity
    cluster_capacity = get_cluster_capacity()

    if total_cpu_requested > cluster_capacity['available_cpu']:
        conflicts.append({
            'type': 'resource_conflict',
            'resource': 'cpu',
            'requested': total_cpu_requested,
            'available': cluster_capacity['available_cpu'],
            'resolution': 'prioritize_by_criticality'
        })

    if total_memory_requested > cluster_capacity['available_memory']:
        conflicts.append({
            'type': 'resource_conflict',
            'resource': 'memory',
            'requested': total_memory_requested,
            'available': cluster_capacity['available_memory'],
            'resolution': 'prioritize_by_criticality'
        })

    return conflicts
```

### Conflict Resolution

When conflicts detected, resolve by priority:

1. **Service Criticality**: Critical services get priority
2. **Current State**: Services in degraded state get priority
3. **Resource Efficiency**: Smaller resource requests get priority
4. **Time-Based**: First-come-first-served

**Example Resolution**:
```json
{
  "conflict": {
    "type": "resource_conflict",
    "resource": "cpu",
    "requested": "500m",
    "available": "300m"
  },
  "resolution": {
    "strategy": "prioritize_by_criticality",
    "decisions": [
      {
        "service": "todo-backend",
        "action": "execute",
        "priority": "high",
        "criticality": "critical",
        "rationale": "Backend is critical service, gets priority"
      },
      {
        "service": "todo-frontend",
        "action": "defer",
        "priority": "medium",
        "criticality": "standard",
        "rationale": "Frontend deferred until resources available"
      }
    ]
  }
}
```

## Service Priority

Services can be assigned priority levels to guide conflict resolution.

### Priority Configuration

```yaml
# blueprints/frontend/blueprint.yaml
metadata:
  name: todo-frontend
  priority: medium
  criticality: standard

# blueprints/backend/blueprint.yaml
metadata:
  name: todo-backend
  priority: high
  criticality: critical
```

### Priority Levels

| Priority | Criticality | Conflict Resolution | Example Services |
|----------|-------------|---------------------|------------------|
| Critical | Critical | Always prioritized | Database, Auth |
| High | Critical | Prioritized over medium/low | Backend API |
| Medium | Standard | Standard priority | Frontend |
| Low | Standard | Deferred if conflicts | Batch jobs |

## Shared Resources

Some resources are shared across services and require coordination.

### Shared Resource Types

1. **Cluster Capacity**: CPU, memory, disk
2. **Network Bandwidth**: Ingress/egress limits
3. **Database Connections**: Connection pool limits
4. **External APIs**: Rate limits

### Shared Resource Management

```python
class SharedResourceManager:
    """
    Manage shared resources across services.
    """

    def __init__(self):
        self.cluster_capacity = self.get_cluster_capacity()
        self.allocated_resources = {}

    def can_allocate(self, service: str, resources: dict) -> bool:
        """
        Check if resources can be allocated to service.

        Args:
            service: Service name
            resources: Resources requested (cpu, memory)

        Returns:
            True if resources available
        """
        # Calculate total allocated
        total_cpu = sum(r['cpu'] for r in self.allocated_resources.values())
        total_memory = sum(r['memory'] for r in self.allocated_resources.values())

        # Check if request fits
        if (total_cpu + resources['cpu'] <= self.cluster_capacity['cpu'] and
            total_memory + resources['memory'] <= self.cluster_capacity['memory']):
            return True

        return False

    def allocate(self, service: str, resources: dict) -> None:
        """
        Allocate resources to service.
        """
        self.allocated_resources[service] = resources

    def deallocate(self, service: str) -> None:
        """
        Deallocate resources from service.
        """
        if service in self.allocated_resources:
            del self.allocated_resources[service]
```

## Multi-Service Monitoring

Monitor all services from single dashboard.

### Monitoring Dashboard

```
Multi-Service Status
├── todo-frontend
│   ├── Replicas: 3 / 3 ready
│   ├── CPU: 60% (target: 70%)
│   ├── Memory: 50% (target: 80%)
│   ├── Latency P95: 150ms (target: 200ms)
│   └── Last Operation: scale_up (2 minutes ago)
│
├── todo-backend
│   ├── Replicas: 3 / 3 ready
│   ├── CPU: 45% (target: 70%)
│   ├── Memory: 55% (target: 80%)
│   ├── Latency P95: 100ms (target: 150ms)
│   └── Last Operation: no_action (5 minutes ago)
│
└── Cluster Resources
    ├── CPU: 8000m / 10000m (80% used)
    ├── Memory: 24Gi / 32Gi (75% used)
    └── Available for scaling: Yes
```

## Best Practices

1. **Independent Blueprints**: Each service has its own blueprint
2. **Service Isolation**: Decisions don't affect other services
3. **Conflict Detection**: Monitor for resource conflicts
4. **Priority Assignment**: Assign priorities to critical services
5. **Shared Resource Awareness**: Consider cluster capacity
6. **Independent Monitoring**: Monitor each service separately
7. **Coordinated Updates**: Update blueprints in coordination

## Troubleshooting

### Problem: Services interfering with each other

**Causes**:
- Shared resource exhaustion
- Timing conflicts
- Configuration errors

**Solutions**:
- Implement conflict detection
- Assign service priorities
- Increase cluster capacity

### Problem: One service always prioritized

**Causes**:
- Priority configuration too high
- Criticality mismatch
- Resource allocation unfair

**Solutions**:
- Review priority assignments
- Balance criticality levels
- Implement fair resource allocation

### Problem: Cluster capacity exhausted

**Causes**:
- Too many services
- Over-provisioning
- Insufficient capacity planning

**Solutions**:
- Increase cluster capacity
- Optimize resource requests
- Implement resource quotas per service

## See Also

- [Blueprint Format Documentation](./BLUEPRINT_FORMAT.md) - Service blueprint structure
- [Decision Engine Documentation](./DECISION_ENGINE.md) - Independent decision making
- [Resource Management](./RESOURCE_MANAGEMENT.md) - Shared resource handling
