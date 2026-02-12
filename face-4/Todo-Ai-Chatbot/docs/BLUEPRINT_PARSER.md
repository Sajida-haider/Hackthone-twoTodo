# Blueprint Parser Documentation

## Overview

The Blueprint Parser is the foundational agent that reads infrastructure blueprints and extracts policies for other agents to use. It validates blueprints against the schema and transforms YAML into structured data that the Decision Engine, Governance Enforcer, and other agents can consume.

**Key Responsibility**: Transform human-readable YAML blueprints into machine-readable policy objects.

## Parser Architecture

```
Blueprint YAML File
        ↓
    [Read File]
        ↓
    [Parse YAML]
        ↓
[Validate Schema]
        ↓
[Extract Policies]
        ↓
Structured Blueprint Object
```

## Parsing Steps

### Step 1: Read Blueprint File

**Input**: File path to blueprint YAML
**Output**: Raw YAML string
**Error Handling**: File not found, permission denied, invalid path

```python
def read_blueprint(file_path: str) -> str:
    """
    Read blueprint YAML file from disk.

    Args:
        file_path: Absolute path to blueprint file

    Returns:
        Raw YAML content as string

    Raises:
        FileNotFoundError: Blueprint file does not exist
        PermissionError: Cannot read blueprint file
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Blueprint not found: {file_path}")
    except PermissionError:
        raise PermissionError(f"Cannot read blueprint: {file_path}")
```

### Step 2: Parse YAML

**Input**: Raw YAML string
**Output**: Python dictionary
**Error Handling**: Invalid YAML syntax, malformed structure

```python
import yaml

def parse_yaml(yaml_content: str) -> dict:
    """
    Parse YAML content into Python dictionary.

    Args:
        yaml_content: Raw YAML string

    Returns:
        Parsed YAML as dictionary

    Raises:
        yaml.YAMLError: Invalid YAML syntax
    """
    try:
        return yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax: {e}")
```

### Step 3: Validate Schema

**Input**: Parsed YAML dictionary
**Output**: Validated blueprint dictionary
**Error Handling**: Missing required fields, invalid types, constraint violations

```python
import jsonschema

def validate_blueprint(blueprint: dict, schema: dict) -> dict:
    """
    Validate blueprint against JSON Schema.

    Args:
        blueprint: Parsed blueprint dictionary
        schema: JSON Schema definition

    Returns:
        Validated blueprint dictionary

    Raises:
        jsonschema.ValidationError: Blueprint does not match schema
    """
    try:
        jsonschema.validate(instance=blueprint, schema=schema)
        return blueprint
    except jsonschema.ValidationError as e:
        raise ValueError(f"Blueprint validation failed: {e.message}")
```

**Validation Checks**:
1. **Required fields present**: apiVersion, kind, metadata, spec, governance
2. **Correct types**: strings are strings, integers are integers, etc.
3. **Pattern matching**: CPU format (e.g., "50m"), memory format (e.g., "128Mi")
4. **Value constraints**: min_replicas ≤ max_replicas, percentages 0-100%
5. **Enum validation**: strategy must be "RollingUpdate" or "Recreate"

**Common Validation Errors**:

| Error | Cause | Solution |
|-------|-------|----------|
| Missing required field | Field not present in YAML | Add the field |
| Invalid type | String where integer expected | Fix type |
| Pattern mismatch | "50" instead of "50m" for CPU | Add unit suffix |
| Constraint violation | min_replicas > max_replicas | Fix values |
| Unknown enum value | strategy: "BlueGreen" | Use valid value |

### Step 4: Extract Policies

**Input**: Validated blueprint dictionary
**Output**: Structured policy objects
**Error Handling**: Missing nested fields, type conversion errors

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ResourcePolicy:
    cpu_request: str
    cpu_limit: str
    cpu_target_utilization: float
    memory_request: str
    memory_limit: str
    memory_target_utilization: float

@dataclass
class ScalingPolicy:
    min_replicas: int
    max_replicas: int
    scale_up_threshold: float
    scale_down_threshold: float
    cooldown_period: int  # seconds

@dataclass
class GovernancePolicy:
    allowed_operations: List[str]
    requires_approval: List[str]
    forbidden_operations: List[str]

