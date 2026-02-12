# Phase IV: Local Kubernetes Deployment

**Status**: Configuration Complete ✅ | Awaiting Tool Installation ⏸️
**Branch**: `001-local-k8s-deployment`
**Created**: 2026-02-10

## Quick Links

- 📋 [Specification](./spec.md) - Feature requirements and user stories
- 📐 [Implementation Plan](./plan.md) - Technical architecture and phases
- ✅ [Tasks](./tasks.md) - Detailed task breakdown (138 tasks)
- 📊 [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - What's been completed
- 🚀 [Deployment Guide](../../../k8s/README.md) - Step-by-step deployment instructions
- 🔧 [Troubleshooting](../../../k8s/TROUBLESHOOTING.md) - Common issues and solutions

## Overview

Phase IV deploys the Todo AI Chatbot (Next.js frontend + FastAPI backend) to a local Kubernetes cluster using Minikube. This phase focuses on containerization, orchestration, and AI-assisted DevOps operations.

## What's Included

### ✅ Docker Configuration
- Multi-stage Dockerfiles for frontend and backend
- Optimized for size (<500MB frontend, <300MB backend)
- Non-root users for security
- Health checks configured
- Complete documentation

### ✅ Helm Charts
- Parameterized charts for both services
- ConfigMaps for configuration
- Secrets for sensitive data
- Resource limits and health probes
- Support for scaling and upgrades

### ✅ Documentation
- Complete deployment guide
- Comprehensive troubleshooting guide
- Environment variable documentation
- Health check specifications
- Helper scripts for automation

## Current Status

**Configuration Files**: ✅ Complete (25 files created)
**Tool Installation**: ⏸️ Required (Docker, Minikube, kubectl, Helm)
**Deployment**: ⏸️ Pending tool installation

## Quick Start

### Prerequisites

Install the following tools:
- **Docker Desktop** (20.10+)
- **Minikube** (latest)
- **kubectl** (1.19+)
- **Helm** (3.x)

See [k8s/README.md](../../../k8s/README.md) for installation instructions.

### Deploy in 5 Steps

```bash
# 1. Start Minikube
minikube start --memory=4096 --cpus=2

# 2. Build images
eval $(minikube docker-env)
docker build -t todo-backend:local -f docker/backend/Dockerfile .
docker build -t todo-frontend:local -f docker/frontend/Dockerfile .

# 3. Create secrets file
cat > secrets.yaml <<EOF
secrets:
  databaseUrl: "postgresql://user:pass@neon.tech:5432/todo_db"
  betterAuthSecret: "$(openssl rand -hex 32)"
  openaiApiKey: "sk-your-key"
EOF

# 4. Deploy with Helm
helm install todo-backend ./helm/todo-backend -f secrets.yaml
helm install todo-frontend ./helm/todo-frontend

# 5. Access application
minikube service todo-frontend
```

## User Stories

### ✅ US1 (P1): Developer Deploys Application Locally
**Status**: Configuration Ready
- Dockerfiles created with multi-stage builds
- Helm charts created with proper configuration
- Documentation complete
- **Blocked by**: Tool installation

### ⏸️ US2 (P2): Developer Scales Application Components
**Status**: Pending US1 completion
- Helm charts support scaling
- kubectl-ai integration planned
- **Requires**: kubectl-ai installation

### ⏸️ US3 (P3): Developer Analyzes Cluster Health
**Status**: Pending US1 completion
- kagent integration planned
- Health monitoring configured
- **Requires**: kagent installation

### ⏸️ US4 (P2): Developer Updates Application Configuration
**Status**: Pending US1 completion
- ConfigMaps and Secrets configured
- Helm upgrade support implemented
- **Requires**: Working deployment

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Minikube Cluster                  │
│                                                       │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │  Frontend Pod    │      │  Backend Pod     │    │
│  │  (Next.js)       │─────▶│  (FastAPI)       │    │
│  │  Port: 3000      │      │  Port: 8000      │    │
│  └──────────────────┘      └──────────────────┘    │
│           │                          │               │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │  Frontend Svc    │      │  Backend Svc     │    │
│  │  (NodePort)      │      │  (ClusterIP)     │    │
│  └──────────────────┘      └──────────────────┘    │
│           │                          │               │
└───────────┼──────────────────────────┼──────────────┘
            │                          │
            ▼                          ▼
      Browser Access            Neon PostgreSQL
   (http://minikube-ip:30080)   (External)
```

## File Structure

```
specs/001-local-k8s-deployment/
├── README.md                    # This file
├── spec.md                      # Feature specification
├── plan.md                      # Implementation plan
├── tasks.md                     # Task breakdown
├── IMPLEMENTATION_SUMMARY.md    # Status summary
└── checklists/
    └── requirements.md          # Quality checklist

docker/
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── ENV_VARS.md
│   └── HEALTH.md
└── backend/
    ├── Dockerfile
    ├── .dockerignore
    ├── ENV_VARS.md
    └── HEALTH.md

helm/
├── todo-frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── README.md
│   └── templates/
└── todo-backend/
    ├── Chart.yaml
    ├── values.yaml
    ├── README.md
    └── templates/

k8s/
├── README.md                    # Deployment guide
├── TROUBLESHOOTING.md           # Troubleshooting guide
└── build-images.sh              # Helper script

docker-compose.yml               # Local testing
```

## Success Criteria

| ID | Criteria | Status |
|----|----------|--------|
| SC-001 | Deploy in <5 minutes | ⏸️ Ready to test |
| SC-002 | Pods ready in <2 minutes | ⏸️ Probes configured |
| SC-003 | UI accessible, API works | ⏸️ Services configured |
| SC-004 | Survives pod restarts | ⏸️ K8s handles automatically |
| SC-005 | Independent scaling | ⏸️ Deployments support scaling |
| SC-006 | Helm upgrade <1 minute | ⏸️ Charts support upgrades |
| SC-007 | kubectl-ai generates manifests | ⏸️ Requires kubectl-ai |
| SC-008 | kagent provides analysis | ⏸️ Requires kagent |
| SC-009 | Image sizes optimized | ✅ Multi-stage builds |
| SC-010 | Health checks pass 95%+ | ⏸️ Probes configured |

## Next Steps

1. **Install Required Tools**
   - Docker Desktop
   - Minikube
   - kubectl
   - Helm

2. **Follow Deployment Guide**
   - See [k8s/README.md](../../../k8s/README.md)
   - Use helper script: `k8s/build-images.sh`

3. **Verify Deployment**
   - Check pods: `kubectl get pods`
   - Access UI: `minikube service todo-frontend`
   - View logs: `kubectl logs -l app=todo-frontend`

4. **Proceed to Spec 2**
   - AI-assisted operations with kubectl-ai
   - Cluster analysis with kagent

## Support

- **Deployment Issues**: See [k8s/TROUBLESHOOTING.md](../../../k8s/TROUBLESHOOTING.md)
- **Helm Chart Help**: See `helm/*/README.md`
- **Docker Issues**: See `docker/*/ENV_VARS.md` and `HEALTH.md`

## Related Specifications

- **Spec 2**: AI-Assisted Kubernetes Operations (Planned)
- **Spec 3**: Advanced Monitoring and Optimization (Future)

## Version History

- **v1.0.0** (2026-02-10): Initial configuration complete
  - All Docker and Helm configuration files created
  - Complete documentation and troubleshooting guides
  - Ready for deployment once tools are installed
