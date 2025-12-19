# SISUiQ Production Readiness Checklist

## ERA/UETCL Strategy & Regulatory Copilot

A structured checklist for production deployment. Items are categorized by priority level.

**Legend:**
- ✅ **MUST** - Required for production
- ⚠️ **SHOULD** - Strongly recommended
- 💡 **OPTIONAL** - Nice to have

---

## Infrastructure

### Container Hardening

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Run containers as non-root user | ⬜ | Add `USER` directive in Dockerfiles |
| ✅ MUST | Use slim/alpine base images | ⬜ | `python:3.13-slim`, `node:20-alpine` |
| ✅ MUST | Pin all base image versions | ⬜ | Never use `:latest` in production |
| ⚠️ SHOULD | Read-only filesystem where possible | ⬜ | `read_only: true` in docker-compose |
| ⚠️ SHOULD | Drop all capabilities | ⬜ | `cap_drop: [ALL]` |
| ⚠️ SHOULD | Set memory limits | ⬜ | Prevent OOM cascades |
| 💡 OPTIONAL | Use distroless images | ⬜ | Minimal attack surface |

### Dependency Management

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Pin all dependency versions | ⬜ | `requirements.txt`, `package-lock.json` |
| ✅ MUST | Scan for CVEs | ⬜ | Use `pip-audit`, `npm audit` |
| ⚠️ SHOULD | Automate dependency updates | ⬜ | Dependabot, Renovate |
| ⚠️ SHOULD | Lock file integrity check | ⬜ | Verify lockfiles in CI |

---

## Network & Proxy

### Nginx Configuration

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | TLS termination at proxy | ⬜ | HTTPS for all external traffic |
| ✅ MUST | Security headers configured | ⬜ | CSP, X-Frame-Options, etc. |
| ✅ MUST | Rate limiting on `/api/chat` | ⬜ | Prevent LLM abuse |
| ✅ MUST | Internal services not exposed | ⬜ | Only nginx on 80/443 |
| ⚠️ SHOULD | HTTP → HTTPS redirect | ⬜ | Force secure connections |
| ⚠️ SHOULD | HSTS enabled | ⬜ | `max-age=31536000` |

### TLS Configuration

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Valid SSL certificate | ⬜ | Let's Encrypt or enterprise CA |
| ✅ MUST | TLS 1.2+ only | ⬜ | Disable TLS 1.0/1.1 |
| ⚠️ SHOULD | Certificate auto-renewal | ⬜ | Certbot cron job |
| ⚠️ SHOULD | OCSP stapling | ⬜ | Faster TLS handshakes |
| 💡 OPTIONAL | Certificate transparency | ⬜ | CT logs for monitoring |

### Network Security

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Firewall configured | ⬜ | Allow only 80/443 inbound |
| ⚠️ SHOULD | VPC/private network | ⬜ | Isolate internal services |
| ⚠️ SHOULD | DDoS protection | ⬜ | Cloudflare, AWS Shield |

---

## Backend Service

### API Security

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Proper JWT authentication | ⬜ | Replace demo token |
| ✅ MUST | CORS locked to frontend origin | ⬜ | No wildcards |
| ✅ MUST | Input validation | ⬜ | Pydantic models on all endpoints |
| ✅ MUST | Rate limiting | ⬜ | Especially `/api/chat` |
| ⚠️ SHOULD | Request size limits | ⬜ | Max 20MB for uploads |
| ⚠️ SHOULD | API versioning | ⬜ | `/api/v1/` prefix |

### File Uploads

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | File type validation | ⬜ | Whitelist: PDF, CSV |
| ✅ MUST | File size limits | ⬜ | Max 20MB enforced |
| ⚠️ SHOULD | Malware scanning | ⬜ | ClamAV integration |
| ⚠️ SHOULD | Secure temp file handling | ⬜ | Cleanup after processing |

### LLM Integration

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | API key rotation | ⬜ | OpenAI key in secrets manager |
| ⚠️ SHOULD | Request timeout | ⬜ | 60s max per LLM call |
| ⚠️ SHOULD | Token budget limits | ⬜ | Prevent runaway costs |
| ⚠️ SHOULD | Prompt injection mitigation | ⬜ | Input sanitization |

---

## Frontend

### Build & Deploy

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Production build | ⬜ | `npm run build` |
| ✅ MUST | Environment variables | ⬜ | No hardcoded secrets |
| ⚠️ SHOULD | Static asset caching | ⬜ | Long cache headers |
| ⚠️ SHOULD | Bundle size optimization | ⬜ | Code splitting |

### Client Security

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Secure token storage | ⬜ | HttpOnly cookies preferred |
| ✅ MUST | XSS prevention | ⬜ | React escapes by default |
| ⚠️ SHOULD | CSP nonces | ⬜ | For inline scripts |

---

## PostgreSQL Database

