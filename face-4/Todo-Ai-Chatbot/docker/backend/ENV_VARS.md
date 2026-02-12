# Backend Environment Variables

## Required Environment Variables

### Database Configuration
- **DATABASE_URL**: PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`
  - Example: `postgresql://user:pass@neon.tech:5432/todo_db`
  - Description: Neon PostgreSQL database connection string

### Authentication
- **BETTER_AUTH_SECRET**: JWT signing secret
  - Description: Shared secret for JWT token signing/verification
  - Must match frontend Better Auth configuration
  - Generate: `openssl rand -hex 32`

### API Configuration
- **API_HOST**: API server host
  - Default: `0.0.0.0`
  - Description: Host to bind the FastAPI server

- **API_PORT**: API server port
  - Default: `8000`
  - Description: Port for the FastAPI server

### OpenAI Configuration (Phase III)
- **OPENAI_API_KEY**: OpenAI API key for AI chatbot
  - Description: Required for AI agent functionality
  - Get from: https://platform.openai.com/api-keys

## Optional Environment Variables

### Logging
- **LOG_LEVEL**: Application logging level
  - Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`
  - Default: `INFO`

### CORS
- **CORS_ORIGINS**: Allowed CORS origins
  - Format: Comma-separated list
  - Example: `http://localhost:3000,http://frontend:3000`
  - Default: `*` (allow all - not recommended for production)

## Kubernetes Secret Values

These sensitive values will be injected via Helm chart Secrets:

```yaml
DATABASE_URL: "postgresql://user:pass@neon.tech:5432/todo_db"
BETTER_AUTH_SECRET: "your-secret-key-here"
OPENAI_API_KEY: "sk-..."
```

## Docker Compose Values

```yaml
environment:
  - DATABASE_URL=postgresql://user:pass@neon.tech:5432/todo_db
  - BETTER_AUTH_SECRET=dev-secret-key
  - OPENAI_API_KEY=sk-...
  - API_HOST=0.0.0.0
  - API_PORT=8000
  - LOG_LEVEL=INFO
```

## Security Notes

- **Never commit secrets to version control**
- Use `.env` files for local development (add to .gitignore)
- Use Kubernetes Secrets for production deployment
- Rotate secrets regularly
- Use different secrets for different environments

## Health Check Endpoint

The backend exposes a health check endpoint at `/health` that can be used for:
- Docker health checks
- Kubernetes liveness probes
- Kubernetes readiness probes
- Load balancer health checks
