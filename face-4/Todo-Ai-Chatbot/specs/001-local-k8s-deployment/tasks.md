# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/001-local-k8s-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Implementation Strategy

**MVP Scope**: User Story 1 (P1) - Developer Deploys Application Locally
- Delivers: Working Kubernetes deployment of frontend and backend to Minikube
- Validates: Core containerization and orchestration capabilities
- Enables: All other user stories depend on this foundation

**Incremental Delivery**:
1. **Sprint 1**: US1 (P1) - Core deployment capability
2. **Sprint 2**: US4 (P2) + US2 (P2) - Configuration management and scaling (parallel)
3. **Sprint 3**: US3 (P3) - Health analysis and optimization

## Dependencies Between User Stories

```
US1 (P1) ──┬──> US2 (P2) - Scaling
           ├──> US3 (P3) - Health Analysis
           └──> US4 (P2) - Configuration Management

US2, US3, US4 are independent of each other (can be done in parallel)
```

## Parallel Execution Opportunities

**Within US1**:
- Frontend containerization (T006-T010) || Backend containerization (T011-T015)
- Frontend Helm chart (T019-T025) || Backend Helm chart (T026-T032)

**After US1**:
- US2 (Scaling) || US3 (Health) || US4 (Configuration) - all independent

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment validation and project structure initialization

- [ ] T001 Verify Docker Desktop installation and version (20.10+) using `docker --version`
- [ ] T002 Verify Docker daemon is running using `docker ps`
- [ ] T003 Verify Minikube installation using `minikube version`
- [ ] T004 Start Minikube cluster with 4GB RAM and 2 CPUs using `minikube start --memory=4096 --cpus=2`
- [ ] T005 Verify kubectl can communicate with Minikube using `kubectl cluster-info`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Install Helm 3.x if not present, verify using `helm version`
- [ ] T007 Install kubectl-ai tool for AI-assisted Kubernetes operations
- [ ] T008 Install kagent tool for cluster analysis
- [ ] T009 Create project directory structure: `docker/frontend/`, `docker/backend/`, `helm/`, `k8s/`
- [ ] T010 Document environment configuration in `k8s/README.md` (tool versions, Minikube config)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Developer Deploys Application Locally (Priority: P1) 🎯 MVP

**Goal**: Deploy the Todo AI Chatbot application (frontend + backend) to Minikube using Helm charts, with both services running and accessible.

**Independent Test**: Run `helm install` commands for both charts, verify pods reach "Running" status, access frontend UI in browser, confirm frontend-backend communication works.

### Frontend Containerization

- [ ] T011 [P] [US1] Review frontend/package.json to identify production dependencies
- [ ] T012 [P] [US1] Document frontend environment variables required in docker/frontend/ENV_VARS.md
- [ ] T013 [P] [US1] Create docker/frontend/Dockerfile with multi-stage build (node:18-alpine base)
- [ ] T014 [P] [US1] Add builder stage to docker/frontend/Dockerfile (install deps, run next build)
- [ ] T015 [P] [US1] Add runner stage to docker/frontend/Dockerfile (copy build artifacts, expose port 3000, non-root user)
- [ ] T016 [P] [US1] Create docker/frontend/.dockerignore (exclude node_modules, .next, .git)
- [ ] T017 [US1] Build frontend image: `docker build -t todo-frontend:local docker/frontend`
- [ ] T018 [US1] Test frontend container locally: `docker run -p 3000:3000 todo-frontend:local`
- [ ] T019 [US1] Verify frontend image size is under 500MB using `docker images todo-frontend:local`
- [ ] T020 [US1] Document frontend health check endpoint in docker/frontend/HEALTH.md

### Backend Containerization

- [ ] T021 [P] [US1] Review backend/requirements.txt to identify production dependencies
- [ ] T022 [P] [US1] Document backend environment variables required in docker/backend/ENV_VARS.md
- [ ] T023 [P] [US1] Create docker/backend/Dockerfile with multi-stage build (python:3.11-slim base)
- [ ] T024 [P] [US1] Add builder stage to docker/backend/Dockerfile (install dependencies via pip)
- [ ] T025 [P] [US1] Add runner stage to docker/backend/Dockerfile (copy packages, expose port 8000, non-root user)
- [ ] T026 [P] [US1] Create docker/backend/.dockerignore (exclude __pycache__, .pytest_cache, .git)
- [ ] T027 [US1] Build backend image: `docker build -t todo-backend:local docker/backend`
- [ ] T028 [US1] Test backend container locally: `docker run -p 8000:8000 todo-backend:local`
- [ ] T029 [US1] Verify backend image size is under 300MB using `docker images todo-backend:local`
- [ ] T030 [US1] Document backend health check endpoint in docker/backend/HEALTH.md