### Security

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Strong passwords | ⬜ | 32+ char random string |
| ✅ MUST | No default credentials | ⬜ | Change `sisuiq:sisuiq` |
| ✅ MUST | Network isolation | ⬜ | Internal network only |
| ⚠️ SHOULD | TLS connections | ⬜ | `sslmode=require` |
| ⚠️ SHOULD | Connection pooling | ⬜ | PgBouncer |

### Backup & Recovery

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Automated backups | ⬜ | Daily `pg_dump` |
| ✅ MUST | Backup encryption | ⬜ | Encrypt at rest |
| ✅ MUST | Backup testing | ⬜ | Monthly restore tests |
| ⚠️ SHOULD | Point-in-time recovery | ⬜ | WAL archiving |
| ⚠️ SHOULD | Off-site backup | ⬜ | Different region/provider |

### Performance

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ⚠️ SHOULD | Connection limits | ⬜ | Match pool size |
| ⚠️ SHOULD | Query timeouts | ⬜ | Prevent long-running queries |
| 💡 OPTIONAL | Read replicas | ⬜ | For scaling reads |

---

## Qdrant Vector Store

### Security

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | API key authentication | ⬜ | Enable auth in Qdrant |
| ✅ MUST | Network isolation | ⬜ | Internal network only |
| ⚠️ SHOULD | TLS for connections | ⬜ | If network traverses boundaries |

### Backup & Recovery

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Snapshot backups | ⬜ | Regular collection snapshots |
| ⚠️ SHOULD | Backup testing | ⬜ | Verify restore works |
| 💡 OPTIONAL | Replication | ⬜ | For high availability |

---

## Observability

### Logging

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Structured JSON logs | ⬜ | Already implemented |
| ✅ MUST | Log aggregation | ⬜ | ELK, Loki, CloudWatch |
| ⚠️ SHOULD | Log rotation | ⬜ | Prevent disk fill |
| ⚠️ SHOULD | Sensitive data redaction | ⬜ | No PII in logs |

### Metrics

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Prometheus metrics | ⬜ | Already implemented |
| ⚠️ SHOULD | Grafana dashboards | ⬜ | Visualize key metrics |
| ⚠️ SHOULD | Alerting rules | ⬜ | Error rate, latency |

### Tracing

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ⚠️ SHOULD | Trace ID propagation | ⬜ | Already implemented |
| 💡 OPTIONAL | OpenTelemetry export | ⬜ | Jaeger, Zipkin |

---

## Security

### Secret Management

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | No secrets in code | ⬜ | Use env vars only |
| ✅ MUST | Secrets in vault/KMS | ⬜ | HashiCorp Vault, AWS Secrets Manager |
| ✅ MUST | CI/CD secrets | ⬜ | GitHub Secrets, GitLab CI vars |
| ⚠️ SHOULD | Secret rotation | ⬜ | Automated rotation |

### API Key Management

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Unique keys per environment | ⬜ | Dev/staging/prod separation |
| ✅ MUST | Key rotation procedure | ⬜ | Document and test |
| ⚠️ SHOULD | Usage monitoring | ⬜ | Alert on anomalies |

### Access Control

| Priority | Item | Status | Notes |
|----------|------|--------|-------|
| ✅ MUST | Admin role separation | ⬜ | Not all users are admins |
| ✅ MUST | Audit logging | ⬜ | Who did what, when |
| ⚠️ SHOULD | MFA for admin access | ⬜ | Especially for prod |

---

## Deployment Commands

### Development

```bash
# Start with dev profile (includes seeding + Prometheus)
cd infra
docker compose --profile dev up -d

# Seed database manually
docker compose exec backend python -m backend.seed
```

### Staging/Production

```bash
# Start without dev profile
cd infra
docker compose up -d

# Run migrations
docker compose exec backend alembic upgrade head
```

### Enable TLS

1. Generate or obtain SSL certificates
2. Mount certs in nginx container:
   ```yaml
   volumes:
     - ./nginx/ssl/cert.pem:/etc/nginx/ssl/cert.pem:ro
     - ./nginx/ssl/key.pem:/etc/nginx/ssl/key.pem:ro
   ```
3. Uncomment TLS config in `nginx/nginx.conf`
4. Add port 443 to nginx service:
   ```yaml
   ports:
     - "80:80"
     - "443:443"
   ```

### Self-Signed Cert (Testing Only)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout infra/nginx/ssl/key.pem \
  -out infra/nginx/ssl/cert.pem \
  -subj "/CN=localhost"
```

---

## Pre-Deployment Checklist

Before going live, verify:

- [ ] All MUST items above are addressed
- [ ] Secrets rotated from development values
- [ ] Backups configured and tested
- [ ] Monitoring and alerting in place
- [ ] Incident response plan documented
- [ ] Load testing completed
- [ ] Security review/penetration test performed
- [ ] Rollback procedure tested

---

## Contact

For security concerns or production deployment support:
- Technical Lead: [TBD]
- Security Team: [TBD]
- Operations: [TBD]
