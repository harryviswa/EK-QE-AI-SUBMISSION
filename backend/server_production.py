#!/usr/bin/env python3
"""
Production WSGI server for NexQA Backend using Waitress
Recommended for Windows to avoid socket errors
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app
from server import app

if __name__ == "__main__":
    try:
        from waitress import serve
        
        host = "0.0.0.0"
        port = 5000
        threads = 4
        
        print("=" * 60)
        print("Starting NexQA Backend with Waitress (Production Server)")
        print("=" * 60)
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Threads: {threads}")
        print(f"URL: http://localhost:{port}")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print()
        
        # Start Waitress WSGI server
        serve(
            app,
            host=host,
            port=port,
            threads=threads,
            connection_limit=1000,
            channel_timeout=300,  # 5 minutes for long LLM operations
            cleanup_interval=30,
            asyncore_use_poll=True  # Better for Windows
        )
        
    except ImportError:
        print("ERROR: Waitress is not installed")
        print("Install it with: pip install waitress")
        print()
        print("Falling back to Flask development server...")
        print()
        app.run(host="0.0.0.0", port=5000, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
