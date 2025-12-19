# SISUiQ Quick Start Guide

Get up and running with the UETCL Strategy Copilot demo in under 10 minutes.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.13 or higher installed (3.11+ also works)
- [ ] Node.js 20 LTS or higher installed (22+ also works)
- [ ] PostgreSQL 16+ installed and running (14+ also works)
- [ ] Docker installed (for Qdrant)
- [ ] OpenAI API key

## Step 1: Clone and Setup

```bash
cd /Users/masinde/pytorch-test/LLMS/UETCL

# Verify you're in the right directory
pwd
# Should output: /Users/masinde/pytorch-test/LLMS/UETCL
```

## Step 2: Start Qdrant Vector Database

```bash
# Start Qdrant in Docker
docker run -d -p 6333:6333 --name sisuiq-qdrant qdrant/qdrant

# Verify it's running
curl http://localhost:6333/
# Should return: {"title":"qdrant - vector search engine"...}
```

## Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sisuiq

# Qdrant
QDRANT_URL=http://localhost:6333

# OpenAI
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small

# Auth (optional for demo)
JWT_SECRET=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# App
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF

# IMPORTANT: Edit .env and add your actual OpenAI API key
nano .env  # or use your preferred editor
```

## Step 4: Initialize Database

```bash
# Create PostgreSQL database
createdb sisuiq

# Or using psql
psql -U postgres -c "CREATE DATABASE sisuiq;"

# Run database initialization
python scripts/setup/init_db.py

# Initialize Qdrant collection
python scripts/setup/init_qdrant.py
```

## Step 5: Generate Sample Data (Optional)

```bash
# Generate sample strategy documents and outage data
python scripts/setup/generate_sample_data.py

# This will create:
# - data/strategy/sample_strategy.pdf
# - data/era/sample_regulations.pdf
# - data/analytics/sample_outages.csv
```

## Step 6: Ingest Data

```bash
# Ingest strategy documents
python scripts/ingest/ingest_strategy.py --input ../data/strategy/

# Ingest ERA regulatory documents
python scripts/ingest/ingest_era.py --input ../data/era/

# Ingest outage analytics
python scripts/ingest/ingest_analytics.py --input ../data/analytics/sample_outages.csv
```

## Step 7: Start Backend Server

```bash
# Make sure you're in the backend directory with venv activated
uvicorn main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

Test the backend:
```bash
# In a new terminal
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

## Step 8: Setup Frontend

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SISUiQ
EOF

# Start development server
npm run dev

# You should see:
# ▲ Next.js 15.x.x
# - Local:        http://localhost:3000
```

## Step 9: Access the Application

Open your browser and navigate to:

**Frontend**: http://localhost:3000
**Backend API Docs**: http://localhost:8000/docs
**Qdrant Dashboard**: http://localhost:6333/dashboard

## Step 10: Test the Demo

### Test Strategy Q&A Mode

1. Navigate to http://localhost:3000
2. Select "Strategy Q&A" mode
3. Ask: "What are UETCL's key strategic objectives for 2024-2029?"
4. Verify you get a response with citations

### Test Analytics + Strategy Mode

1. Switch to "Analytics + Strategy" mode
2. Ask: "What do outage patterns suggest about infrastructure priorities?"
3. Verify analytics data is incorporated in the response

### Test Regulatory Advisor Mode

1. Switch to "ERA Regulatory Mode"
2. Ask: "What are the key transmission reliability requirements?"
3. Verify ERA regulatory content is referenced

## Troubleshooting

### Backend won't start

**Issue**: `ModuleNotFoundError`
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Database connection error
```bash
# Check PostgreSQL is running
pg_isready
# Verify DATABASE_URL in .env is correct
```

**Issue**: Qdrant connection error
```bash
# Check Qdrant is running
docker ps | grep qdrant
# If not running:
docker start sisuiq-qdrant
```

### Frontend won't start

**Issue**: `Cannot find module`
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

**Issue**: API connection error
```bash
# Verify backend is running
curl http://localhost:8000/health
# Check NEXT_PUBLIC_API_URL in .env.local
```

### No data in responses

**Issue**: Empty citations or "I don't have information"
```bash
# Check data ingestion
curl http://localhost:8000/api/admin/documents
# Should return list of documents

# Re-run ingestion if needed
python scripts/ingest/ingest_strategy.py --input ../data/strategy/
```

### OpenAI API errors

**Issue**: `AuthenticationError`
```bash
# Verify API key in backend/.env
# Test API key:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Development Workflow

### Making Changes

**Backend changes**:
- FastAPI will auto-reload on file changes
- Check terminal for errors
- Test endpoints at http://localhost:8000/docs

**Frontend changes**:
- Next.js will hot-reload on file changes
- Check browser console for errors
- Test UI at http://localhost:3000

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Viewing Logs

**Backend logs**: Check the terminal where uvicorn is running

**Frontend logs**: Check browser console (F12) and terminal

**Qdrant logs**:
```bash
docker logs sisuiq-qdrant
```

## Next Steps

- [ ] Read the [Architecture Documentation](docs/architecture/README.md)
- [ ] Explore the [API Documentation](docs/api/README.md)
- [ ] Review [Project Structure](STRUCTURE.md)
- [ ] Add your own data to `data/` directories
- [ ] Customize agent prompts in `backend/agents/`
- [ ] Customize UI theme in `frontend/`

## Getting Help

- Check the main [README.md](README.md)
- Review [.claude](.claude) for project details
- Check [docs/](docs/) for comprehensive documentation

## Production Deployment

For production deployment instructions, see [docs/deployment.md](docs/deployment.md).

---

**Success!** You should now have a fully functional SISUiQ demo running locally.

Try asking complex questions that combine strategy, analytics, and regulatory knowledge to see the power of the hybrid RAG system!
