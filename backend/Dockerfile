FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-api.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads data /data/chroma_db

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the Flask app
CMD ["python", "server.py"]