def extract_policies(blueprint: dict) -> dict:
    """
    Extract policy objects from validated blueprint.

    Args:
        blueprint: Validated blueprint dictionary

    Returns:
        Dictionary of policy objects
    """
    return {
        'metadata': {
            'name': blueprint['metadata']['name'],
            'version': blueprint['metadata']['version'],
            'owner': blueprint['metadata']['owner']
        },
        'resources': ResourcePolicy(
            cpu_request=blueprint['spec']['resources']['cpu']['request'],
            cpu_limit=blueprint['spec']['resources']['cpu']['limit'],
            cpu_target_utilization=parse_percentage(
                blueprint['spec']['resources']['cpu']['target_utilization']
            ),
            memory_request=blueprint['spec']['resources']['memory']['request'],
            memory_limit=blueprint['spec']['resources']['memory']['limit'],
            memory_target_utilization=parse_percentage(
                blueprint['spec']['resources']['memory']['target_utilization']
            )
        ),
        'scaling': ScalingPolicy(
            min_replicas=blueprint['spec']['scaling']['min_replicas'],
            max_replicas=blueprint['spec']['scaling']['max_replicas'],
            scale_up_threshold=parse_percentage(
                blueprint['spec']['scaling']['scale_up_threshold']
            ),
            scale_down_threshold=parse_percentage(
                blueprint['spec']['scaling']['scale_down_threshold']
            ),
            cooldown_period=parse_duration(
                blueprint['spec']['scaling']['cooldown_period']
            )
        ),
        'governance': GovernancePolicy(
            allowed_operations=blueprint['governance']['agent_authority']['allowed_operations'],
            requires_approval=blueprint['governance']['agent_authority']['requires_approval'],
            forbidden_operations=blueprint['governance']['agent_authority']['forbidden_operations']
        )
    }
```

**Helper Functions**:

```python
def parse_percentage(value: str) -> float:
    """Convert percentage string to float (e.g., "80%" -> 0.80)"""
    return float(value.rstrip('%')) / 100.0

def parse_duration(value: str) -> int:
    """Convert duration string to seconds (e.g., "60s" -> 60, "1m" -> 60)"""
    if value.endswith('s'):
        return int(value[:-1])
    elif value.endswith('m'):
        return int(value[:-1]) * 60
    elif value.endswith('h'):
        return int(value[:-1]) * 3600
    else:
        raise ValueError(f"Invalid duration format: {value}")

def parse_resource(value: str) -> int:
    """Convert resource string to bytes (e.g., "128Mi" -> 134217728)"""
    if value.endswith('Mi'):
        return int(value[:-2]) * 1024 * 1024
    elif value.endswith('Gi'):
        return int(value[:-2]) * 1024 * 1024 * 1024
    elif value.endswith('m'):  # millicores
        return int(value[:-1])
    else:
        return int(value)
```

## Complete Parser Flow

```python
class BlueprintParser:
    """
    Blueprint Parser Agent

    Reads, validates, and extracts policies from infrastructure blueprints.
    """

    def __init__(self, schema_path: str):
        """Initialize parser with JSON Schema."""
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)

    def parse(self, blueprint_path: str) -> dict:
        """
        Parse blueprint file and extract policies.

        Args:
            blueprint_path: Path to blueprint YAML file

        Returns:
            Dictionary of extracted policies

        Raises:
            FileNotFoundError: Blueprint file not found
            ValueError: Invalid blueprint format or validation failure
        """
        # Step 1: Read file
        yaml_content = self.read_blueprint(blueprint_path)

        # Step 2: Parse YAML
        blueprint = self.parse_yaml(yaml_content)

        # Step 3: Validate schema
        validated_blueprint = self.validate_blueprint(blueprint, self.schema)

        # Step 4: Extract policies
        policies = self.extract_policies(validated_blueprint)

        return policies
```

## Parser Output Format

The parser produces a structured dictionary that other agents consume:

```json
{
  "metadata": {
    "name": "todo-frontend",
    "version": "1.0.0",
    "owner": "devops-team"
  },
  "resources": {
    "cpu_request": "50m",
    "cpu_limit": "200m",
    "cpu_target_utilization": 0.70,
    "memory_request": "128Mi",
    "memory_limit": "512Mi",
    "memory_target_utilization": 0.80
  },
  "performance": {
    "latency_p95": 200,
    "throughput_min": 100,
    "availability": 0.999
  },
  "scaling": {
    "min_replicas": 1,
    "max_replicas": 5,
    "scale_up_threshold": 0.80,
    "scale_down_threshold": 0.30,
    "cooldown_period": 60
  },
  "reliability": {
    "max_restart_count": 3,
    "rollback_threshold": 2,
    "rollback_on_failure": true
  },
  "governance": {
    "allowed_operations": [
      "scale_within_limits",
      "restart_failed_pods",
      "adjust_resources_within_10_percent"
    ],
    "requires_approval": [
      "scale_beyond_limits",
      "change_resource_limits_beyond_10_percent"
    ],
    "forbidden_operations": [
      "delete_deployment",
      "delete_service",
      "modify_secrets"
    ]
  }
}
```

## Error Handling

The parser provides clear, actionable error messages:

### Example 1: Missing Required Field

**Blueprint**:
```yaml
apiVersion: infra.spec-driven.io/v1
kind: InfrastructureBlueprint
metadata:
  name: todo-frontend
  # version is missing
