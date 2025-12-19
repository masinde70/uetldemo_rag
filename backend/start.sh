#!/bin/bash
# Create backend package structure for imports
mkdir -p /app/backend
cp -r /app/*.py /app/backend/ 2>/dev/null || true
cp -r /app/routers /app/backend/ 2>/dev/null || true
cp -r /app/services /app/backend/ 2>/dev/null || true
cp -r /app/models /app/backend/ 2>/dev/null || true
cp -r /app/agents /app/backend/ 2>/dev/null || true
cp -r /app/utils /app/backend/ 2>/dev/null || true
cp -r /app/config /app/backend/ 2>/dev/null || true
cp -r /app/rag /app/backend/ 2>/dev/null || true
cp -r /app/storage /app/backend/ 2>/dev/null || true
cp -r /app/prompts /app/backend/ 2>/dev/null || true
cp -r /app/observability /app/backend/ 2>/dev/null || true
cp -r /app/alembic /app/backend/ 2>/dev/null || true
cp -r /app/api /app/backend/ 2>/dev/null || true

export PYTHONPATH=/app
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
