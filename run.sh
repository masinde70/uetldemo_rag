#!/bin/bash
# SISUiQ - Quick Start Script
# Starts all services (postgres, qdrant, backend, frontend, nginx)

set -e

cd "$(dirname "$0")/infra"

echo "🚀 Starting SISUiQ Stack..."

# Build and start all services
docker compose up -d --build

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check health
if curl -s http://localhost/api/health > /dev/null 2>&1; then
    echo "✅ Backend healthy"
else
    echo "⚠️  Backend still starting..."
fi

if curl -s http://localhost > /dev/null 2>&1; then
    echo "✅ Frontend healthy"
else
    echo "⚠️  Frontend still starting..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 SISUiQ Ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   🌐 App:    http://localhost"
echo "   📊 Admin:  http://localhost/admin"
echo "   🔧 API:    http://localhost/api/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Logs: cd infra && docker compose logs -f"
echo "🛑 Stop: cd infra && docker compose down"
