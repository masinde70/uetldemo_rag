# SISUiQ Deployment Guide

This guide covers the CI/CD pipeline and deployment strategies for SISUiQ.

## Overview

SISUiQ uses GitHub Actions for continuous integration and deployment:

| Workflow | Trigger | Environment |
|----------|---------|-------------|
| `ci.yml` | Push/PR to main, develop | N/A (tests only) |
| `cd-staging.yml` | Push to main | Staging |
| `cd-prod.yml` | Push tags v* | Production |

## CI Pipeline

### Workflow: `ci.yml`

Runs on every push and pull request to `main` or `develop` branches.

**Jobs:**

1. **lint-backend** - Python linting with Ruff and mypy
2. **lint-frontend** - TypeScript/ESLint checks
3. **test-backend** - Unit tests with pytest (requires Postgres & Qdrant services)
4. **test-e2e** - Playwright end-to-end tests
5. **build** - Docker image builds (only on main branch)

### Running Locally

```bash
# Lint
make lint

# Format
make format

# Run tests
make test
make test-e2e
```

## Staging Deployment

### Workflow: `cd-staging.yml`

Auto-deploys to staging when code is pushed to `main` branch.

**Process:**

1. Runs CI checks (can be skipped via workflow dispatch)
2. Builds and pushes Docker images to GHCR with `staging` tag
3. Deploys to staging server via SSH
4. Runs database migrations
5. Executes smoke tests

### Required Secrets

| Secret | Description |
|--------|-------------|
| `STAGING_SSH_HOST` | Staging server hostname |
| `STAGING_SSH_USER` | SSH username |
| `STAGING_SSH_KEY` | SSH private key |
| `STAGING_URL` | Staging application URL |
| `OPENAI_API_KEY` | OpenAI API key for testing |

### Manual Deployment

```bash
# Trigger via GitHub Actions
gh workflow run cd-staging.yml

# Or with skip tests option
gh workflow run cd-staging.yml -f skip_tests=true
```

## Production Deployment

### Workflow: `cd-prod.yml`

Deploys to production when a release tag is pushed.

**Requirements:**

- Tag must match format: `v1.0.0` or `v1.0.0-beta`
- Requires manual approval (GitHub environment protection)
- Creates GitHub Release with changelog

**Process:**

1. Validates release tag format
2. Builds production Docker images with version tags
3. Waits for manual approval
4. Deploys to production server
5. Runs database migrations
6. Executes smoke tests
7. Creates GitHub Release

### Required Secrets

| Secret | Description |
|--------|-------------|
| `PROD_SSH_HOST` | Production server hostname |
| `PROD_SSH_USER` | SSH username |
| `PROD_SSH_KEY` | SSH private key |
| `PROD_URL` | Production application URL |
| `PROD_API_URL` | Production API URL for frontend build |

### Creating a Release

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0

# Or with annotation
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Manual Deployment

```bash
# Deploy specific tag
gh workflow run cd-prod.yml -f tag=v1.0.0
```

## Container Registry

Images are pushed to GitHub Container Registry (GHCR):

```
ghcr.io/<owner>/<repo>/backend:latest
ghcr.io/<owner>/<repo>/backend:staging
ghcr.io/<owner>/<repo>/backend:v1.0.0

ghcr.io/<owner>/<repo>/frontend:latest
ghcr.io/<owner>/<repo>/frontend:staging
ghcr.io/<owner>/<repo>/frontend:v1.0.0
```

### Pulling Images

```bash
# Authenticate
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull images
docker pull ghcr.io/<owner>/<repo>/backend:latest
docker pull ghcr.io/<owner>/<repo>/frontend:latest
```

## Server Setup

### Prerequisites

- Docker and Docker Compose installed
- Access to PostgreSQL 16+
- Access to Qdrant vector database
- SSL certificates (for production)

### Directory Structure

```
/opt/sisuiq/
├── docker-compose.yml
├── .env
├── nginx/
│   └── nginx.conf
├── data/
│   └── postgres/
└── logs/
```

### Environment Variables

Create `/opt/sisuiq/.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://sisuiq:password@postgres:5432/sisuiq
POSTGRES_PASSWORD=password

# Qdrant
QDRANT_URL=http://qdrant:6333

# OpenAI
OPENAI_API_KEY=sk-...

# App
ENVIRONMENT=production
CORS_ORIGINS=https://sisuiq.example.com
ADMIN_TOKEN=secure-admin-token

# Frontend
NEXT_PUBLIC_API_URL=/api
```

### Docker Compose

```yaml
# /opt/sisuiq/docker-compose.yml
version: "3.8"

services:
  backend:
    image: ghcr.io/<owner>/<repo>/backend:latest
    env_file: .env
    depends_on:
      - postgres
      - qdrant
    networks:
      - sisuiq

  frontend:
    image: ghcr.io/<owner>/<repo>/frontend:latest
    environment:
      - BACKEND_URL=http://backend:8000
    networks:
      - sisuiq

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - backend
      - frontend
    networks:
      - sisuiq

  postgres:
    image: postgres:16-alpine
    env_file: .env
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    networks:
      - sisuiq

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - ./data/qdrant:/qdrant/storage
    networks:
      - sisuiq

networks:
  sisuiq:
    driver: bridge
```

## Database Migrations

### Running Migrations

```bash
# Via Docker Compose
docker compose exec backend alembic upgrade head

# Or via Makefile
make migrate
```

### Creating New Migration

```bash
cd backend
alembic revision --autogenerate -m "description"
```

### Rollback

```bash
# Rollback one step
docker compose exec backend alembic downgrade -1

# Rollback to specific revision
docker compose exec backend alembic downgrade <revision_id>
```

## Monitoring

### Health Checks

- Backend: `GET /api/health`
- Version: `GET /api/version`

### Logs

```bash
# All logs
docker compose logs -f

# Specific service
docker compose logs -f backend

# With timestamps
docker compose logs -f -t
```

### Metrics

Prometheus metrics are available at `/metrics` (internal network only).

## Rollback Procedure

### Immediate Rollback

```bash
# SSH to server
ssh user@server

# Rollback to previous image
cd /opt/sisuiq
docker compose pull backend:previous-sha
docker compose up -d backend

# Or rollback database
docker compose exec backend alembic downgrade -1
```

### GitHub Actions Rollback

```bash
# Re-deploy previous tag
gh workflow run cd-prod.yml -f tag=v0.9.0
```

## Troubleshooting

### Common Issues

**Image pull fails:**
```bash
# Re-authenticate
docker logout ghcr.io
echo $GITHUB_TOKEN | docker login ghcr.io -u $USERNAME --password-stdin
```

**Database connection fails:**
```bash
# Check PostgreSQL is running
docker compose ps postgres
docker compose logs postgres

# Test connection
docker compose exec backend python -c "from backend.db import engine; print('OK')"
```

**Migration fails:**
```bash
# Check current revision
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history
```

## Security Considerations

1. **Secrets Management**: All secrets stored in GitHub Secrets
2. **Environment Protection**: Production requires manual approval
3. **SSH Keys**: Use dedicated deployment keys with minimal permissions
4. **Network Isolation**: Database and Qdrant not exposed externally
5. **SSL/TLS**: Always use HTTPS in production

## Related Documentation

- [QUICKSTART.md](../QUICKSTART.md) - Local development setup
- [Architecture](architecture/README.md) - System architecture
- [API Documentation](api/README.md) - API reference
