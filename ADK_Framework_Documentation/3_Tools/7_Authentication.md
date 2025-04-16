# Authentication

Proper authentication is crucial when your agent tools need to access secure resources or APIs. This document covers the authentication options available in ADK and best practices for implementing them securely.

## Authentication Types

ADK supports various authentication methods to connect your tools to external services:

1. **API Key Authentication**: Simple key-based authentication
2. **Bearer Token Authentication**: Token-based authentication
3. **OAuth Authentication**: Complete OAuth 2.0 flow with token refresh
4. **Basic Authentication**: Username and password
5. **Custom Authentication**: Implement specialized authentication schemes

## API Key Authentication

The simplest form of authentication is using API keys. This method is commonly used by many services like Google APIs, weather APIs, and other third-party services.

```python
from google.adk.agents import Agent
from google.adk.tools.http import HTTPTool

# Create an HTTP tool with API key authentication
http_tool = HTTPTool(
    base_url="https://api.example.com",
    headers={"X-API-Key": "your-api-key"}
)

# Create an agent with the authenticated tool
api_agent = Agent(
    name="api_agent",
    model="gemini-2.0-flash",
    instruction="Interact with the Example API to retrieve and update information.",
    tools=[http_tool]
)
```

### Security Best Practices for API Keys

1. **Environment Variables**: Store API keys in environment variables, not in code

```python
import os

api_key = os.environ.get("API_KEY")
http_tool = HTTPTool(
    base_url="https://api.example.com",
    headers={"X-API-Key": api_key}
)
```

2. **Key Rotation**: Implement a process for regularly rotating API keys
3. **Scope Limitation**: Use keys with the minimum required permissions

## OAuth Authentication

For more complex authentication flows like OAuth 2.0:

```python
from google.adk.agents import Agent
from google.adk.tools.oauth import OAuth2Session, OAuth2Tool

# Set up OAuth authentication
oauth_session = OAuth2Session(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorization_endpoint="https://auth.example.com/authorize",
    token_endpoint="https://auth.example.com/token",
    scopes=["read", "write"]
)

# Create an OAuth tool that will handle token management
oauth_tool = OAuth2Tool(
    session=oauth_session,
    base_url="https://api.example.com"
)

# Create functions that use the OAuth tool
def get_user_data() -> dict:
    """Get the current user's data."""
    return oauth_tool.request("GET", "/users/me")

def update_user_profile(name: str, email: str) -> dict:
    """Update the user's profile information."""
    return oauth_tool.request("PATCH", "/users/me", json={"name": name, "email": email})

# Create an agent with the OAuth-authenticated functions
oauth_agent = Agent(
    name="oauth_agent",
    model="gemini-2.0-flash",
    instruction="Securely access and modify user data through the authenticated API.",
    tools=[get_user_data, update_user_profile]
)
```

### Token Refresh

The `OAuth2Session` class automatically handles token refresh when tokens expire:

```python
oauth_session = OAuth2Session(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_endpoint="https://auth.example.com/token",
    refresh_token_url="https://auth.example.com/token",  # URL for refreshing tokens
    auto_refresh=True  # Enable automatic token refresh
)
```

### Interactive OAuth Flow

For scenarios requiring user interaction (like web applications):

```python
from google.adk.tools.oauth import OAuth2Session

# Create the OAuth session
oauth_session = OAuth2Session(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorization_endpoint="https://auth.example.com/authorize",
    token_endpoint="https://auth.example.com/token",
    redirect_uri="http://localhost:8080/callback",
    scopes=["profile", "email"]
)

# Get the authorization URL
auth_url = oauth_session.get_authorization_url()
print(f"Please visit this URL to authorize the application: {auth_url}")

# After the user authorizes and is redirected, capture the authorization code
auth_code = input("Enter the authorization code from the redirect URL: ")

# Exchange the code for tokens
tokens = oauth_session.fetch_token(code=auth_code)

# Now you can use the session for authenticated requests
```

## Basic Authentication

For services using username and password authentication:

```python
from google.adk.agents import Agent
from google.adk.tools.http import HTTPTool
import base64

# Create credentials
username = "your-username"
password = "your-password"
auth_header = f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"

# Create an HTTP tool with Basic authentication
http_tool = HTTPTool(
    base_url="https://api.example.com",
    headers={"Authorization": auth_header}
)

# Create an agent with the authenticated tool
basic_auth_agent = Agent(
    name="basic_auth_agent",
    model="gemini-2.0-flash",
    tools=[http_tool]
)
```

## Google Cloud Authentication

For Google Cloud services, ADK leverages Application Default Credentials:

```python
# Set up Google Cloud authentication
# This uses the environment's Application Default Credentials
import google.auth

credentials, project = google.auth.default()

# These credentials are used automatically by Google Cloud tools
from google.adk.tools.storage import GCSFileTool

storage_tool = GCSFileTool(credentials=credentials)

# Create an agent with Google Cloud authentication
cloud_agent = Agent(
    name="cloud_storage_agent",
    model="gemini-2.0-flash",
    instruction="Help users manage files in Google Cloud Storage.",
    tools=[storage_tool]
)
```

### Service Account Authentication

For production deployments, use service account authentication:

