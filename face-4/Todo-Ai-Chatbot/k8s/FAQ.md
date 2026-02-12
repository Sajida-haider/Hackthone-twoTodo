# AI DevOps FAQ

Frequently asked questions about using kubectl-ai and kagent for managing the Todo AI Chatbot deployment.

## Table of Contents

1. [General Questions](#general-questions)
2. [kubectl-ai Questions](#kubectl-ai-questions)
3. [kagent Questions](#kagent-questions)
4. [Installation and Setup](#installation-and-setup)
5. [Troubleshooting](#troubleshooting)
6. [Performance and Optimization](#performance-and-optimization)
7. [Security and Safety](#security-and-safety)
8. [Integration and Workflows](#integration-and-workflows)

---

## General Questions

### Q: What are kubectl-ai and kagent?

**A**: kubectl-ai is a natural language interface for Kubernetes operations. It translates conversational queries into kubectl commands. kagent is a cluster health analysis tool that provides AI-powered recommendations for optimization and troubleshooting.

### Q: Do I need both tools?

**A**: It depends on your use case:
- **kubectl-ai only**: If you just need to perform operations (view, scale, debug)
- **kagent only**: If you only need health monitoring and recommendations
- **Both**: Recommended for complete AI-assisted DevOps workflow

### Q: Which tool should I learn first?

**A**: Start with kubectl-ai. It's more immediately useful for daily operations and has a gentler learning curve. Add kagent once you're comfortable with basic operations and want deeper insights.

### Q: Are these tools safe to use in production?

**A**: Yes, with proper precautions:
- kubectl-ai shows command previews before execution
- kagent is read-only (doesn't execute changes)
- Always review generated commands
- Test in non-production first
- Follow the safety guidelines in AI_DEVOPS.md

### Q: Do these tools replace kubectl?

**A**: No, they complement kubectl:
- Use kubectl-ai for complex or unfamiliar operations
- Use regular kubectl for simple commands you know well
- Use kagent for analysis that would require multiple kubectl commands

### Q: How much faster are AI tools compared to manual operations?

**A**: Typically 50-70% faster for:
- Complex queries requiring multiple kubectl commands
- Debugging workflows
- Resource analysis
- Operations you're unfamiliar with

For simple operations you know well, regular kubectl may be faster.

---

## kubectl-ai Questions

### Q: How does kubectl-ai understand my queries?

**A**: kubectl-ai uses natural language processing to:
1. Parse your query for intent (view, scale, debug, etc.)
2. Identify resources (pods, deployments, services)
3. Extract parameters (replica counts, time ranges, filters)
4. Generate the appropriate kubectl command
5. Show you the command for review

### Q: What if kubectl-ai generates the wrong command?

**A**: You have several options:
1. **Don't execute**: Press 'n' to cancel
2. **Edit**: Some versions allow editing before execution
3. **Rephrase**: Try asking in a different way
4. **Manual**: Use regular kubectl instead

Always review the generated command before confirming.

### Q: Can kubectl-ai handle complex multi-step operations?

**A**: kubectl-ai works best for single operations. For multi-step workflows:
- Break into individual kubectl-ai commands
- Use shell scripts for complex automation
- Combine kubectl-ai with kagent for analysis + action workflows

### Q: Does kubectl-ai work with all Kubernetes resources?

**A**: kubectl-ai supports most common resources:
- ✅ Pods, Deployments, Services, ConfigMaps, Secrets
- ✅ ReplicaSets, StatefulSets, DaemonSets
- ✅ Ingress, PersistentVolumes, PersistentVolumeClaims
- ⚠️ Custom Resource Definitions (CRDs) - may have limited support

### Q: Can I use kubectl-ai with multiple clusters?

**A**: Yes, kubectl-ai uses your current kubectl context:
```bash
# Switch context
kubectl config use-context minikube

# Now kubectl-ai operates on minikube
kubectl-ai "show me all pods"

# Switch to another cluster
kubectl config use-context production

# Now kubectl-ai operates on production
kubectl-ai "show me all pods"
```

### Q: How do I make kubectl-ai queries more accurate?

**A**: Follow these tips:
1. **Be specific**: Include app names (todo-frontend, todo-backend)
2. **Use full names**: "deployment" instead of "deploy"
3. **Include context**: "show me logs for the backend pod" vs "show logs"
4. **Specify quantities**: "last 50 lines" instead of "recent logs"
5. **Use clear verbs**: "scale", "show", "describe", "debug"

### Q: Can kubectl-ai create new resources?

**A**: kubectl-ai can generate commands to create resources, but it's not recommended for:
- Complex resource definitions (use YAML files instead)
- Production deployments (use Helm or GitOps)
- Resources requiring multiple fields

Best for: viewing, scaling, debugging, log analysis.

### Q: Does kubectl-ai support watch mode?

**A**: Yes, you can ask:
```bash
kubectl-ai "watch pod status"
kubectl-ai "monitor frontend deployment"
```

Press Ctrl+C to stop watching.

### Q: Can I save kubectl-ai generated commands?

**A**: Yes, several ways:
```bash
# Save to file
kubectl-ai "show me all pods" | tee command.log

# View command without executing
kubectl-ai "show me all pods"
# Copy the generated command before pressing 'n'

# Shell history
history | grep kubectl-ai
```

---

## kagent Questions

### Q: How does kagent analyze my cluster?

**A**: kagent:
1. Collects metrics from metrics-server
2. Analyzes resource usage patterns
3. Correlates data across pods, nodes, and services
4. Identifies bottlenecks and inefficiencies
5. Generates AI-powered recommendations

### Q: How long does kagent analysis take?

**A**: Typical times:
- Basic health check: 10-30 seconds
- Resource analysis: 30-60 seconds
- Bottleneck detection: 30-60 seconds
- Trend analysis (24h): 60-90 seconds
- Comprehensive report: 2-3 minutes

### Q: Why are kagent recommendations different each time?

**A**: kagent analyzes current state, which changes over time:
- Resource usage fluctuates
- Pod states change
- Traffic patterns vary
- Cluster conditions evolve

Recommendations reflect the current situation.

### Q: Should I implement all kagent recommendations?

**A**: No, use judgment:
1. **Review each recommendation**: Understand the impact
2. **Prioritize by severity**: HIGH → MEDIUM → LOW
3. **Consider your goals**: Cost vs performance vs reliability
4. **Test first**: Implement in non-production
5. **Measure impact**: Verify improvements

### Q: Can kagent automatically implement recommendations?

**A**: No, kagent is read-only by design. This is a safety feature:
- You review recommendations
- You decide what to implement
- You execute changes (manually or with kubectl-ai)
- kagent verifies the results

### Q: How accurate are kagent's bottleneck detections?

**A**: Generally >90% accurate for:
- CPU bottlenecks
- Memory pressure
- Disk space issues
- Network saturation

Less accurate for:
- Application-level issues
- External dependencies (databases, APIs)
- Intermittent problems

### Q: Does kagent work without metrics-server?

**A**: No, kagent requires metrics-server for:
- CPU and memory metrics
- Resource usage data
- Trend analysis

Enable with: `minikube addons enable metrics-server`

### Q: Can kagent predict future resource needs?

**A**: kagent provides trend analysis that helps with capacity planning:
```bash
kagent analyze trends --duration 7d
```

This shows patterns but doesn't make explicit predictions. Use the trends to inform your scaling decisions.

### Q: How often should I run kagent health checks?

**A**: Recommended frequency:
- **Daily**: Basic health check
- **Weekly**: Detailed analysis + recommendations
- **Monthly**: Comprehensive trend analysis
- **On-demand**: When issues occur or before major changes

### Q: Can kagent analyze specific pods only?

**A**: Yes, use filters:
```bash
kagent health --deployment todo-frontend
kagent analyze resources --pod <pod-name>
kagent health --namespace default
```

---

## Installation and Setup

### Q: Where can I download kubectl-ai and kagent?

**A**: Installation methods vary by tool. Check:
- Project GitHub repositories
- Package managers (brew, apt, yum, choco)
- Binary releases
- See `k8s/scripts/install-kubectl-ai.sh` and `k8s/scripts/install-kagent.sh` for templates

### Q: Do I need special permissions to use these tools?

**A**: You need the same permissions as kubectl:
```bash
# Check permissions
kubectl auth can-i get pods
kubectl auth can-i scale deployments
kubectl auth can-i get metrics
```

If these return "yes", you can use kubectl-ai and kagent.

### Q: Can I use these tools on Windows?

**A**: Yes, both tools support:
- Windows (native binaries or WSL)
- macOS
- Linux

Installation methods vary by platform.

### Q: Do I need to configure API keys?

**A**: Depends on the tool implementation:
- Some versions are fully local (no API keys needed)
- Some use cloud AI services (may require API keys)
- Check tool documentation for your specific version

### Q: How do I update kubectl-ai and kagent?

**A**: Update methods:
```bash
# Homebrew
brew upgrade kubectl-ai
brew upgrade kagent

# Manual
# Download new binary and replace old one

# Package manager
sudo apt-get update && sudo apt-get upgrade kubectl-ai kagent
```

### Q: Can I use these tools with managed Kubernetes (EKS, GKE, AKS)?

**A**: Yes, as long as:
- You have kubectl access
- metrics-server is enabled
- You have appropriate RBAC permissions

The tools work with any Kubernetes cluster.

---

## Troubleshooting

### Q: kubectl-ai says "command not found"

**A**: Check installation:
```bash
# Verify installation
which kubectl-ai

# Check PATH
echo $PATH

# Reinstall if needed
# See k8s/scripts/install-kubectl-ai.sh
```

### Q: kagent shows "no metrics available"

**A**: Enable metrics-server:
```bash
# For Minikube
minikube addons enable metrics-server

# Wait for metrics to be collected
sleep 60

# Verify
kubectl top nodes
kubectl top pods

# Try kagent again
kagent health
```

### Q: kubectl-ai generates incorrect commands

**A**: Improve your query:
```bash
# Too vague
kubectl-ai "show pods"

# Better
kubectl-ai "show me all pods for todo-frontend"

# Even better
kubectl-ai "show me all pods for todo-frontend with their status"
```

### Q: kagent reports are empty or incomplete

**A**: Common causes:
1. **Metrics not ready**: Wait 60 seconds after enabling metrics-server
2. **No pods running**: Deploy your application first
3. **Wrong context**: Check `kubectl config current-context`
4. **Permissions**: Verify `kubectl auth can-i get metrics`

### Q: kubectl-ai is very slow

**A**: Possible causes:
1. **Large cluster**: Many resources to query
2. **Network latency**: Slow connection to cluster
3. **Complex query**: Simplify your request
4. **Tool version**: Update to latest version

### Q: kagent recommendations seem wrong

**A**: Verify the analysis:
1. **Check metrics**: `kubectl top pods` - are they accurate?
2. **Review context**: Is this normal load or a spike?
3. **Consider timing**: Run during representative load
4. **Compare trends**: Use `kagent analyze trends --duration 24h`

### Q: "Permission denied" errors

**A**: Check RBAC permissions:
```bash
# Check what you can do
kubectl auth can-i --list

# Common required permissions
kubectl auth can-i get pods
kubectl auth can-i get deployments
kubectl auth can-i scale deployments
kubectl auth can-i get metrics

# Contact cluster admin if permissions are missing
```

### Q: kubectl-ai won't execute commands

**A**: Check preview mode:
```bash
# Check if preview mode is enabled
kubectl-ai config get preview-mode

# If true, commands won't auto-execute
# You must confirm each command

# This is a safety feature - keep it enabled
```

---

## Performance and Optimization

### Q: How can I make kubectl-ai faster?

**A**: Optimization tips:
1. **Be specific**: Narrow queries are faster
2. **Limit output**: Use `--tail=50` for logs
3. **Use filters**: Filter by namespace, labels
4. **Cache context**: Stay in one namespace
5. **Update tool**: Latest versions are optimized

### Q: How can I make kagent analysis faster?

**A**: Optimization tips:
1. **Shorter durations**: Use `--duration 1h` instead of `7d`
2. **Specific targets**: Analyze one deployment instead of all
3. **Off-peak hours**: Run detailed analysis when cluster is idle
4. **Cache reports**: Save and reuse instead of re-running
5. **Parallel analysis**: Run multiple analyses in parallel

### Q: Can I run kagent continuously?

**A**: Yes, but consider:
```bash
# Continuous monitoring (every 5 minutes)
while true; do
  kagent health --alert-threshold cpu=80,memory=80
  sleep 300
done

# Better: Use Kubernetes monitoring tools for continuous monitoring
# Use kagent for periodic deep analysis
```

### Q: How much overhead do these tools add?

**A**: Minimal overhead:
- **kubectl-ai**: No cluster overhead (runs locally)
- **kagent**: Reads metrics (same as `kubectl top`)
- **metrics-server**: ~50MB memory, 50m CPU

Total impact: <1% of cluster resources.

### Q: Can I run multiple kagent analyses in parallel?

**A**: Yes, for different targets:
```bash
# Parallel analysis
kagent analyze cpu > cpu.txt &
kagent analyze memory > memory.txt &
kagent analyze disk > disk.txt &
wait

# Review all reports
cat cpu.txt memory.txt disk.txt
```

---

## Security and Safety

### Q: Can kubectl-ai accidentally delete resources?

**A**: Only if you confirm:
1. kubectl-ai shows command preview
2. You must explicitly confirm with 'y'
3. Review carefully before confirming
4. Never auto-confirm destructive operations

### Q: Does kagent have access to secrets?

**A**: kagent reads metrics and resource definitions, but:
- Secret values are not exposed in metrics
- kagent doesn't decode secret data
- Reports show secret names, not contents

### Q: Can I restrict what kubectl-ai can do?

**A**: Yes, through Kubernetes RBAC:
```bash
# Limit to read-only operations
# Remove permissions for: delete, create, update

# kubectl-ai will only be able to view resources
```

### Q: Are AI tool queries logged?

**A**: Depends on your setup:
- kubectl-ai queries: Check shell history
- Generated kubectl commands: Logged by Kubernetes audit logs
- kagent analysis: Not logged by default

Enable logging for compliance:
```bash
kubectl-ai "..." | tee -a ai-ops.log
```

### Q: Can I use these tools in air-gapped environments?

**A**: Depends on tool implementation:
- **Local AI models**: Yes, fully offline
- **Cloud AI services**: No, requires internet
- Check your specific tool version

### Q: What data do these tools send externally?

**A**: Varies by implementation:
- **Fully local**: No external data transmission
- **Cloud-based**: May send queries to AI service
- Check tool documentation and privacy policy

---

## Integration and Workflows

### Q: Can I use kubectl-ai in scripts?

**A**: Yes, but with caution:
```bash
# Non-interactive mode (if supported)
kubectl-ai --yes "scale todo-frontend to 3 replicas"

# Better: Use generated commands in scripts
# 1. Use kubectl-ai to generate command
# 2. Review and test
# 3. Put tested kubectl command in script
```

### Q: Can I integrate kagent with monitoring tools?

**A**: Yes, export reports:
```bash
# JSON format for parsing
kagent health --output json > health.json

# Send to monitoring system
curl -X POST monitoring-system/api/reports \
  -H "Content-Type: application/json" \
  -d @health.json
```

### Q: How do kubectl-ai and kagent work together?

**A**: Common workflow:
1. **kagent**: Analyze and identify issues
2. **kubectl-ai**: Execute fixes
3. **kagent**: Verify improvements

See AI_DEVOPS.md for integration patterns.

### Q: Can I use these tools with CI/CD?

**A**: Limited use cases:
- **kagent**: Yes, for health checks in pipelines
- **kubectl-ai**: Not recommended (requires human review)

Better: Use kubectl directly in CI/CD.

### Q: Can I create custom commands or aliases?

**A**: Yes, create shell aliases:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias k-pods='kubectl-ai "show me all pods"'
alias k-health='kagent health'
alias k-analyze='kagent analyze resources'

# Use
k-pods
k-health
```

### Q: How do I share kagent reports with my team?

**A**: Export and share:
```bash
# Generate report
kagent health --detailed > health-report.txt

# Share via:
# - Email attachment
# - Slack/Teams
# - Shared drive
# - Git repository (history/reports/)
```

---

## Advanced Questions

### Q: Can I extend kubectl-ai with custom commands?

**A**: Depends on tool implementation. Some versions support:
- Custom command templates
- Plugin systems
- Configuration files

Check tool documentation.

### Q: Can kagent analyze historical data?

**A**: kagent analyzes current metrics and recent trends:
```bash
# Last 24 hours
kagent analyze trends --duration 24h

# Last 7 days
kagent analyze trends --duration 7d
```

For longer history, use dedicated monitoring tools (Prometheus, Grafana).

### Q: Can I use kubectl-ai for disaster recovery?

**A**: Not recommended. For DR:
- Use tested scripts
- Use GitOps (ArgoCD, Flux)
- Use Helm rollback
- Don't rely on AI tools in emergencies

### Q: How do I contribute to kubectl-ai or kagent?

**A**: Check project repositories:
- Report issues
- Submit pull requests
- Improve documentation
- Share usage examples

---

## Getting Help

### Q: Where can I find more examples?

**A**: Check documentation:
- `k8s/KUBECTL_AI_EXAMPLES.md` - kubectl-ai examples
- `k8s/KAGENT_GUIDE.md` - kagent guide
- `k8s/AI_DEVOPS.md` - Best practices
- `k8s/QUICK_REFERENCE.md` - Quick reference

### Q: How do I report bugs?

**A**: Report to tool maintainers:
1. Check if issue is already reported
2. Provide reproduction steps
3. Include tool version
4. Include error messages
5. Include cluster information

### Q: Where can I ask questions?

**A**: Resources:
- Tool GitHub issues
- Kubernetes Slack channels
- Stack Overflow (tag: kubernetes, kubectl-ai, kagent)
- Project documentation

### Q: How do I request new features?

**A**: Submit feature requests:
1. Check if feature already exists
2. Describe use case clearly
3. Explain why it's needed
4. Provide examples
5. Submit to project repository

---

## Quick Troubleshooting Guide

| Problem | Quick Fix |
|---------|-----------|
| Command not found | Check PATH: `which kubectl-ai` |
| No metrics | Enable metrics-server: `minikube addons enable metrics-server` |
| Wrong context | Switch context: `kubectl config use-context minikube` |
| Permission denied | Check permissions: `kubectl auth can-i get pods` |
| Slow performance | Be more specific in queries |
| Incorrect commands | Rephrase query with more details |
| Empty reports | Wait 60s for metrics, verify pods are running |
| Stale data | Wait for metrics refresh (30-60s) |

---

## See Also

- [kubectl-ai Examples](./KUBECTL_AI_EXAMPLES.md) - Detailed usage examples
- [kagent Guide](./KAGENT_GUIDE.md) - Comprehensive guide
- [AI DevOps Best Practices](./AI_DEVOPS.md) - Best practices and patterns
- [Quick Reference](./QUICK_REFERENCE.md) - Quick reference cards
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions
