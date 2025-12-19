FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
  tesseract-ocr \
  poppler-utils \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application into backend package structure
COPY . ./backend/

# Set PYTHONPATH so 'from backend.xxx' imports work
ENV PYTHONPATH=/app

EXPOSE 8000

# Railway provides PORT env var dynamically
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
