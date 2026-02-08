"""
Swagger/OpenAPI to Python API Automation Script Generator
Parses OpenAPI specs and generates executable Python automation scripts.
"""
import json
import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin


def fetch_swagger_spec(swagger_url: str) -> Dict[str, Any]:
    """
    Fetch OpenAPI/Swagger specification from URL.
    Supports both JSON and YAML formats.
    """
    try:
        response = requests.get(swagger_url, timeout=10)
        response.raise_for_status()
        
        # Try JSON first
        try:
            return response.json()
        except json.JSONDecodeError:
            # Try YAML
            try:
                import yaml
                return yaml.safe_load(response.text)
            except ImportError:
                # If YAML not available, try treating as JSON again
                raise ValueError("Could not parse OpenAPI spec. Ensure it's valid JSON or YAML.")
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch Swagger URL: {str(e)}")


def generate_python_script(spec: Dict[str, Any], swagger_url: str) -> str:
    """
    Generate a Python API automation script from an OpenAPI specification.
    """
    title = spec.get("info", {}).get("title", "API Client")
    description = spec.get("info", {}).get("description", "Auto-generated API client")
    base_url = spec.get("servers", [{}])[0].get("url", "")
    paths = spec.get("paths", {})
    
    script = f'''#!/usr/bin/env python3
"""
{title}
{description}

Auto-generated API automation script from Swagger/OpenAPI specification.
Generated from: {swagger_url}

Install dependencies:
    pip install requests pytest pytest-cov pyyaml

Run tests:
    pytest {title.lower().replace(" ", "_")}_test.py -v
"""

import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin
import time

class {title.replace(" ", "").replace("-", "")}Client:
    """Client for {title} API"""
    
    def __init__(self, base_url: str = "{base_url}", timeout: int = 30):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.headers = {{"Content-Type": "application/json"}}
    
    def set_auth(self, token: str, auth_type: str = "bearer"):
        """Set authentication token"""
        if auth_type.lower() == "bearer":
            self.headers["Authorization"] = f"Bearer {{token}}"
        else:
            self.headers["Authorization"] = f"{{auth_type}} {{token}}"
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            Response JSON or status info
        """
        url = urljoin(self.base_url, endpoint)
        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("timeout", self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return {{
                "status": response.status_code,
                "data": response.json() if response.content else {{}},
                "headers": dict(response.headers)
            }}
        except requests.exceptions.RequestException as e:
            return {{
                "status": getattr(e.response, "status_code", 0),
                "error": str(e),
                "data": None
            }}
    
    # Auto-generated endpoint methods
'''

    # Generate methods for each endpoint
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                operation_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
                summary = details.get("summary", f"{method.upper()} {path}")
                parameters = details.get("parameters", [])
                request_body = details.get("requestBody", {})
                
                # Build parameter string
                param_list = ["self", "**kwargs"]
                param_doc = ""
                
                for param in parameters:
                    param_name = param.get("name", "param")
                    param_in = param.get("in", "query")
                    param_doc += f"                {param_name}: Parameter to send in {param_in}\n"
                
                if request_body:
                    param_doc += f"                data: Request body data\n"
                
                script += f'''
    def {operation_id}(self, **kwargs):
        """
        {summary}
        
        Args:
{param_doc}        
        Returns:
            Response dictionary with status, data, and headers
        """
        return self._request("{method.upper()}", "{path}", **kwargs)
'''

    # Add example usage and tests
    script += '''

def main():
    """Example usage of the API client"""
    # Initialize client
    client = APIClient(base_url="YOUR_API_BASE_URL")
    
    # Set authentication if needed
    # client.set_auth("your_token_here")
    
    # Example: Make API calls
    # response = client.get_example_endpoint()
    # print(f"Status: {response['status']}")
    # print(f"Data: {response['data']}")


# Test suite
if __name__ == "__main__":
    import unittest
    
    class TestAPIClient(unittest.TestCase):
        """Test cases for API automation"""
        
        @classmethod
        def setUpClass(cls):
            """Set up test fixtures"""
            cls.client = APIClient(base_url="YOUR_TEST_BASE_URL")
        
        def test_client_initialization(self):
            """Test client can be initialized"""
            self.assertIsNotNone(self.client)
            self.assertIn("Content-Type", self.client.headers)
        
        def test_set_auth(self):
            """Test authentication header is set"""
            self.client.set_auth("test_token")
            self.assertIn("Authorization", self.client.headers)
            self.assertIn("Bearer", self.client.headers["Authorization"])
        
        def test_auth_types(self):
            """Test different auth types"""
            self.client.set_auth("token123", "Bearer")
            self.assertEqual(
                self.client.headers["Authorization"],
                "Bearer token123"
            )
    
    # Run tests
    unittest.main()
'''

    return script


def create_api_automation_script(swagger_url: str) -> tuple[str, str]:
    """
    Create a complete Python API automation script from Swagger URL.
    
    Args:
        swagger_url: URL to the OpenAPI/Swagger specification
    
    Returns:
        Tuple of (script_content, filename)
    """
    # Fetch the spec
    spec = fetch_swagger_spec(swagger_url)
    
    # Generate script
    script = generate_python_script(spec, swagger_url)
    
    # Create filename from API title
    title = spec.get("info", {}).get("title", "api_client")
    filename = title.lower().replace(" ", "_") + "_automation.py"
    
    return script, filename
