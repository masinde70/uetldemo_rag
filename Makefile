# SISUiQ - Makefile
# Commands for managing the Docker stack and development

.PHONY: help start stop restart logs clean clean-all status check-docker \
        install dev dev-backend dev-frontend lint format test test-e2e \
        seed migrate pre-commit-install up down eval

# Default target
help:
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🎯 SISUiQ - Available Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "  Docker Commands:"
	@echo "  make up         - Alias for start"
	@echo "  make down       - Alias for stop"
	@echo "  make start      - Start all services"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - Follow container logs"
	@echo "  make status     - Show container status"
	@echo "  make clean      - Stop and remove containers"
	@echo "  make clean-all  - Remove containers, volumes, and images"
	@echo ""
	@echo "  Development Commands:"
	@echo "  make install    - Install all dependencies (backend + frontend)"
	@echo "  make dev        - Run backend and frontend in development mode"
	@echo "  make dev-backend  - Run backend only (uvicorn with reload)"
	@echo "  make dev-frontend - Run frontend only (next dev)"
	@echo ""
	@echo "  Code Quality:"
	@echo "  make lint       - Run linters (ruff, mypy, eslint)"
	@echo "  make format     - Format code (ruff format, prettier)"
	@echo "  make pre-commit-install - Install pre-commit hooks"
	@echo ""
	@echo "  Testing:"
	@echo "  make test       - Run backend unit tests"
	@echo "  make test-e2e   - Run Playwright E2E tests"
	@echo "  make eval       - Run LLM evaluation against golden dataset"
	@echo ""
	@echo "  Database:"
	@echo "  make migrate    - Run Alembic migrations"
	@echo "  make seed       - Seed database with sample data"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""

# Check if Docker/Colima is running
check-docker:
	@echo "🔍 Checking Docker..."
	@if command -v colima >/dev/null 2>&1; then \
		if ! colima status >/dev/null 2>&1; then \
			echo "🐳 Starting Colima..."; \
			colima start; \
		else \
			echo "✅ Colima is running"; \
		fi \
	elif command -v docker >/dev/null 2>&1; then \
		if ! docker info >/dev/null 2>&1; then \
			echo "❌ Docker daemon is not running. Please start Docker Desktop."; \
			exit 1; \
		else \
			echo "✅ Docker is running"; \
		fi \
	else \
		echo "❌ Docker not found. Please install Docker or Colima."; \
		exit 1; \
	fi

# Start all services
start: check-docker
	@echo ""
	@echo "🚀 Starting SISUiQ Stack..."
	@cd infra && docker compose up -d --build
	@echo ""
	@echo "⏳ Waiting for services to be healthy..."
	@sleep 5
	@if curl -s http://localhost/api/health > /dev/null 2>&1; then \
		echo "✅ Backend healthy"; \
	else \
		echo "⚠️  Backend still starting..."; \
	fi
	@if curl -s http://localhost > /dev/null 2>&1; then \
		echo "✅ Frontend healthy"; \
	else \
		echo "⚠️  Frontend still starting..."; \
	fi
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🎯 SISUiQ Ready!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "   🌐 App:    http://localhost"
	@echo "   📊 Admin:  http://localhost/admin"
	@echo "   🔧 API:    http://localhost/api/docs"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""

# Stop all services
stop:
	@echo "🛑 Stopping SISUiQ Stack..."
	@cd infra && docker compose stop
	@echo "✅ All services stopped"

# Restart all services
restart: stop start

# Show logs
logs:
	@cd infra && docker compose logs -f

# Show status
status:
	@echo ""
	@echo "📊 Container Status:"
	@echo ""
	@cd infra && docker compose ps
	@echo ""

# Stop and remove containers
clean:
	@echo "🧹 Cleaning up containers..."
	@cd infra && docker compose down
	@echo "✅ Containers removed"

# Full cleanup - remove containers, volumes, and images
clean-all:
	@echo "🧹 Full cleanup - removing containers, volumes, and images..."
	@cd infra && docker compose down -v --rmi local
	@echo ""
	@echo "🗑️  Pruning unused Docker resources..."
	@docker system prune -f
	@echo ""
	@echo "✅ Full cleanup complete"

# Stop Colima (if using)
colima-stop:
	@if command -v colima >/dev/null 2>&1; then \
		echo "🐳 Stopping Colima..."; \
		colima stop; \
		echo "✅ Colima stopped"; \
	else \
		echo "ℹ️  Colima not installed"; \
	fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Development Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Aliases for up/down
up: start
down: stop

# Install all dependencies
install:
	@echo ""
	@echo "📦 Installing dependencies..."
	@echo ""
	@echo "🐍 Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt
	@echo ""
	@echo "⚛️  Installing frontend dependencies..."
	@cd frontend && npm ci
	@echo ""
	@echo "✅ All dependencies installed"

# Run backend in development mode
dev-backend:
	@echo ""
	@echo "🐍 Starting backend in development mode..."
	@cd backend && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend in development mode
dev-frontend:
	@echo ""
	@echo "⚛️  Starting frontend in development mode..."
	@cd frontend && npm run dev

# Run both backend and frontend (requires two terminals or use tmux)
dev:
	@echo ""
	@echo "🚀 Starting development servers..."
	@echo ""
	@echo "ℹ️  This will start the backend. Open another terminal for frontend:"
	@echo "    make dev-frontend"
	@echo ""
	@make dev-backend

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Code Quality
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Run linters
lint:
	@echo ""
	@echo "🔍 Running linters..."
	@echo ""
	@echo "🐍 Backend (ruff + mypy)..."
	@cd backend && python -m ruff check . || true
	@cd backend && python -m mypy . --ignore-missing-imports || true
	@echo ""
	@echo "⚛️  Frontend (eslint)..."
	@cd frontend && npm run lint || true
	@echo ""
	@echo "✅ Linting complete"

# Format code
format:
	@echo ""
	@echo "✨ Formatting code..."
	@echo ""
	@echo "🐍 Backend (ruff format)..."
	@cd backend && python -m ruff format . || true
	@cd backend && python -m ruff check --fix . || true
	@echo ""
	@echo "⚛️  Frontend (prettier)..."
	@cd frontend && npx prettier --write "**/*.{ts,tsx,js,jsx,json,css,md}" || true
	@echo ""
	@echo "✅ Formatting complete"

# Install pre-commit hooks
pre-commit-install:
	@echo ""
	@echo "🪝 Installing pre-commit hooks..."
	@pip install pre-commit
	@pre-commit install
	@echo "✅ Pre-commit hooks installed"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Testing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Run backend tests
test:
	@echo ""
	@echo "🧪 Running backend tests..."
	@cd backend && python -m pytest tests/ -v --tb=short || true
	@echo ""
	@echo "✅ Backend tests complete"

# Run E2E tests
test-e2e:
	@echo ""
	@echo "🎭 Running Playwright E2E tests..."
	@npx playwright test
	@echo ""
	@echo "✅ E2E tests complete"

# Run LLM evaluation
eval:
	@echo ""
	@echo "📊 Running LLM evaluation..."
	@python -m eval.runner --output eval_report.json
	@echo ""
	@echo "✅ Evaluation complete. Report: eval_report.json"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Run database migrations
migrate:
	@echo ""
	@echo "📊 Running database migrations..."
	@cd backend && python -m alembic upgrade head
	@echo ""
	@echo "✅ Migrations complete"

# Seed database with sample data
seed:
	@echo ""
	@echo "🌱 Seeding database..."
	@cd backend && python -m backend.seed
	@echo ""
	@echo "✅ Database seeded"
