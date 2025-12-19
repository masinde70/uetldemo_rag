# SISUiQ Security Notes

## DEMO-GRADE ONLY DISCLAIMER

This application is currently configured for **demonstration and development purposes only**.

**DO NOT deploy this to production without addressing the security concerns below.**

The current implementation prioritizes rapid prototyping and ease of setup over security hardening. Several shortcuts have been taken that would be unacceptable in a production environment handling real UETCL/ERA data.

---

## Critical Issues to Fix Before Production

### 1. Authentication & Authorization

**Current State:**
- Admin dashboard uses a static token (`ADMIN_TOKEN`) passed via header
- No user authentication system
- No session management with proper expiry
- No role-based access control (RBAC)

**Required Changes:**
```python
# backend/auth.py - Implement proper auth
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Use bcrypt for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Must be cryptographically random
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Verify user exists in database
    return user
```

**Production Checklist:**
- [ ] Implement OAuth2/OIDC with proper IdP (Azure AD, Okta, etc.)
- [ ] Add JWT with short expiry and refresh token rotation
- [ ] Implement RBAC with roles: admin, analyst, viewer
- [ ] Add audit logging for all authentication events
- [ ] Implement account lockout after failed attempts
- [ ] Add MFA for admin accounts

---

### 2. Environment Variables & Secrets

**Current State:**
- Secrets in `.env` files (plain text)
- Default demo values hardcoded as fallbacks
- Database credentials in environment variables

**Required Changes:**

```yaml
# docker-compose.prod.yml
services:
  backend:
    secrets:
      - db_password
      - jwt_secret
      - openai_api_key
      - admin_token
    environment:
      - DATABASE_URL_FILE=/run/secrets/db_password

secrets:
  db_password:
    external: true  # Use Docker Swarm secrets or K8s secrets
  jwt_secret:
    external: true
```

**Production Checklist:**
- [ ] Use a secrets manager (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
- [ ] Remove all default fallback values from code
- [ ] Rotate secrets regularly (automated rotation preferred)
- [ ] Never log secrets or include in error messages
- [ ] Use separate secrets for each environment

---

### 3. Database Security

**Current State:**
- PostgreSQL with default configuration
- Connection string with embedded credentials
- No connection pooling limits
- No SSL/TLS for database connections

**Required Changes:**

```python
# backend/db.py - Production database configuration
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require",  # Force SSL
        "ssl_context": ssl_context,  # Custom CA cert
    }
)
```

```ini
# postgresql.conf additions
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
ssl_ca_file = '/path/to/ca.crt'
```

**Production Checklist:**
- [ ] Enable SSL/TLS for all database connections
- [ ] Use connection pooling with limits (PgBouncer)
- [ ] Set up database user with minimal required permissions
- [ ] Enable database audit logging
- [ ] Implement backup encryption
- [ ] Set up read replicas for analytics queries

---

### 4. API Security Headers & CORS

**Current State:**
- Permissive CORS (`allow_origins=["*"]`)
- Missing security headers
- No rate limiting

**Required Changes:**

```python
# backend/main.py - Security middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

app = FastAPI()

# Strict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sisuiq.uetcl.go.ug"],  # Specific domain only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["sisuiq.uetcl.go.ug", "localhost"]
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request):
    pass

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

**Production Checklist:**
- [ ] Restrict CORS to specific production domains
- [ ] Add all security headers (CSP, HSTS, X-Frame-Options, etc.)
- [ ] Implement rate limiting per user/IP
- [ ] Add request size limits
- [ ] Enable HTTPS only (redirect HTTP to HTTPS)

---

### 5. Input Validation & Sanitization

**Current State:**
- Basic Pydantic validation
- No sanitization of user input for RAG queries
- Potential for prompt injection attacks

**Required Changes:**

```python
# backend/schemas.py - Enhanced validation
from pydantic import BaseModel, Field, validator
import bleach

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=36, max_length=36)
    message: str = Field(..., min_length=1, max_length=4000)
    mode: str = Field(..., pattern="^(strategy_qa|actions|analytics|regulatory)$")

    @validator('message')
    def sanitize_message(cls, v):
        # Remove potential XSS
        v = bleach.clean(v, tags=[], strip=True)
        # Check for prompt injection patterns
        injection_patterns = [
            "ignore previous instructions",
            "disregard above",
            "system prompt",
        ]
        v_lower = v.lower()
        for pattern in injection_patterns:
            if pattern in v_lower:
                raise ValueError("Invalid input detected")
        return v
```

**Production Checklist:**
- [ ] Implement comprehensive input validation
- [ ] Add prompt injection detection
- [ ] Sanitize all user input before storage
- [ ] Validate file uploads (if added)
- [ ] Implement output encoding

---

### 6. Docker & Container Security

**Current State:**
- Running as root in containers
- Latest tags instead of pinned versions
- No resource limits
- Development-oriented Dockerfiles

**Required Changes:**

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim-bookworm AS builder

# Security: Don't run as root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Pin versions, verify checksums
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim-bookworm

# Security hardening
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=appuser:appgroup . .

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.prod.yml
version: "3.8"
services:
  backend:
    image: sisuiq-backend:v1.0.0  # Pinned version
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Production Checklist:**
- [ ] Run containers as non-root user
- [ ] Use read-only file systems where possible
- [ ] Drop all capabilities, add only required ones
- [ ] Set resource limits (CPU, memory)
- [ ] Pin image versions (no :latest tags)
- [ ] Scan images for vulnerabilities (Trivy, Snyk)
- [ ] Use distroless or minimal base images

---

### 7. Logging & Monitoring

**Current State:**
- Basic console logging
- No structured logging
- No audit trail
- No monitoring/alerting

**Required Changes:**

```python
# backend/logging_config.py
import logging
import structlog
from pythonjsonlogger import jsonlogger

