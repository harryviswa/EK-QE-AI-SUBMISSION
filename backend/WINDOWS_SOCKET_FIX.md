# Windows Socket Error WinError 10038 - Troubleshooting Guide

## Problem
When running the Flask backend server on Windows, you may encounter:
```
OSError: [WinError 10038] An operation was attempted on something that is not a socket
```

This typically happens during long-running LLM operations.

## Root Cause
- Flask's default non-threaded mode can't handle concurrent requests
- Long LLM inference times cause client sockets to timeout and close
- Flask tries to respond on closed sockets, causing the error
- Windows handles socket cleanup differently than Unix systems

## Solutions Applied

### 1. ✅ Enabled Threaded Mode
The server now runs with `threaded=True`:
```python
app.run(host="0.0.0.0", port=5000, threaded=True, use_reloader=False)
```

### 2. ✅ Increased Request Timeout
Extended timeout for long LLM operations:
```python
WSGIRequestHandler.timeout = 300  # 5 minutes
```

### 3. ✅ Added Error Handling
Wrapped LLM calls in try-except blocks to catch and handle errors gracefully.

### 4. ✅ Disabled Reloader
Set `use_reloader=False` to prevent double initialization issues on Windows.

## How to Start the Server Properly

### Option 1: Use the Startup Script (Recommended)
```batch
cd backend
start-server.bat
```

This script:
- Kills any existing server processes
- Activates virtual environment
- Starts the server cleanly
- Shows errors if startup fails

### Option 2: Manual Start
```batch
cd backend

# Kill any existing Python server processes first
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *server.py*"

# Start fresh
python server.py
```

### Option 3: Production Mode with Waitress
For production or testing without socket issues:
```batch
pip install waitress
waitress-serve --port=5000 server:app
```

## Verify Server Health

Run the diagnostic script:
```batch
cd backend
python check_server.py
```

This will:
- Check if server is running
- Test basic endpoints
- Test LLM endpoints
- Report any socket/timeout issues

## Additional Tips

### 1. Close Idle Connections
If you still see socket errors:
- Close all browser tabs connected to the frontend
- Restart the backend server
- Clear browser cache and restart frontend dev server

### 2. Check Port Conflicts
```batch
netstat -ano | findstr :5000
```
If port 5000 is in use, kill the process:
```batch
taskkill /PID <process_id> /F
```

### 3. Monitor LLM Performance
Long LLM calls can cause timeouts. Check logs for:
```
LLM call error: ...
LLM processing failed: ...
```

### 4. Use Frontend Timeout Settings
The frontend is configured with extended timeouts:
- Validation: 300 seconds (5 minutes)
- Swagger generation: 60 seconds
- RAG queries: Default axios timeout

## Frontend Changes (If Needed)

If you still get timeout errors from the frontend, increase client-side timeouts in `frontend/src/api/client.js`:
```javascript
ragQuery: (query, type = 'qa', topK = 5, useReranking = true) =>
  api.post('/query/rag', {
    query,
    type,
    top_k: topK,
    use_reranking: useReranking,
  }, {
    timeout: 300000  // 5 minutes
  }),
```

## Testing the Fix

1. Start the backend server:
   ```batch
   cd backend
   start-server.bat
   ```

2. Check server health:
   ```batch
   python check_server.py
   ```

3. Test validation endpoint (long-running):
   ```batch
   # Upload a test case Excel file via the UI
   # Or use curl:
   curl -X POST -F "file=@testcases.xlsx" http://localhost:5000/api/validate/testcases
   ```

4. Monitor console for errors. You should see:
   ```
   Validation completed successfully
   ```
   Instead of socket errors.

## Still Having Issues?

### Windows Firewall
Check if Windows Firewall is blocking Python:
```batch
netsh advfirewall firewall show rule name=all | findstr Python
```

### Antivirus Software
Some antivirus software blocks socket operations. Add exceptions for:
- `python.exe`
- Your project directory
- Port 5000

### Virtual Environment
Ensure you're using a clean virtual environment:
```batch
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements-api.txt
```

## Alternative: Use Gunicorn on WSL
If issues persist, consider running on Windows Subsystem for Linux (WSL):
```bash
# In WSL
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 server:app
```

## Summary of Changes

| File | Change | Purpose |
|------|--------|---------|
| `server.py` | Added `threaded=True` | Handle concurrent requests |
| `server.py` | Set `WSGIRequestHandler.timeout=300` | Prevent timeout during LLM calls |
| `server.py` | Added try-except around LLM calls | Graceful error handling |
| `server.py` | Added `use_reloader=False` | Prevent double initialization |
| `start-server.bat` | New startup script | Clean server restart |
| `check_server.py` | Health check script | Diagnose issues |

The error should now be resolved. If you continue to see socket errors, use `waitress-serve` (production WSGI server) instead of Flask's development server.