### Docker Compose Integration

- [ ] T031 [US1] Create docker-compose.yml with frontend service (port 3000)
- [ ] T032 [US1] Add backend service to docker-compose.yml (port 8000)
- [ ] T033 [US1] Configure environment variables in docker-compose.yml (NEXT_PUBLIC_API_URL, DATABASE_URL)
- [ ] T034 [US1] Set up bridge network in docker-compose.yml for service communication
- [ ] T035 [US1] Test Docker Compose deployment: `docker-compose up`
- [ ] T036 [US1] Verify frontend-backend communication in Docker Compose environment
- [ ] T037 [US1] Document Docker Compose usage in docker-compose.README.md

### Minikube Image Registry Setup

- [ ] T038 [US1] Configure Docker to use Minikube's Docker daemon: `eval $(minikube docker-env)`
- [ ] T039 [US1] Rebuild frontend image in Minikube context: `docker build -t todo-frontend:local docker/frontend`
- [ ] T040 [US1] Rebuild backend image in Minikube context: `docker build -t todo-backend:local docker/backend`
- [ ] T041 [US1] Verify images in Minikube: `minikube ssh` then `docker images`
- [ ] T042 [US1] Create build script for Minikube images in k8s/build-images.sh

### Frontend Helm Chart Creation

- [ ] T043 [P] [US1] Initialize frontend Helm chart: `helm create helm/todo-frontend`
- [ ] T044 [P] [US1] Create Deployment template in helm/todo-frontend/templates/deployment.yaml
- [ ] T045 [P] [US1] Configure Deployment with image: todo-frontend:local, ImagePullPolicy: Never
- [ ] T046 [P] [US1] Add resource requests/limits to Deployment (CPU: 100m/500m, Memory: 128Mi/512Mi)
- [ ] T047 [P] [US1] Add liveness probe to Deployment (HTTP GET /api/health)
- [ ] T048 [P] [US1] Add readiness probe to Deployment (HTTP GET /api/health)
- [ ] T049 [P] [US1] Create Service template in helm/todo-frontend/templates/service.yaml (NodePort, port 3000)
- [ ] T050 [P] [US1] Create ConfigMap template in helm/todo-frontend/templates/configmap.yaml
- [ ] T051 [P] [US1] Create Secret template in helm/todo-frontend/templates/secret.yaml
- [ ] T052 [P] [US1] Parameterize all values in helm/todo-frontend/values.yaml
- [ ] T053 [P] [US1] Create helm/todo-frontend/README.md with installation instructions
- [ ] T054 [US1] Validate frontend Helm chart: `helm lint helm/todo-frontend`
- [ ] T055 [US1] Test frontend Helm template rendering: `helm template helm/todo-frontend`

### Backend Helm Chart Creation

- [ ] T056 [P] [US1] Initialize backend Helm chart: `helm create helm/todo-backend`
- [ ] T057 [P] [US1] Create Deployment template in helm/todo-backend/templates/deployment.yaml
- [ ] T058 [P] [US1] Configure Deployment with image: todo-backend:local, ImagePullPolicy: Never
- [ ] T059 [P] [US1] Add resource requests/limits to Deployment (CPU: 200m/1000m, Memory: 256Mi/1Gi)
- [ ] T060 [P] [US1] Add liveness probe to Deployment (HTTP GET /health)
- [ ] T061 [P] [US1] Add readiness probe to Deployment (HTTP GET /health)
- [ ] T062 [P] [US1] Create Service template in helm/todo-backend/templates/service.yaml (ClusterIP, port 8000)
- [ ] T063 [P] [US1] Create ConfigMap template in helm/todo-backend/templates/configmap.yaml
- [ ] T064 [P] [US1] Create Secret template in helm/todo-backend/templates/secret.yaml (DATABASE_URL, API keys)
- [ ] T065 [P] [US1] Parameterize all values in helm/todo-backend/values.yaml
- [ ] T066 [P] [US1] Create helm/todo-backend/README.md with installation instructions
- [ ] T067 [US1] Validate backend Helm chart: `helm lint helm/todo-backend`
- [ ] T068 [US1] Test backend Helm template rendering: `helm template helm/todo-backend`