# Structured JSON logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# Audit logging
async def audit_log(event: str, user_id: str, details: dict):
    logger = structlog.get_logger("audit")
    logger.info(
        event,
        user_id=user_id,
        details=details,
        timestamp=datetime.utcnow().isoformat()
    )
```

**Production Checklist:**
- [ ] Implement structured JSON logging
- [ ] Set up centralized log aggregation (ELK, CloudWatch, etc.)
- [ ] Add audit logging for sensitive operations
- [ ] Configure log rotation and retention
- [ ] Set up alerting for security events
- [ ] Never log sensitive data (passwords, tokens, PII)

---

### 8. Network Security

**Current State:**
- Services exposed on default ports
- No network segmentation
- No WAF or DDoS protection

**Required Changes:**

```yaml
# docker-compose.prod.yml - Network isolation
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
  database:
    driver: bridge
    internal: true

services:
  nginx:
    networks:
      - frontend
      - backend

  backend:
    networks:
      - backend
      - database
    # No ports exposed externally

  postgres:
    networks:
      - database
    # Only accessible from backend network
```

**Production Checklist:**
- [ ] Implement network segmentation
- [ ] Use a reverse proxy (nginx, traefik) with TLS termination
- [ ] Deploy behind WAF (Cloudflare, AWS WAF)
- [ ] Enable DDoS protection
- [ ] Restrict database access to backend only
- [ ] Use private subnets for internal services

---

### 9. OpenAI API Security

**Current State:**
- API key in environment variable
- No token usage limits
- No content filtering beyond OpenAI defaults

**Required Changes:**

```python
# backend/services/llm.py
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

class SecureLLMClient:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=30.0,
            max_retries=3,
        )
        self.daily_token_limit = 100000
        self.token_usage = TokenUsageTracker()

    async def chat(self, messages: list, user_id: str) -> str:
        # Check rate limits
        if await self.token_usage.get_daily_usage(user_id) > self.daily_token_limit:
            raise RateLimitExceeded("Daily token limit reached")

        # Add safety system prompt
        safe_messages = [
            {"role": "system", "content": SAFETY_SYSTEM_PROMPT},
            *messages
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=safe_messages,
            max_tokens=2000,
            user=user_id,  # For OpenAI abuse tracking
        )

        # Track usage
        await self.token_usage.record(user_id, response.usage.total_tokens)

        return response.choices[0].message.content
```

**Production Checklist:**
- [ ] Implement per-user token limits
- [ ] Add content moderation layer
- [ ] Monitor API costs and set budget alerts
- [ ] Log all LLM interactions for audit
- [ ] Implement fallback for API failures

---

### 10. Data Protection & Privacy

**Current State:**
- No data encryption at rest
- No PII handling procedures
- No data retention policies

**Production Checklist:**
- [ ] Encrypt sensitive data at rest (AES-256)
- [ ] Implement data classification (public, internal, confidential)
- [ ] Define and enforce data retention policies
- [ ] Add data anonymization for analytics
- [ ] Implement right-to-deletion capabilities
- [ ] Document data flows and processing activities
- [ ] Ensure compliance with Uganda Data Protection Act

---

## Quick Reference: Environment Variables for Production

```bash
# .env.production (use secrets manager in practice)

# Database
DATABASE_URL=postgresql+asyncpg://user:STRONGPASSWORD@db:5432/sisuiq?ssl=require

# Authentication
JWT_SECRET_KEY=<cryptographically-random-256-bit-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_TOKEN=<cryptographically-random-token>

# OpenAI
OPENAI_API_KEY=sk-...

# Vector DB
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=<api-key-if-cloud>

# Security
CORS_ORIGINS=https://sisuiq.uetcl.go.ug
TRUSTED_HOSTS=sisuiq.uetcl.go.ug

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
DAILY_TOKEN_LIMIT=100000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Deployment Checklist

Before deploying to production, ensure:

- [ ] All security issues above are addressed
- [ ] Penetration testing completed
- [ ] Security review by qualified personnel
- [ ] Incident response plan documented
- [ ] Backup and recovery procedures tested
- [ ] SSL certificates installed and auto-renewal configured
- [ ] Monitoring and alerting operational
- [ ] Security headers validated (securityheaders.com)
- [ ] Dependencies scanned for vulnerabilities
- [ ] Access logs enabled and reviewed

---

## Contact

For security concerns or vulnerability reports, contact:
- UETCL IT Security Team
- Email: security@uetcl.go.ug

---

*Last Updated: December 2024*
*Version: 1.0.0 (Demo)*
