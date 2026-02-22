#!/bin/bash
set -e

# Start Ollama service in the background
echo "Starting Ollama service..."
/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready by checking logs or waiting a fixed time
echo "Waiting for Ollama to start up (60 seconds initial wait)..."
sleep 60

max_attempts=30
attempt=0

# Try to pull the gemma3:1b model with retries
echo "Pulling gemma3:1b model (this may take a few minutes)..."
until ollama pull gemma3:1b 2>&1; do
    attempt=$((attempt+1))
    if [ $attempt -ge $max_attempts ]; then
        echo "Error: Failed to pull gemma3:1b after $max_attempts attempts"
        kill $OLLAMA_PID 2>/dev/null || true
        exit 1
    fi
    echo "  Attempt $attempt/$max_attempts: Retrying gemma3:1b pull..."
    sleep 5
done

echo "gemma3:1b pull complete!"

# Also pull nomic-embed-text for embeddings if not already present
echo "Pulling nomic-embed-text model for embeddings (this may take a few minutes)..."
attempt=0
until ollama pull nomic-embed-text:latest 2>&1; do
    attempt=$((attempt+1))
    if [ $attempt -ge 10 ]; then
        echo "Warning: Failed to pull nomic-embed-text after 10 attempts, continuing..."
        break
    fi
    echo "  Attempt $attempt/10: Retrying nomic-embed-text pull..."
    sleep 5
done

echo "Model setup complete!"

# Keep the service running
wait $OLLAMA_PID