### Kubernetes Deployment

- [ ] T069 [US1] Deploy backend to Minikube: `helm install todo-backend helm/todo-backend`
- [ ] T070 [US1] Wait for backend pods to reach Running status: `kubectl wait --for=condition=Ready pod -l app=todo-backend`
- [ ] T071 [US1] Verify backend service is accessible: `kubectl get svc todo-backend`
- [ ] T072 [US1] Check backend pod logs for errors: `kubectl logs -l app=todo-backend`
- [ ] T073 [US1] Deploy frontend to Minikube: `helm install todo-frontend helm/todo-frontend`
- [ ] T074 [US1] Wait for frontend pods to reach Running status: `kubectl wait --for=condition=Ready pod -l app=todo-frontend`
- [ ] T075 [US1] Get frontend NodePort: `kubectl get svc todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'`
- [ ] T076 [US1] Access frontend in browser: `http://$(minikube ip):<nodeport>`
- [ ] T077 [US1] Test frontend-backend API communication through UI
- [ ] T078 [US1] Verify health checks passing: `kubectl get pods` (check READY column)
- [ ] T079 [US1] Test pod resilience: delete a pod and verify Kubernetes recreates it
- [ ] T080 [US1] Document deployment process in k8s/DEPLOYMENT.md

**Checkpoint**: User Story 1 complete - application deployed to Minikube, fully functional

---

## Phase 4: User Story 2 - Developer Scales Application Components (Priority: P2)

**Goal**: Enable independent scaling of frontend and backend pods to test load distribution and validate stateless architecture.

**Independent Test**: Use kubectl-ai to scale frontend to 3 replicas, verify all pods running and traffic distributed. Scale backend to 2 replicas, verify requests handled by different pods.

### kubectl-ai Setup and Testing

- [ ] T081 [US2] Verify kubectl-ai installation and configuration
- [ ] T082 [US2] Test kubectl-ai manifest generation: "Create a deployment for nginx with 2 replicas"
- [ ] T083 [US2] Verify generated manifest is valid using `kubectl apply --dry-run`

### Scaling Operations

- [ ] T084 [P] [US2] Use kubectl-ai to scale frontend: "Scale todo-frontend to 3 replicas"
- [ ] T085 [P] [US2] Verify 3 frontend pods are running: `kubectl get pods -l app=todo-frontend`
- [ ] T086 [P] [US2] Test load distribution across frontend replicas (check pod logs)
- [ ] T087 [P] [US2] Use kubectl-ai to scale backend: "Scale todo-backend to 2 replicas"
- [ ] T088 [P] [US2] Verify 2 backend pods are running: `kubectl get pods -l app=todo-backend`
- [ ] T089 [P] [US2] Test requests handled by different backend pods (check pod logs)
- [ ] T090 [US2] Test kubectl-ai describe operation: "Describe the todo-backend deployment"
- [ ] T091 [US2] Test kubectl-ai restart operation: "Restart todo-frontend pods"
- [ ] T092 [US2] Verify pods are recreated after restart
- [ ] T093 [US2] Document kubectl-ai usage examples in k8s/KUBECTL_AI.md

**Checkpoint**: User Story 2 complete - scaling validated, kubectl-ai functional

---

## Phase 5: User Story 3 - Developer Analyzes Cluster Health (Priority: P3)

**Goal**: Use kagent to analyze cluster health, resource utilization, and provide optimization recommendations.

**Independent Test**: Run kagent health analysis, verify report generated within 30 seconds showing CPU/memory/disk usage. Review optimization recommendations.

### kagent Setup and Analysis

- [ ] T094 [US3] Verify kagent installation and configuration
- [ ] T095 [US3] Run kagent cluster health analysis command
- [ ] T096 [US3] Verify health report generated within 30 seconds
- [ ] T097 [US3] Review report showing CPU, memory, disk usage for all pods
- [ ] T098 [US3] Use kagent to analyze pod resource utilization
- [ ] T099 [US3] Review recommendations for resource limit adjustments
- [ ] T100 [US3] Generate load on application (multiple API requests)
- [ ] T101 [US3] Use kagent to analyze performance under load
- [ ] T102 [US3] Review bottleneck identification and optimization suggestions
- [ ] T103 [US3] Document kagent usage examples in k8s/KAGENT.md
- [ ] T104 [US3] Document how to interpret kagent reports in k8s/KAGENT.md
- [ ] T105 [US3] Document how to apply kagent recommendations in k8s/KAGENT.md

