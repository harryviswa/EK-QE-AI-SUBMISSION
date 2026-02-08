# NexQA.ai — Quality Engineering AI Assistant

![NexQA.ai](https://img.shields.io/badge/NexQA.ai-Quality%20Engineering%20AI-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue)
![React](https://img.shields.io/badge/react-18-blue)

## Overview

**NexQA.ai** is a modern, privacy-first Retrieval-Augmented Generation (RAG) application tailored for Quality Engineers (QEs). It features a **React frontend with glassmorphism design** paired with a **Flask backend API**. Empowering QE teams with AI-assisted test case generation, validation, API automation, and knowledge management.

## 🎯 Assessment Alignment: Lead Quality Assurance Engineer (AI)

This repository doubles as the working submission for the **Lead Quality Assurance Engineer (AI) — Future of Quality Engineering Assessment**. The challenge demands a concrete, executable solution that reimagines how software quality is achieved using AI, automation, and modern engineering practices. Here’s how NexQA.ai satisfies every requirement:

| Assessment Expectation | How NexQA.ai Delivers |
| --- | --- |
| **Functional Solution** | End-to-end RAG platform with React + Flask + ChromaDB, fully runnable via Docker Compose or local setup. - Currently local setup should be working |
| **AI-First Quality Engineering** | Integrates Ollama or Azure OpenAI for LLM reasoning, AI-driven test generation, validation, risk analysis, and automation script authoring. - Azure OpenAI is an addition and can be extended for later integration |
| **Performance & Scalability** | Uses persistent ChromaDB, efficient chunking, cosine similarity search, and cross-encoder re-ranking for high-quality retrieval at scale. |
| **Data & Storage Strategy** | Supports PDF/TXT/XLS/XLSX uploads, persistent vector stores, caching-friendly APIs, and URL ingestion with structured chunk metadata. |
| **RAG Considerations** | Handles context selection, chunk overlap, embedding provider switching, latency logging, and traceable source attribution. |
| **Modern UX** | Glassmorphism UI, contextual help on first load, Excel export for tables, and responsive layout tailored for enterprise teams. |
| **Deliverables** | Working codebase (this repo), comprehensive README (>1 page) covering problem, approach, architecture, performance, and execution steps. |
| **Walkthrough Ready** | Detailed documentation plus logging, health checks, and observability hooks to discuss trade-offs, limitations, and next steps during interviews. |

>*Stretch Goal*: (https://drive.google.com/file/d/1EPCxiE8JWCJrXFZtWOIR-oXHqMdH2Gq5/view?usp=sharing)

### What Makes NexQA.ai Unique?

- 🤖 **AI-Powered Testing** — Generate test cases, strategies, and validations using local or cloud LLMs
- 🔒 **Privacy-First** — Run completely offline with local Ollama LLMs or use Azure OpenAI
- 🎨 **Modern UI** — Glassmorphism design with smooth animations, centered title with glass effect
- 🔧 **API Automation** — Generate Python automation scripts from Swagger/OpenAI specs
- ✅ **Test Validation** — Upload Excel testcases and get AI-powered gap analysis
- 📚 **Knowledge Base** — Ingest PDFs, Excel, text files, and web pages into your vector store

## ✨ Key Features

### Core Capabilities
- 🎨 **Modern Glassmorphism UI** — Frosted glass effects with Tailwind CSS, centered title with glass effect
- 📤 **Multi-Format Upload** — PDFs, Excel (.xlsx/.xls), text files (max 50MB)
- 🌐 **Web Integration** — Add external web pages as knowledge sources
- 💬 **Interactive Chat** — Context-aware conversations with source attribution and contextual help on first load
- 📊 **Export Anywhere** — PDF, Excel, clipboard export, and smart Excel export for table responses
- ℹ️ **Built-in Help** — Comprehensive help information displayed on first load with all available actions

### Quality Engineering Features
- 🧪 **Test Case Generation** — AI-generated test scenarios from requirements
- ✅ **Test Validation** — Upload Excel testcases and identify missing coverage
- 📋 **Strategy Planning** — Generate comprehensive test strategies and risk assessments
- 🔧 **API Automation** — Create executable Python scripts from Swagger/OpenAPI specs
- 🎯 **Smart Retrieval** — Cross-encoder re-ranking for high-quality context

### Technical Features
- 🔍 **Semantic Search** — ChromaDB vector database with cosine similarity
- 🤖 **Dual LLM Support** — Offline (Ollama) and online (Azure OpenAI)
- 🔄 **Flexible Embeddings** — Choose between Ollama or Azure OpenAI embeddings
- 👤 **Multi-User Ready** — Per-user document collections with user_id metadata
- 🐳 **Docker Ready** — Complete Docker Compose setup for easy deployment
- 🪟 **Windows Optimized** — Production-ready with Waitress WSGI server
- 📑 **Excel Export** — Client-side Excel generation from table responses using xlsx library
- 🆘 **Contextual Help** — Auto-displayed help section on first chat load with action types and usage tips

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                             │
│               http://localhost:3000                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              React Frontend (Vite + TailwindCSS)                │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ DocumentUpload│ QueryChat   │SourceManager │ SwaggerAuto  │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│  │ ValidateTestcases │ Sidebar │ GlassBackground              │ │
│  └──────────────────────┴─────┴──────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API (axios)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Flask Backend (Python 3.11/3.12)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API Routes (12 endpoints)                                │  │
│  │  • /api/health, /api/info                                │  │
│  │  • /api/documents/* (upload, add-url, list)              │  │
│  │  • /api/automation/generate-from-swagger                 │  │
│  │  • /api/validate/testcases                               │  │
│  │  • /api/query/* (search, rag)                            │  │
│  │  • /api/export/* (pdf, excel)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│  ┌──────────────────────────┴──────────────────────────────┐   │
│  │ models.py — RAG Pipeline                                 │   │
│  │  • Document Processing (PDF, Excel, TXT, Web)            │   │
│  │  • Embedding (Ollama or Azure OpenAI)                    │   │
│  │  • Vector Store (ChromaDB)                               │   │
│  │  • Retrieval + Cross-Encoder Re-ranking                  │   │
│  │  • LLM Calls (Ollama or Azure OpenAI)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
   ┌──────────────────┐       ┌──────────────────┐
   │  Ollama Service  │       │  Azure OpenAI    │
   │  (Local LLM)     │       │  (Cloud LLM)     │
   │  :11434          │       │  Optional        │
   └──────────────────┘       └──────────────────┘
              │
              ▼
   ┌──────────────────┐
   │  ChromaDB        │
   │  Vector Store    │
   │  (Persistent)    │
   └──────────────────┘
```

### Data Flow

1. **Document Ingestion**: Files/URLs → Processing → Chunking → Embedding → ChromaDB
2. **Query Processing**: User Query → Vector Search → Re-ranking → Context → LLM → Response
3. **Automation**: Swagger URL → Parse OpenAPI → Generate Python Script → Download

## 📁 Folder Structure

```
EK-QE-AI-SUBMISSION/
│
├── backend/                           # Flask REST API Backend
│   ├── server.py                      # Main API server (12 endpoints)
│   ├── server_production.py          # Waitress WSGI production server
│   ├── models.py                      # RAG pipeline & document processing
│   ├── prompts.py                     # LLM prompt templates
│   ├── utils.py                       # PDF/Excel export utilities (uses fpdf2)
│   ├── swagger_generator.py          # OpenAPI to Python script generator
│   ├── check_server.py                # Health check diagnostic tool
│   ├── check_db.py                    # ChromaDB diagnostic tool
│   ├── start-server.bat               # Windows startup script
│   ├── requirements-api.txt           # Python dependencies
│   ├── .env.example                   # Environment variables template
│   ├── Dockerfile                     # Backend containerization
│   ├── README.md                      # Backend documentation
│   ├── harry-rag-chroma-db/           # Vector database storage
│   └── uploads/                       # Uploaded files
│
├── frontend/                          # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUpload.jsx     # File upload UI with drag-drop
│   │   │   ├── QueryChat.jsx          # Chat interface with markdown, help info, Excel export
│   │   │   ├── SourceManager.jsx      # Document management panel
│   │   │   ├── SwaggerAutomation.jsx  # API automation generator
│   │   │   ├── ValidateTestcases.jsx  # Test validation interface
│   │   │   ├── Sidebar.jsx            # Navigation sidebar
│   │   │   └── GlassBackground.jsx    # Animated background
│   │   ├── api/
│   │   │   └── client.js              # Axios API client
│   │   ├── styles/
│   │   │   └── globals.css            # Glassmorphism styles + CSS vars
│   │   ├── App.jsx                    # Main app orchestration (centered title)
│   │   └── main.jsx                   # React entry point
│   ├── index.html
│   ├── package.json                   # Dependencies (includes xlsx ^0.18.5)
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── Dockerfile                     # Frontend containerization
│   └── README.md                      # Frontend documentation
│
├── .gitignore
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites

**Required (pick one):**
- **Docker & Docker Compose** ([Download Docker Desktop](https://www.docker.com/products/docker-desktop)) ⭐ **Recommended**
- OR **Python 3.11 or 3.12** + **Node.js 18+** + **Ollama**

**Optional:**
- **Azure OpenAI** account — For cloud-based embeddings and LLM

##VIDEO DEMO: https://drive.google.com/file/d/1EPCxiE8JWCJrXFZtWOIR-oXHqMdH2Gq5/view?usp=sharing

### Option 1: Local Development (Advanced)

#### Step 1: Install Ollama

Download and install Ollama, then pull models:

```bash
# Start Ollama service
ollama serve

# In another terminal, pull models
ollama pull nomic-embed-text:latest  # For embeddings
ollama pull gemma3:1b                # For LLM (lightweight)
# Or use other models: llama3.2:3b, mistral:7b, qwen3:30b
```

#### Step 2: Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (Python 3.11 or 3.12 compatible)
pip install -r requirements-api.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env if needed (defaults work for local Ollama)

# Start Flask server
python server.py
```

✅ Backend runs on **http://localhost:5000**

**For Production (Windows):** Use `python server_production.py` for Waitress WSGI server.

#### Step 3: Setup Frontend

Open a **new terminal**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies (includes xlsx ^0.18.5)
npm install

# Start development server
npm run dev
```

✅ Frontend runs on **http://localhost:5173** (Vite dev server)

#### Step 4: Access Application

Open your browser to **http://localhost:5173**


### Option 2: Docker Compose (Recommended - Works on All Systems)  - Currently having issue with Backend

**Easiest way to run on Windows, Mac, or Linux - no installation needed!**

```bash
# Step 1: Navigate to project
cd EK-QE-AI-SUBMISSION

# Step 2: Create environment file
cp .env.docker .env

# Step 3: Start all services (3 seconds!)
docker compose up -d

# Step 4: Access the app
# Frontend: http://localhost:3000
# Backend: http://localhost:5000/api/health
# Ollama: http://localhost:11434/api/tags
```

**What's running:**
- ✅ Frontend (React)
- ✅ Backend (Flask API)
- ✅ Ollama (LLM service)
- ✅ ChromaDB (vector database with persistent storage)

**See logs:**
```bash
docker compose logs -f
```

**Stop services:**
```bash
docker compose down
```

**For detailed Docker setup see** [DOCKER_SETUP.md](DOCKER_SETUP.md)

---




### Option 3: Using Startup Script (Windows Only)

We provide a batch script for easy Windows startup:

```batch
cd backend
start-server.bat
```

This script:
1. Kills any existing Python server processes
2. Activates virtual environment
3. Installs dependencies (if needed)
4. Starts the Flask server

Then start the frontend separately:
```batch
cd frontend
npm run dev
```

## ⚙️ Environment Configuration

### Backend Configuration (`backend/.env`)

Copy the example file:
```bash
cd backend
cp .env.example .env
```

**Configuration Options:**

```bash
# ==================== EMBEDDING PROVIDER ====================
# Choose: 'ollama' (local, free) or 'azure' (cloud, paid)
EMBEDDING_PROVIDER=ollama

# ==================== OLLAMA (Local) ====================
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest

# ==================== AZURE OPENAI (Cloud) ====================
# Only required if EMBEDDING_PROVIDER=azure or using Azure for LLM
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_EMBEDDING_MODEL=text-embedding-ada-002
AZURE_OPENAI_MODEL=gpt-4

# ==================== DATABASE ====================
CHROMA_DB_PATH=./harry-rag-chroma-db

# ==================== SERVER ====================
FLASK_ENV=production
FLASK_DEBUG=False
```

### Frontend Configuration (`frontend/.env`)

Usually not needed, but you can customize:

```bash
VITE_API_URL=http://localhost:5000/api
```

### Switching Embedding Providers

#### Using Ollama (Default — Free & Local)

```bash
EMBEDDING_PROVIDER=ollama
```
- No API costs
- Requires local Ollama installation
- Fast local inference
- ~768 dimensional embeddings

#### Using Azure OpenAI (Cloud — Paid)

```bash
EMBEDDING_PROVIDER=azure
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://...
```
- Pay-per-use pricing
- No local resources needed
- 1536 dimensional embeddings (ada-002)
- See [backend/AZURE_MIGRATION.md](backend/AZURE_MIGRATION.md) for detailed migration guide

**⚠️ Important:** When switching providers, you **must delete** the `harry-rag-chroma-db` folder and re-upload all documents because embeddings from different models are incompatible.

## 📡 API Endpoints

### Health & Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check, returns status and timestamp |
| GET | `/api/info` | API info, available models, active model |

### Document Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload PDF, TXT, XLSX, XLS files (max 50MB) |
| POST | `/api/documents/add-url` | Add web page as knowledge source |
| GET | `/api/documents/list` | List user's uploaded documents |

### API Automation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/automation/generate-from-swagger` | Generate Python automation script from Swagger/OpenAPI URL |

### Test Validation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/validate/testcases` | Full validation with LLM analysis (identifies missing testcases) |
| POST | `/api/validate/testcases/quick` | Quick validation without LLM (metadata only) |

### Query & RAG
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/query/search` | Semantic vector search in knowledge base |
| POST | `/api/query/rag` | RAG query with LLM response (supports: qa, testcase, strategy, risk, validate) |

### Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/export/pdf` | Export conversation as PDF |
| POST | `/api/export/excel` | Export data as Excel spreadsheet |

### Request Examples

#### Upload Document
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "X-User-ID: user123" \
  -F "file=@requirements.pdf"
```

#### RAG Query
```bash
curl -X POST http://localhost:5000/api/query/rag \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{
    "query_text": "What are the login requirements?",
    "query_type": "qa",
    "mode": "offline",
    "temperature": 0.7
  }'
```

#### Generate API Automation Script
```bash
curl -X POST http://localhost:5000/api/automation/generate-from-swagger \
  -H "Content-Type: application/json" \
  -d '{
    "swagger_url": "https://petstore.swagger.io/v2/swagger.json"
  }'
```

#### Validate Testcases
```bash
curl -X POST http://localhost:5000/api/validate/testcases \
  -H "X-User-ID: user123" \
  -F "file=@testcases.xlsx"
```

## 📖 Usage Guide

### 1. Upload Knowledge Sources

#### Upload Files
1. Click **"Knowledge Sources"** tab in the left sidebar
2. Drag & drop files or click **"Choose Files"**
3. Supported formats: PDF, TXT, XLSX, XLS (max 50MB each)
4. Files are automatically processed, chunked, embedded, and stored
5. View uploaded files in the **"My Documents"** panel

#### Add Web Pages
1. In the **"Knowledge Sources"** tab, click the **"+ Add URL"** button
2. Paste the web page URL
3. Web content is scraped, processed, and added to your knowledge base

### 2. Ask Questions (RAG Query)

1. Click **"Ask Questions"** tab
2. **First-time users:** An automatic help section displays with:
   - All 8 available action types (QA, Test Cases, Strategy, Risk, Validate, API Automation, etc.)
   - Usage instructions and tips
   - Example queries
3. Select a query type:
   - **QA** — General question & answer
   - **Test Cases** — Generate test scenarios
   - **Strategy** — Create test strategy document
   - **Risk** — Identify risks and mitigation
   - **Validate** — Validate existing test coverage
4. Type your question
5. Click **"Send"** or press Enter
6. View AI response with source attribution
7. **Excel Export:** For responses with tables, click the Excel icon to download as .xlsx file
8. Export response (Copy, Download)

**Example Questions:**
- "What are the authentication requirements?"
- "Generate test cases for the login feature"
- "Create a test strategy for API security testing"
- "What risks exist in the payment flow?"

### 3. Validate Test Cases

1. Click **"Validate Tests"** tab
2. Upload an Excel file with your test cases
   - Expected format: Columns like Test ID, Test Case, Steps, Expected Result
3. Click **"Validate"**
4. AI analyzes test coverage and identifies:
   - Missing test scenarios
   - Gaps in coverage
   - Recommendations for improvement
5. Results appear in the chat window with detailed analysis

### 4. Generate API Automation Scripts

1. Click **"API Automation"** tab
2. Paste a Swagger/OpenAPI specification URL
   - Example: `https://petstore.swagger.io/v2/swagger.json`
3. Click **"Generate Script"**
4. Review the generated Python script with:
   - API client class
   - Methods for each endpoint
   - Request parameters and authentication
   - Example usage
5. **Download** the script or **Copy to Clipboard**
6. Script appears in chat window for reference

**Generated Script Features:**
- Production-ready Python code
- Requests library integration
- Error handling
- Type hints
- Docstrings
- Example usage

### 5. Export Results

**Copy to Clipboard:**
- Click the copy icon next to any response

**Download as Text:**
- Click the download icon next to responses

**Export as Excel (Table Responses):**
- When a response contains table data, an Excel icon appears
- Click to download as .xlsx file with proper formatting
- Multi-table responses create multiple sheets
- Auto-adjusts column widths

**Export as PDF:**
- Use the `/api/export/pdf` endpoint (via API)

**Export as Excel (API):**
- Use the `/api/export/excel` endpoint (via API)

### 6. Manage Documents

**View Documents:**
- See all uploaded documents in the **"My Documents"** panel
- Shows filename, type, and upload date

**Delete Documents:**
- Click the delete icon next to any document (UI feature - may need implementation)

## 🛠️ Technology Stack

### Frontend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **React** | UI framework | 18.3.1 |
| **Vite** | Build tool & dev server | 5.4.11 |
| **Tailwind CSS** | Styling framework | 3.4.17 |
| **ReactMarkdown** | Markdown rendering | Latest |
| **Axios** | HTTP client | 1.7.9 |
| **Lucide React** | Icon library | Latest |
| **React Toastify** | Notifications | Latest |
| **xlsx** | Excel export functionality | ^0.18.5 |

### Backend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **Flask** | REST API framework | 3.0.0 |
| **Flask-CORS** | Cross-origin support | 4.0.0 |
| **ChromaDB** | Vector database | 0.3.21 |
| **LangChain** | Document processing | Latest |
| **numpy** | Numerical operations | 1.26.4 |
| **pandas** | Excel processing | 2.2.0 |
| **Sentence Transformers** | Cross-encoder re-ranking | Latest |
| **Ollama** | Local LLM inference | Latest |
| **OpenAI (Azure)** | Cloud LLM & embeddings | 1.12.0 |
| **PyMuPDF** | PDF processing | 1.24.1 |
| **fpdf2** | PDF generation | 2.7.0 |
| **python-dotenv** | Environment management | 1.0.0 |
| **Waitress** | Production WSGI server | 3.0.0 |
| **PyYAML** | YAML parsing (Swagger) | 6.0.1 |

### Infrastructure
| Component | Purpose |
|-----------|---------|
| **Ollama** | Local LLM service (llama3, mistral, gemma, etc.) |
| **ChromaDB** | Persistent vector storage with cosine similarity |
| **Waitress** | Production-grade WSGI server for Windows |

### Available LLM Models

**Offline (Ollama):**
- `gemma3:1b` — Lightweight, fast (default)
- `llama3.2:3b` — Balanced performance
- `mistral:7b` — High quality
- `deepseek-r1:latest` — Reasoning model
- `qwen3:30b` — Large model for complex tasks

**Online (Azure OpenAI):**
- `gpt-4` — Advanced reasoning
- `gpt-3.5-turbo` — Fast, cost-effective

**Embedding Models:**
- Ollama: `nomic-embed-text:latest` (768 dims)
- Azure: `text-embedding-ada-002` (1536 dims)

## Prerequisites

- **Python 3.11 or 3.12** (both fully supported with compatible dependencies)
- **Node.js 18+** (for frontend development)
- **Ollama** (for local inference)
- **Docker & Docker Compose** (for containerized deployment)
- **OpenAI API Key** (optional, for GPT models)

## 🎨 Customization

### Change LLM Models

Edit [backend/models.py](backend/models.py):

```python
# Available offline models
offline_models = [
    "gemma3:1b",           # Lightweight (default)
    "llama3.2:3b",         # Balanced
    "deepseek-r1:latest",  # Reasoning
    "qwen3:30b",           # Large
    "mistral:7b"           # High quality
]

# Set default model
active_model = offline_models[0]  # Change index to switch default

# Or set specific model
active_model = "mistral:7b"
```

Then restart the backend server.

### Change Embedding Model

**For Ollama:**
```bash
# In backend/.env
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

**For Azure:**
```bash
# In backend/.env
EMBEDDING_PROVIDER=azure
AZURE_EMBEDDING_MODEL=text-embedding-ada-002
```

### Customize UI Theme

Edit [frontend/src/styles/globals.css](frontend/src/styles/globals.css):

```css
:root {
  /* Chat response colors */
  --chat-heading-color: #60a5fa;      /* Blue headings */
  --chat-body-color: #e5e7eb;         /* Gray body text */
  --chat-code-bg: rgba(0, 0, 0, 0.3); /* Code background */
  
  /* Glassmorphism effects */
  --glass-bg: rgba(255, 255, 255, 0.1);
  --glass-border: rgba(255, 255, 255, 0.2);
}
```

### Add New Query Types

1. **Add prompt template** in [backend/prompts.py](backend/prompts.py):
```python
def my_custom_prompt():
    return """Your custom prompt template here..."""
```

2. **Update backend route** in [backend/server.py](backend/server.py):
```python
@app.route("/api/query/rag", methods=["POST"])
def rag_query():
    # Add your query type case
    elif query_type == "my_custom":
        sys_prompt = my_custom_prompt()
```

3. **Add UI button** in [frontend/src/components/QueryChat.jsx](frontend/src/components/QueryChat.jsx):
```jsx
<button onClick={() => setActiveQueryType('my_custom')}>
  My Custom Query
</button>
```

### Customize Document Processing

Edit chunk size and overlap in [backend/models.py](backend/models.py):

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,      # Increase for longer context
    chunk_overlap=100,   # Increase for more context overlap
    separators=["\n\n", "\n", ".", "?", "!", " ", ""],
)
```

### Add New File Types

Edit [backend/server.py](backend/server.py):

```python
ALLOWED_EXTENSIONS = {"pdf", "txt", "xlsx", "xls", "docx"}  # Add docx
```

Then add loader in [backend/models.py](backend/models.py):

```python
from langchain_community.document_loaders import Docx2txtLoader

# In process_document():
elif suffix.lower() == ".docx":
    loader = Docx2txtLoader(temp_file.name)
```

## 🐛 Troubleshooting

### Backend Issues

**Error: "Connection refused to localhost:11434"**
```bash
# Ensure Ollama is running
ollama serve

# Check if Ollama is accessible
curl http://localhost:11434/api/tags
```

**Error: "ModuleNotFoundError: No module named 'flask'"**
```bash
# Activate virtual environment
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements-api.txt
```

**Error: "OSError: [WinError 10038] socket operation on nonsocket"**
- This is a Windows-specific issue with Flask development server
- **Solution 1:** Use the production server
  ```bash
  python server_production.py
  ```
- **Solution 2:** Already fixed in current `server.py` with `threaded=True`
- See [backend/WINDOWS_SOCKET_FIX.md](backend/WINDOWS_SOCKET_FIX.md) for details

**Error: "Azure OpenAI credentials not found"**
```bash
# Check your .env file
cd backend
cat .env  # Linux/Mac
type .env  # Windows

# Verify these are set:
# AZURE_OPENAI_API_KEY=your-key
# AZURE_OPENAI_ENDPOINT=your-endpoint
```

**Error: "The API deployment for this resource does not exist"**
- Verify deployment names in Azure Portal match your `.env`:
  - `AZURE_EMBEDDING_MODEL` should match your embedding deployment name
  - `AZURE_OPENAI_MODEL` should match your chat deployment name

**Documents not being found after switching embedding providers**
- Delete the vector database:
  ```bash
  cd backend
  rm -rf harry-rag-chroma-db  # Linux/Mac
  rmdir /s /q harry-rag-chroma-db  # Windows
  ```
- Restart server
- Re-upload all documents

**Python 3.12 compatibility issues**
- All dependencies in `requirements-api.txt` are now Python 3.12 compatible
- Uses numpy 1.26.4, pandas 2.2.0, chromadb 0.3.21, pymupdf 1.24.1, fpdf2 2.7.0
- If you encounter issues, ensure you're using the latest requirements file

### Frontend Issues

**Error: "Failed to fetch" when accessing API**
- Check backend is running: `curl http://localhost:5000/api/health`
- Verify `VITE_API_URL` in `frontend/.env`
- Check CORS configuration in `backend/server.py`

**Blank page or build errors**
```bash
cd frontend

# Clean install
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite

# Restart dev server
npm run dev
```

**Port 5173 already in use**
```bash
# Vite will automatically use next available port (5174, 5175, etc.)
# Or kill existing process:
# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5173 | xargs kill -9
```

**Excel export not working**
```bash
# Ensure xlsx package is installed
cd frontend
npm install xlsx@^0.18.5

# Restart dev server
npm run dev
```

### Performance Issues

**Slow query responses**
- Use a smaller LLM model: `gemma3:1b` instead of `qwen3:30b`
- Reduce chunk overlap in `backend/models.py`
- Use Azure OpenAI for faster cloud-based inference
- Check available RAM and CPU usage

**Out of memory**
- Reduce model size in Ollama
- Increase system RAM allocation
- Use Azure OpenAI instead of local Ollama

### Database Issues

**ChromaDB errors**
```bash
# Check database integrity
cd backend
python check_db.py

# Reset database if corrupted
rm -rf harry-rag-chroma-db
# Restart server and re-upload documents
```

**Embedding dimension mismatch**
- This happens when switching between embedding providers
- **Solution:** Delete database and re-upload documents
- Ollama embeddings: 768 dimensions
- Azure embeddings: 1536 dimensions

## 📚 Documentation

### Main Documentation
- [README.md](README.md) — This file (project overview & setup)

### Backend Documentation
- [backend/README.md](backend/README.md) — Backend API documentation
- [backend/AZURE_MIGRATION.md](backend/AZURE_MIGRATION.md) — Azure OpenAI migration guide
- [backend/WINDOWS_SOCKET_FIX.md](backend/WINDOWS_SOCKET_FIX.md) — Windows deployment troubleshooting
- [backend/.env.example](backend/.env.example) — Environment variables reference

### Frontend Documentation
- [frontend/README.md](frontend/README.md) — Frontend development guide

## 🗺️ Roadmap

### Planned Features
- [ ] User authentication and multi-tenant support
- [ ] Document versioning and history
- [ ] Advanced analytics and usage metrics
- [ ] Integration with Jira, Azure DevOps, TestRail
- [ ] Collaborative features (shared knowledge bases)
- [ ] Custom model fine-tuning
- [ ] Mobile-responsive PWA
- [ ] Real-time collaboration
- [ ] Plugin/extension system

### Recent Updates
- ✅ **Python 3.12 Support** — Full compatibility with Python 3.11 and 3.12
- ✅ **Excel Export for Tables** — Smart detection and client-side Excel generation using xlsx library
- ✅ **Contextual Help System** — Auto-displayed help on first chat load with all action types
- ✅ **Glass Effect Title** — Centered application title with glassmorphism design
- ✅ **fpdf to fpdf2 Migration** — Modern PDF generation library
- ✅ **ChromaDB Compatibility** — Fixed embedding function compatibility issues
- ✅ **Improved Error Handling** — Better logging and fallback mechanisms
- ✅ Swagger/OpenAPI automation script generator
- ✅ Azure OpenAI embedding support
- ✅ Test case validation with AI analysis
- ✅ Windows production deployment (Waitress)
- ✅ Markdown formatting in chat responses
- ✅ Cross-encoder re-ranking for better retrieval

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow existing code style (PEP 8 for Python, ESLint for JavaScript)
- Add tests for new features
- Update documentation
- Keep commits atomic and well-described

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

## 👨‍💻 Author

**Harry** — Quality Engineering AI Enthusiast

- LinkedIn: [Connect with me](https://linkedin.com)
- GitHub: [EK-QE-AI-SUBMISSION](https://github.com)

## 🙏 Acknowledgments

- **Caltech AI & ML Postgraduate Program** — For the foundation and inspiration
- **Ollama Team** — For making local LLMs accessible
- **LangChain** — For document processing utilities
- **ChromaDB** — For the excellent vector database
- **OpenAI** — For Azure OpenAI services
- **React & Vite** — For modern frontend tooling
- **Open Source Community** — For countless libraries and tools

## 📊 Project Stats

| Metric | Count |
|--------|-------|
| **Frontend Components** | 7 |
| **API Endpoints** | 12 |
| **Backend Files** | 12+ |
| **Supported File Types** | 4 (PDF, TXT, XLSX, XLS) |
| **Query Types** | 5 (QA, Test Cases, Strategy, Risk, Validation) |
| **LLM Models** | 5+ offline, 2 online |
| **Embedding Providers** | 2 (Ollama, Azure) |
| **Python Versions** | 2 (3.11, 3.12) |

## 🌟 Star History

If you find this project helpful, please consider giving it a star ⭐

## 💬 Support

For issues, questions, or feature requests:
- 🐛 [Open an issue](https://github.com/yourusername/EK-QE-AI-SUBMISSION/issues)
- 💬 [Start a discussion](https://github.com/yourusername/EK-QE-AI-SUBMISSION/discussions)
- 📧 Email support

---

**Built with ❤️ for Quality Engineers by Quality Engineers**

**Happy Testing with NexQA.ai! 🚀**
