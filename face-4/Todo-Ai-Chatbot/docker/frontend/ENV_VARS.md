# Frontend Environment Variables

## Required Environment Variables

### API Configuration
- **NEXT_PUBLIC_API_URL**: Backend API base URL
  - Local development: `http://localhost:8000`
  - Docker Compose: `http://backend:8000`
  - Kubernetes: `http://todo-backend:8000`
  - Description: Base URL for backend API calls

### Build Configuration
- **NODE_ENV**: Node environment
  - Values: `development`, `production`
  - Default: `production` (in container)

## Optional Environment Variables

### Feature Flags
- **NEXT_PUBLIC_ENABLE_CHAT**: Enable chat interface
  - Values: `true`, `false`
  - Default: `true`

### Logging
- **NEXT_PUBLIC_LOG_LEVEL**: Client-side logging level
  - Values: `debug`, `info`, `warn`, `error`
  - Default: `info`

## Kubernetes ConfigMap Values

These values will be injected via Helm chart ConfigMap:

```yaml
NEXT_PUBLIC_API_URL: "http://todo-backend:8000"
NODE_ENV: "production"
```

## Docker Compose Values

```yaml
environment:
  - NEXT_PUBLIC_API_URL=http://backend:8000
  - NODE_ENV=production
```

## Notes

- All `NEXT_PUBLIC_*` variables are embedded at build time
- Changes to these variables require rebuilding the Docker image
- For Kubernetes, use Helm values.yaml to customize these settings
