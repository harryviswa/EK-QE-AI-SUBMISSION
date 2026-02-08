# NexQA.ai Docker Setup Guide

Complete Docker and Docker Compose setup for running NexQA.ai on any system (Windows, Mac, Linux).

## 📋 Prerequisites

- **Docker** ([Download](https://www.docker.com/products/docker-desktop)) — 20.10+
- **Docker Compose** — Usually included with Docker Desktop
- **4GB RAM minimum** — 8GB recommended

## ✅ Quick Start (30 seconds)

### Step 1: Clone/Navigate to Project
```bash
cd EK-QE-AI-SUBMISSION
```

### Step 2: Create Environment File
```bash
# Copy example to .env
cp .env.docker .env

# Optional: Edit .env if using Azure OpenAI
# nano .env  (or edit in your editor)
```

### Step 3: Start Everything
```bash
docker compose up -d
```

### Step 4: Access the App
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000/api/health
- **Ollama:** http://localhost:11434/api/tags

**Done!** 🎉

---

## 🔧 Available Configurations

### Configuration 1: Full Offline with Local Ollama (Recommended for Development)

**`.env` configuration:**
```bash
EMBEDDING_PROVIDER=ollama
OLLAMA_HOST=http://ollama:11434
```

**Pros:**
- ✅ Completely free
- ✅ No internet required
- ✅ Fast local inference
- ✅ Good for development

**Cons:**
- ⚠️ Requires Docker to run Ollama container
- ⚠️ Initial model download takes time
- ⚠️ Uses significant disk space

**Start:**
```bash
cp .env.docker .env
docker compose up -d
```

### Configuration 2: Azure OpenAI Only (No Ollama Download)

**`.env` configuration:**
```bash
EMBEDDING_PROVIDER=azure
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_EMBEDDING_MODEL=text-embedding-ada-002
AZURE_OPENAI_MODEL=gpt-4
```

**Pros:**
- ✅ No local LLM required
- ✅ Latest GPT models
- ✅ Production-ready

**Cons:**
- ⚠️ Requires Azure subscription (pay-per-use)
- ⚠️ Needs internet connection
- ⚠️ Latency from API calls

**Start:**
```bash
cp .env.docker .env
# Edit .env with your Azure credentials
docker compose up -d
```

### Configuration 3: Hybrid (Azure LLM + Local Embeddings)

**`.env` configuration:**
```bash
EMBEDDING_PROVIDER=ollama
OLLAMA_HOST=http://ollama:11434
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-4
```

**Pros:**
- ✅ Fast embeddings (local)
- ✅ Powerful LLM (Azure)
- ✅ Lower costs than full Azure

**Cons:**
- ⚠️ Requires both Ollama setup and Azure account
- ⚠️ Mixed latency

**Start:**
```bash
cp .env.docker .env
# Edit .env with Azure credentials
docker compose up -d
```

---

## 🚀 Common Commands

### Start Services
```bash
# Start in background
docker compose up -d

# Start and watch logs
docker compose up

# Start specific service
docker compose up -d backend frontend
```

### Stop Services
```bash
# Stop all services
docker compose down

# Stop but keep data
docker compose stop

# Stop and remove all data (⚠️ deletes everything!)
docker compose down -v
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f ollama

# Last 100 lines
docker compose logs --tail=100
```

### Check Status
```bash
# List running containers
docker compose ps

# Check specific service
docker compose exec backend curl http://localhost:5000/api/health

# Check Ollama models
docker compose exec ollama ollama list
```

### Manage Models in Ollama

```bash
# List installed models
docker compose exec ollama ollama list

# Pull additional models
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull mistral:7b
docker compose exec ollama ollama pull qwen3:30b

# Remove a model
docker compose exec ollama ollama rm mistral:7b
```

---

## 💾 Data Persistence

### ChromaDB Storage
**Location:** Named volume `chroma_data`

ChromaDB (vector database) is automatically persisted. Even if you stop and restart containers:
```bash
docker compose down
docker compose up -d
# All your uploaded documents and knowledge base are still there!
```

### Ollama Models
**Location:** Named volume `ollama_data`

Downloaded models persist across restarts. This prevents re-downloading models:
```bash
# Models cached locally
docker compose down
docker compose up -d
# Models still available, no need to re-download
```

### Uploads
**Location:** `./backend/uploads` (mounted from host)

User uploaded files persist in the local filesystem.

### Reset Everything
```bash
# ⚠️ Deletes all data (documents, knowledge base, models)
docker compose down -v
docker volume prune

# Restart fresh
docker compose up -d
```

---

## 🔍 Troubleshooting

### Services Won't Start

**Check running containers:**
```bash
docker compose ps
```

**View error logs:**
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f ollama
```

### Port Already in Use

Ports `3000`, `5000`, or `11434` might be occupied:

**Option 1: Stop conflicting processes**
```bash
# Windows (PowerShell)
Get-Process | Where-Object { $_.Port -eq 3000 } | Stop-Process

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

**Option 2: Change ports in docker-compose.yaml**
```yaml
backend:
  ports:
    - "5001:5000"  # Changed from 5000:5000

frontend:
  ports:
    - "3001:3000"  # Changed from 3000:3000
```

### Out of Memory

Containers are hitting memory limits:

**Solution 1: Increase Docker memory**
- Open Docker Desktop Settings
- Resources → Memory
- Increase to 8GB or more

**Solution 2: Use lighter models**
```bash
docker compose exec ollama ollama pull gemma3:1b
```

### Can't Connect to Ollama

**Error:** "Connection refused to http://ollama:11434"

**Solution:**
```bash
# Check if ollama container is healthy
docker compose ps

# If not healthy, check logs
docker compose logs ollama

# Restart it
docker compose restart ollama

# Wait for it to be healthy (30-60 seconds)
docker compose ps
```

### Frontend Shows Blank Page or 404

**Check backend connectivity:**
```bash
# From host machine
curl http://localhost:5000/api/health

# Should return: {"status": "healthy", ...}
```

**Check frontend logs:**
```bash
docker compose logs frontend
```

### Models Take Too Long to Download

**Skip model pull on startup:**
Edit `docker-compose.yaml`, find the `ollama` service, change:
```yaml
command: sh -c 'ollama serve'  # Just run server, don't pull models
```

Then manually pull models when needed:
```bash
docker compose exec ollama ollama pull nomic-embed-text:latest
```

---

## 📊 System Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **RAM** | 4GB | 8GB+ | Ollama needs 2-4GB for models |
| **CPU** | 2 cores | 4+ cores | Better with more cores |
| **Disk** | 20GB | 50GB+ | Models can be 5-20GB each |
| **Network** | Not required | 500Mbps | Only if using Azure OpenAI |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│          Docker Network (nexqa-network)             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │  Frontend (3000) │      │  Backend (5000)  │   │
│  │  React/Vite      │      │  Flask API       │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│           │                         │              │
│           │    HTTP API calls       │              │
│           └────────────────────────►│              │
│                                     │              │
│                                     ├─────────────┐│
│                                     │             ││
│                       ┌─────────────▼──────┐     ││
│                       │ ChromaDB Volume    │     ││
│                       │ (Vector DB)        │     ││
│                       └────────────────────┘     ││
│                                                  ││
│                       ┌─────────────▼──────┐     ││
│                       │ Ollama (11434)     │     ││
│                       │ LLM Service        │     ││
│                       └────────────────────┘     ││
│                                                  ││
│                       ┌─────────────▼──────┐     ││
│                       │ Ollama Models Vol  │     ││
│                       │ (cached models)    │     ││
│                       └────────────────────┘     ││
│                                                  ││
│                       ┌──────────────────────────┘│
│                       │ Uploaded Files Volume    │
│                       │ (./backend/uploads)      │
│                       └────────────────────────┘
│
└─────────────────────────────────────────────────────┘

         ┌─────────────────────────────┐
         │   Host Machine              │
         │   (Your Computer)           │
         │                             │
         │ Ports:                      │
         │ - 3000 (Frontend)           │
         │ - 5000 (Backend)            │
         │ - 11434 (Ollama - optional) │
         └─────────────────────────────┘
```

---

## 🌍 Deploy to Cloud

### Azure Container Instances (ACI)

```bash
# Login to Azure
az login

# Create resource group
az group create -n nexqa -l eastus

# Create container registry
az acr create -g nexqa -n nexqaregistry --sku Basic

# Build and push images
docker compose build
docker tag nexqa-backend:latest nexqaregistry.azurecr.io/nexqa-backend:latest
docker push nexqaregistry.azurecr.io/nexqa-backend:latest

# Deploy with ACI
az container create \
  --resource-group nexqa \
  --name nexqa-app \
  --image nexqaregistry.azurecr.io/nexqa-backend:latest \
  --ports 3000 5000 11434 \
  --environment-variables EMBEDDING_PROVIDER=azure
```

### AWS ECS/Fargate

```bash
# Create ECR repository
aws ecr create-repository --repository-name nexqa

# Build and push
docker build -t nexqa-backend ./backend
docker tag nexqa-backend:latest <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/nexqa:latest
docker push <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/nexqa:latest
```

### Docker Hub

```bash
# Login
docker login

# Tag and push
docker compose build
docker tag nexqa-backend:latest yourusername/nexqa-backend:latest
docker push yourusername/nexqa-backend:latest

# Others can run
docker pull yourusername/nexqa-backend:latest
```

---

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Ollama Container Docs](https://ollama.ai)
- [ChromaDB Docker Setup](https://docs.trychroma.com/)

---

## 🆘 Support

For issues:
1. Check logs: `docker compose logs -f`
2. Verify containers: `docker compose ps`
3. Check volumes: `docker volume ls`
4. Reset if needed: `docker compose down -v && docker compose up -d`

---

**Built with ❤️ for Quality Engineers**

Happy containerized testing! 🐳