```

**Error**:
```
Blueprint validation failed: 'version' is a required property in metadata
Location: metadata.version
Fix: Add version field (e.g., version: "1.0.0")
```

### Example 2: Invalid Format

**Blueprint**:
```yaml
spec:
  resources:
    cpu:
      request: 50  # Missing 'm' suffix
```

**Error**:
```
Blueprint validation failed: '50' does not match pattern '^\\d+m?$'
Location: spec.resources.cpu.request
Fix: Add unit suffix (e.g., "50m" for millicores)
```

### Example 3: Constraint Violation

**Blueprint**:
```yaml
spec:
  scaling:
    min_replicas: 5
    max_replicas: 3  # min > max
```

**Error**:
```
Blueprint validation failed: min_replicas (5) must be ≤ max_replicas (3)
Location: spec.scaling
Fix: Ensure min_replicas ≤ max_replicas
```

## Parser Performance

**Typical Performance**:
- Read file: <1ms
- Parse YAML: <5ms
- Validate schema: <10ms
- Extract policies: <5ms
- **Total: <25ms**

**Optimization**:
- Cache parsed blueprints (invalidate on file change)
- Pre-load JSON Schema at startup
- Use fast YAML parser (PyYAML with C extensions)

## Parser Testing

**Test Cases**:

1. **Valid Blueprint**: Parser succeeds, returns policies
2. **Missing Required Field**: Parser fails with clear error
3. **Invalid YAML Syntax**: Parser fails with syntax error
4. **Invalid Format**: Parser fails with pattern mismatch error
5. **Constraint Violation**: Parser fails with constraint error
6. **File Not Found**: Parser fails with file not found error

**Example Test**:
```python
def test_parse_valid_blueprint():
    parser = BlueprintParser('blueprints/schema.json')
    policies = parser.parse('blueprints/frontend/blueprint.yaml')

    assert policies['metadata']['name'] == 'todo-frontend'
    assert policies['scaling']['min_replicas'] == 1
    assert policies['scaling']['max_replicas'] == 5
    assert 'scale_within_limits' in policies['governance']['allowed_operations']
```

## Integration with Other Agents

The parser output is consumed by:

1. **Decision Engine**: Uses scaling policies to make scaling decisions
2. **Governance Enforcer**: Uses governance policies to classify operations
3. **Verification Engine**: Uses performance targets to verify outcomes
4. **Audit Logger**: Uses metadata for logging blueprint version

**Example Integration**:
```python
# Parse blueprint
parser = BlueprintParser('blueprints/schema.json')
policies = parser.parse('blueprints/frontend/blueprint.yaml')

# Pass to Decision Engine
decision_engine = DecisionEngine(policies)
decision = decision_engine.make_decision(current_metrics)

# Pass to Governance Enforcer
governance = GovernanceEnforcer(policies['governance'])
classification = governance.classify_operation(decision['operation'])
```

## Blueprint Change Detection

The parser can watch for blueprint changes and trigger re-parsing:

```python
import time
import os

class BlueprintWatcher:
    """Watch blueprint file for changes and re-parse."""

    def __init__(self, blueprint_path: str, parser: BlueprintParser):
        self.blueprint_path = blueprint_path
        self.parser = parser
        self.last_modified = os.path.getmtime(blueprint_path)
        self.policies = parser.parse(blueprint_path)

    def check_for_changes(self) -> bool:
        """Check if blueprint has been modified."""
        current_modified = os.path.getmtime(self.blueprint_path)
        if current_modified > self.last_modified:
            self.last_modified = current_modified
            self.policies = self.parser.parse(self.blueprint_path)
            return True
        return False
```

## Best Practices

1. **Validate Early**: Parse and validate blueprints before agents start
2. **Cache Parsed Blueprints**: Avoid re-parsing on every decision
3. **Provide Clear Errors**: Help users fix blueprint issues quickly
4. **Log Parsing Events**: Track when blueprints are parsed and validated
5. **Version Tracking**: Always include blueprint version in parser output

## Troubleshooting

### Problem: Parser fails with "Invalid YAML syntax"

**Cause**: YAML indentation or syntax error
**Solution**: Use YAML linter to find syntax errors

### Problem: Parser fails with "Pattern mismatch"

**Cause**: Value doesn't match expected format (e.g., "50" instead of "50m")
**Solution**: Check blueprint format documentation, add correct suffix

### Problem: Parser succeeds but agents make wrong decisions

**Cause**: Blueprint values are incorrect (not a parser issue)
**Solution**: Review blueprint values, ensure they match intended policies

## See Also

- [Blueprint Format Documentation](./BLUEPRINT_FORMAT.md) - Blueprint structure and syntax
- [Decision Engine Documentation](./DECISION_ENGINE.md) - How decisions are made from policies
- [Governance Documentation](./GOVERNANCE.md) - How governance rules are enforced
