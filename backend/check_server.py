#!/usr/bin/env python3
"""
Server Health Check and Diagnostics
Helps diagnose socket and connection issues on Windows
"""
import requests
import time
import sys

def check_server_health():
    """Check if the server is running and responding"""
    url = "http://localhost:5000/api/health"
    
    print("Checking NexQA Backend Server...")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✓ Server is healthy!")
            print(f"  Response time: {elapsed:.2f}s")
            print(f"  Status: {response.json()}")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server")
        print("  Make sure the server is running on port 5000")
        return False
    except requests.exceptions.Timeout:
        print("✗ Server request timed out")
        print("  Server may be overloaded or stuck")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_llm_endpoint():
    """Test a simple LLM query to check for socket issues"""
    url = "http://localhost:5000/api/query/rag"
    
    print("\nTesting LLM endpoint...")
    print("-" * 50)
    
    try:
        payload = {
            "query": "What is quality assurance?",
            "type": "qa",
            "top_k": 3
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✓ LLM endpoint working!")
            print(f"  Response time: {elapsed:.2f}s")
            return True
        else:
            print(f"✗ LLM endpoint returned status {response.status_code}")
            print(f"  Error: {response.json().get('error', 'Unknown error')}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ LLM request timed out (>60s)")
        print("  This may indicate socket issues or slow LLM processing")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("NexQA Backend Server Diagnostics")
    print("=" * 50)
    print()
    
    # Check basic health
    health_ok = check_server_health()
    
    if health_ok:
        # Only test LLM if server is healthy
        llm_ok = test_llm_endpoint()
        
        print()
        print("=" * 50)
        if health_ok and llm_ok:
            print("✓ All checks passed!")
        else:
            print("✗ Some checks failed")
            print("  Check server logs for details")
        print("=" * 50)
        sys.exit(0 if (health_ok and llm_ok) else 1)
    else:
        print()
        print("=" * 50)
        print("✗ Server health check failed")
        print("  Start the server with: python server.py")
        print("=" * 50)
        sys.exit(1)
