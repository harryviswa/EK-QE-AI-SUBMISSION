# Backend API Documentation

This directory contains the Flask REST API backend for NexQA.ai.

## Features

- **Flask REST API** with CORS support
- **Document Processing** - PDF, TXT, XLSX file handling
- **Vector Store Management** - ChromaDB integration
- **RAG Pipeline** - Retrieval, re-ranking, and LLM inference
- **Export Functions** - PDF and Excel generation
- **Health Checks** - Monitoring and diagnostics

## Directory Structure

```
backend/
├── server.py            # Flask API server & routes
├── models.py            # Document processing & RAG logic
├── prompts.py           # LLM prompt templates
├── utils.py             # Utility functions (PDF, Excel)
├── requirements.txt     # Core dependencies
├── requirements-api.txt # Flask API dependencies
├── Dockerfile           # Docker container definition
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Setup

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt

# Create .env file
cp .env.example .env

# Start Ollama (in another terminal)
ollama serve

# Run Flask server
python server.py
```

Server runs on http://localhost:5000

### Docker

```bash
docker build -t nexqa-backend .
docker run -p 5000:5000 -v $(pwd)/harry-rag-chroma-db:/app/data/harry-rag-chroma-db nexqa-backend
```

## API Routes

### Health & Info
```
GET  /api/health           - Health check
GET  /api/info             - API info & available models
```

### Document Management
```
POST /api/documents/upload - Upload document (PDF, TXT, XLSX, XLS)
POST /api/documents/add-url - Add web page as knowledge source
GET  /api/documents/list   - List user's documents
```

### Query & RAG
```
POST /api/query/search     - Semantic search in vector store
POST /api/query/rag        - RAG query with LLM response
```

### Export
```
POST /api/export/pdf       - Export as PDF
POST /api/export/excel     - Export as Excel
```

## Request Headers

All requests should include:
```
X-User-ID: <user_id>      # Generated if not provided
Content-Type: application/json
```

## Response Format

All responses follow this format:

```json
{
  "message": "Success message",
  "data": { /* response data */ }
}
```

Or on error:

```json
{
  "error": "Error message"
}
```

## Configuration

### Environment Variables

```env
FLASK_ENV=production              # development or production
CHROMA_DB_PATH=./harry-rag-chroma-db
OPENAI_API_KEY=sk-...            # Optional
AZURE_OPENAI_ENDPOINT=...        # Optional
AZURE_OPENAI_KEY=...             # Optional
OLLAMA_HOST=http://localhost:11434
```

### Customization

#### Change Default Model
Edit `models.py`:
```python
offline_models = ["mistral:7b", "neural-chat", ...]
active_model = offline_models[0]
```

#### Add New Prompt Template
Edit `prompts.py`:
```python
my_custom_prompt = """Your prompt template here"""
```

Then use in `server.py`:
```python
prompt_templates = {
    "custom": my_custom_prompt,
    ...
}
```

## Dependencies

### Core (requirements.txt)
- langchain - Document processing
- chromadb - Vector database
- sentence-transformers - Cross-encoder re-ranking
- ollama - Local LLM inference
- openai - OpenAI API client
- pandas - Data processing
- openpyxl - Excel support
- fpdf - PDF generation

### API (requirements-api.txt)
- flask - Web framework
- flask-cors - CORS support
- python-dotenv - Environment management
- requests - HTTP client

## Examples

### Upload Document
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "X-User-ID: user123" \
  -F "file=@document.pdf"
```

### Query with RAG
```bash
curl -X POST http://localhost:5000/api/query/rag \
  -H "X-User-ID: user123" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the test cases?",
    "type": "testcase",
    "top_k": 5,
    "use_reranking": true
  }'
```

### List Documents
```bash
curl -X GET http://localhost:5000/api/documents/list \
  -H "X-User-ID: user123"
```

## Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check connectivity: `curl http://localhost:11434`
- Verify `OLLAMA_HOST` environment variable

### Out of Memory
- Use smaller model: `ollama pull mistral:7b`
- Reduce `chunk_size` in `models.py`
- Increase system RAM or Docker memory allocation

### CORS Issues
- Check `CORS(app)` in `server.py`
- Verify frontend URL matches CORS configuration
- Check browser console for specific CORS errors

### File Upload Failures
- Check file size (max 50MB)
- Ensure proper file format (PDF, TXT, XLSX, XLS)
- Verify `uploads/` directory exists and is writable

## Performance Tips

1. **Model Selection** - Smaller models (7B) are faster than 70B
2. **Chunk Size** - Balance between context and speed (default: 800 tokens)
3. **Top-K** - Limit retrieval results (default: 5)
4. **Re-ranking** - Disable for faster responses, enable for quality
5. **Caching** - Cache frequently queried documents

## Monitoring

Check health and metrics:

```bash
# Health check
curl http://localhost:5000/api/health

# API info
curl http://localhost:5000/api/info
```

Response:
```json
{
  "name": "NexQA.ai Backend",
  "version": "1.0.0",
  "available_models": ["mistral:7b", ...],
  "active_model": "mistral:7b"
}
```

---

For more information, see the [main README.md](../README.md)
