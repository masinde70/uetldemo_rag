#!/bin/bash
# SISUiQ - Stop Script
# Stops all services

cd "$(dirname "$0")/infra"

echo "🛑 Stopping SISUiQ Stack..."
docker compose stop
echo "✅ All services stopped"