```python
from google.oauth2 import service_account
from google.adk.tools.bigquery import BigQueryTool

# Load service account credentials
credentials = service_account.Credentials.from_service_account_file(
    'path/to/service-account-key.json'
)

# Create a tool with these credentials
bq_tool = BigQueryTool(
    project="your-gcp-project",
    credentials=credentials
)
```

## Custom Authentication

For specialized authentication schemes, you can implement a custom solution:

```python
import time
import hmac
import hashlib
import base64

def create_hmac_signature(key, message):
    """Create an HMAC signature for API authentication."""
    key_bytes = key.encode('utf-8')
    message_bytes = message.encode('utf-8')
    signature = hmac.new(key_bytes, message_bytes, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

def call_custom_auth_api(endpoint: str, params: dict) -> dict:
    """Call an API with custom HMAC authentication.
    
    Args:
        endpoint: API endpoint to call
        params: Query parameters
        
    Returns:
        dict: API response
    """
    import requests
    
    # Authentication details
    api_key = "your-api-key"
    api_secret = "your-api-secret"
    
    # Create timestamp for the request
    timestamp = str(int(time.time()))
    
    # Create message to sign
    message = f"{endpoint}{timestamp}"
    
    # Generate signature
    signature = create_hmac_signature(api_secret, message)
    
    # Prepare headers
    headers = {
        "X-API-Key": api_key,
        "X-Timestamp": timestamp,
        "X-Signature": signature
    }
    
    # Make the request
    response = requests.get(
        f"https://api.example.com{endpoint}",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.text
        }

# Create an agent with the custom authenticated function
agent = Agent(
    name="custom_auth_agent",
    model="gemini-2.0-flash",
    tools=[call_custom_auth_api]
)
```

## MCP Server Authentication

When working with MCP servers, you can configure authentication:

```python
from google.adk.tools.mcp import MCPTool, MCPAuth

# API Key authentication
auth = MCPAuth.api_key("your-api-key")
weather_tool = MCPTool(
    server_name="weather-service",
    tool_name="get_weather",
    auth=auth
)

# OAuth authentication
oauth_auth = MCPAuth.oauth(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://auth.example.com/token"
)
finance_tool = MCPTool(
    server_name="finance-service",
    tool_name="get_portfolio",
    auth=oauth_auth
)
```

## OpenAPI Tools Authentication

When generating tools from OpenAPI specifications, you can include authentication:

```python
from google.adk.tools.openapi import create_openapi_tools

# Create tools with API key authentication
tools = create_openapi_tools(
    spec_path="path/to/api_spec.yaml",
    base_url="https://api.example.com",
    headers={"X-API-Key": "your-api-key"}
)

# OAuth bearer token
tools = create_openapi_tools(
    spec_path="path/to/api_spec.yaml",
    base_url="https://api.example.com",
    headers={"Authorization": f"Bearer {access_token}"}
)
```

## Authentication in Production Environments

For production deployments, consider these additional best practices:

### 1. Secrets Management

Use a secure secrets management solution:

```python
# Example using a hypothetical secrets manager
from your_secrets_manager import SecretsManager

secrets = SecretsManager()
api_key = secrets.get("API_KEY")
```

### 2. Separate Development and Production Credentials

```python
import os

# Determine environment
environment = os.environ.get("ENVIRONMENT", "development")

if environment == "production":
    api_key = secrets_manager.get("PROD_API_KEY")
    base_url = "https://api.example.com"
else:
    api_key = os.environ.get("DEV_API_KEY")
    base_url = "https://dev-api.example.com"
```

### 3. Implement Proper Error Handling

```python
def call_authenticated_api(param: str) -> dict:
    """Call API with proper error handling for authentication issues."""
    try:
        result = api_tool.request("/endpoint", params={"param": param})
        return result
    except AuthenticationError:
        # Handle authentication failures
        refresh_credentials()  # Attempt to refresh credentials
        try:
            result = api_tool.request("/endpoint", params={"param": param})
            return result
        except:
            return {"status": "error", "message": "Authentication failed. Please try again later."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### 4. Implement Proper Logging (Without Credentials)

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_api(endpoint: str) -> dict:
    """Call API with proper logging."""
    try:
        logger.info(f"Calling API endpoint: {endpoint}")
        # Don't log the actual headers with credentials!
        result = api_tool.request(endpoint)
        logger.info(f"API call successful: {endpoint}")
        return result
    except Exception as e:
        logger.error(f"API call failed: {endpoint}, Error: {str(e)}")
        return {"status": "error", "message": str(e)}
```

## Security Best Practices

When implementing authentication in your agent tools:

1. **Never hardcode credentials** in your source code.
2. **Use environment variables** or secure credential stores.
3. **Implement the principle of least privilege** by requesting only the permissions your agent needs.
4. **Rotate credentials** regularly, especially for production deployments.
5. **Audit tool access** to monitor and detect potential security issues.
6. **Use HTTPS/TLS** for all communication with authentication servers and APIs.
7. **Implement rate limiting** to prevent abuse of authenticated endpoints.
8. **Consider using credential rotation** for long-lived deployments.

## Conclusion

Choosing the right authentication method depends on your specific use case and the requirements of the external service you're connecting to. ADK provides flexible options to handle various authentication schemes while maintaining security best practices.

For more advanced authentication scenarios, consider implementing a dedicated authentication service or leveraging identity management platforms integrated with your agent deployment.
