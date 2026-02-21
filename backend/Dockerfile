FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-api.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY . .

# Create non-root user and necessary directories
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/uploads /data/chroma_db \
    && chown -R appuser:appuser /app /data

USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the Flask app with a production WSGI server
CMD ["waitress-serve", "--listen=0.0.0.0:5000", "server:app"]