**Checkpoint**: User Story 3 complete - cluster health analysis functional

---

## Phase 6: User Story 4 - Developer Updates Application Configuration (Priority: P2)

**Goal**: Enable configuration updates (environment variables, secrets) without rebuilding container images using Helm upgrades.

**Independent Test**: Modify values.yaml, run `helm upgrade`, verify pods restart with new configuration within 1 minute without image rebuilds.

### Configuration Management Testing

- [ ] T106 [P] [US4] Modify frontend environment variable in helm/todo-frontend/values.yaml
- [ ] T107 [P] [US4] Run Helm upgrade for frontend: `helm upgrade todo-frontend helm/todo-frontend`
- [ ] T108 [P] [US4] Verify frontend pods restart with new configuration
- [ ] T109 [P] [US4] Verify upgrade completes in under 1 minute
- [ ] T110 [P] [US4] Check frontend pod environment variables: `kubectl exec <pod> -- env`
- [ ] T111 [P] [US4] Modify backend secret in helm/todo-backend/values.yaml
- [ ] T112 [P] [US4] Run Helm upgrade for backend: `helm upgrade todo-backend helm/todo-backend`
- [ ] T113 [P] [US4] Verify backend pods restart with new secrets
- [ ] T114 [P] [US4] Verify backend connects with new configuration
- [ ] T115 [US4] Test Helm rollback: `helm rollback todo-frontend`
- [ ] T116 [US4] Verify previous configuration is restored
- [ ] T117 [US4] Verify application still functions after rollback
- [ ] T118 [US4] Document configuration management workflow in k8s/CONFIG_MANAGEMENT.md

**Checkpoint**: User Story 4 complete - configuration management validated

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and final polish

### Success Criteria Verification

- [ ] T119 Verify SC-001: Clean deployment completes in under 5 minutes
- [ ] T120 Verify SC-002: Pods reach Running status within 2 minutes
- [ ] T121 Verify SC-003: Frontend UI accessible and communicates with backend
- [ ] T122 Verify SC-004: Application survives pod restarts without data loss
- [ ] T123 Verify SC-005: Frontend and backend scale independently
- [ ] T124 Verify SC-006: Helm upgrade completes in under 1 minute
- [ ] T125 Verify SC-007: kubectl-ai generates valid Kubernetes manifests
- [ ] T126 Verify SC-008: kagent provides health analysis within 30 seconds
- [ ] T127 Verify SC-009: Image sizes (frontend <500MB, backend <300MB)
- [ ] T128 Verify SC-010: Health checks pass 95%+ over 10 minutes
- [ ] T129 Document all success criteria verification results in specs/001-local-k8s-deployment/VALIDATION.md

### Documentation and Polish

- [ ] T130 [P] Create deployment quickstart guide in specs/001-local-k8s-deployment/README.md
- [ ] T131 [P] Create troubleshooting guide in k8s/TROUBLESHOOTING.md
- [ ] T132 [P] Create architecture diagram showing deployment structure
- [ ] T133 [P] Document AI DevOps tool usage best practices in k8s/AI_DEVOPS.md
- [ ] T134 [P] Review and update all Helm chart documentation
- [ ] T135 [P] Review and update all Dockerfile comments
- [ ] T136 Create Phase IV summary report in specs/001-local-k8s-deployment/SUMMARY.md
- [ ] T137 Document known limitations in specs/001-local-k8s-deployment/SUMMARY.md
- [ ] T138 Document recommendations for Phase V in specs/001-local-k8s-deployment/SUMMARY.md

---

## Task Summary

**Total Tasks**: 138
**By User Story**:
- Setup & Foundation: 10 tasks (T001-T010)
- US1 (P1) - Deploy Application: 70 tasks (T011-T080)
- US2 (P2) - Scaling: 13 tasks (T081-T093)
- US3 (P3) - Health Analysis: 12 tasks (T094-T105)
- US4 (P2) - Configuration Management: 13 tasks (T106-T118)
- Polish & Validation: 20 tasks (T119-T138)

**Parallel Opportunities**: 45 tasks marked with [P] can run in parallel

**Estimated Effort**: 3-5 days for single developer

**Critical Path**: T001-T010 (Setup) → T011-T080 (US1) → Validation

**MVP Delivery**: Complete T001-T080 for working Kubernetes deployment
