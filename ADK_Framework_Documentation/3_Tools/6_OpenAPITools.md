# OpenAPI Tools

ADK supports generating tools from OpenAPI specifications, allowing you to quickly integrate with any API that provides an OpenAPI definition. This feature dramatically simplifies the process of connecting your agents to third-party services and APIs.

## What is OpenAPI?

The OpenAPI Specification (formerly known as Swagger) is a standardized way to describe RESTful APIs. It provides a machine-readable format that enables automatic generation of documentation, client SDKs, and server stubs.

An OpenAPI specification typically includes:

- API endpoints and operations
- Input and output parameters
- Authentication methods
- Data types and models
- Documentation and examples

## Creating Tools from OpenAPI Specs

ADK makes it easy to turn an OpenAPI specification into agent tools:

```python
from google.adk.agents import Agent
from google.adk.tools.openapi import create_openapi_tools

# Create tools from an OpenAPI specification
weather_api_tools = create_openapi_tools(
    spec_path="path/to/weather_api_openapi.yaml",
    base_url="https://api.weather.com"
)

# Create an agent with the OpenAPI tools
api_agent = Agent(
    name="weather_api_agent",
    model="gemini-2.0-flash",
    instruction="Help users get weather information using the Weather API.",
    tools=weather_api_tools
)
```

The `create_openapi_tools` function processes the OpenAPI specification and generates a set of tools, one for each operation defined in the spec.

## OpenAPI Specification Sources

You can provide an OpenAPI specification in several ways:

### 1. Local File Path

```python
tools = create_openapi_tools(
    spec_path="path/to/api_spec.yaml",
    base_url="https://api.example.com"
)
```

### 2. URL to a Specification

```python
tools = create_openapi_tools(
    spec_url="https://api.example.com/openapi.json",
    base_url="https://api.example.com"
)
```

### 3. Dictionary Object

```python
spec_dict = {
    "openapi": "3.0.0",
    "info": {"title": "Example API", "version": "1.0.0"},
    "paths": {
        "/users": {
            "get": {
                "summary": "Get users",
                "operationId": "getUsers",
                # ...
            }
        }
    }
    # ...
}

tools = create_openapi_tools(
    spec_dict=spec_dict,
    base_url="https://api.example.com"
)
```

## Authentication with OpenAPI Tools

Many APIs require authentication. You can provide authentication information when creating OpenAPI tools:

### API Key Authentication

```python
tools = create_openapi_tools(
    spec_path="path/to/api_spec.yaml",
    base_url="https://api.example.com",
    headers={"X-API-Key": "your-api-key"}
)
```

### Bearer Token Authentication

```python
tools = create_openapi_tools(
    spec_path="path/to/api_spec.yaml",
    base_url="https://api.example.com",
    headers={"Authorization": f"Bearer {token}"}
)
```

### OAuth Authentication

For more complex authentication like OAuth, you might need to set up the token acquisition separately:

```python
from google.adk.tools.oauth import OAuth2Session

# Set up OAuth session
oauth_session = OAuth2Session(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://auth.example.com/token"
)
token = oauth_session.fetch_token()

# Create tools with OAuth authentication
tools = create_openapi_tools(
    spec_path="path/to/api_spec.yaml",
    base_url="https://api.example.com",
    headers={"Authorization": f"Bearer {token['access_token']}"}
)
```

## Example: Integrating with a Pet Store API

Here's a complete example using the popular Pet Store demo API:

```python
from google.adk.agents import Agent
from google.adk.tools.openapi import create_openapi_tools

# Create tools from the Pet Store API specification
petstore_tools = create_openapi_tools(
    spec_url="https://petstore.swagger.io/v2/swagger.json",
    base_url="https://petstore.swagger.io/v2"
)

# Create an agent with the Pet Store API tools
pet_agent = Agent(
    name="pet_store_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are a pet store assistant that can help users:
    - Find pets by status (available, pending, sold)
    - Get pet details by ID
    - Update pet information
    - Place orders for pets
    
    Use the appropriate API endpoints based on the user's request.
    """,
    tools=petstore_tools
)

# Example usage
response = pet_agent.run("Show me all available pets")
print(response.text)
```

## Customization Options

The `create_openapi_tools` function supports several customization options:

```python
tools = create_openapi_tools(
    spec_path="path/to/api_spec.yaml",
    base_url="https://api.example.com",
    headers={"X-API-Key": "your-api-key"},
    operation_ids=["getUsers", "createUser"],  # Only include specific operations
    exclude_operation_ids=["deleteUser"],  # Exclude specific operations
    tool_name_prefix="api_",  # Prefix for generated tool names
    timeout=30,  # Request timeout in seconds
    validate_schema=True  # Validate response against OpenAPI schema
)
```

## Handling API Responses

When an agent uses an OpenAPI tool, it receives the API response which it can incorporate into its reasoning and response. For example:

```
User: "What pets are available for adoption?"

Agent (thinking): I should use the findPetsByStatus operation from the 
Pet Store API to get available pets.

Agent → OpenAPI Tool: Calls findPetsByStatus(status="available")

API → Agent: Returns [
  {"id": 1, "name": "Doggo", "status": "available", "category": {"name": "Dogs"}},
  {"id": 2, "name": "Kitty", "status": "available", "category": {"name": "Cats"}},
  ...
]

Agent → User: "There are several pets available for adoption. These include:
- Doggo (Dog)
- Kitty (Cat)
Would you like more information about any specific pet?"
```

## Error Handling

OpenAPI tools automatically handle many common API errors, but you can also add your own error handling:

```python
def find_pets_with_error_handling(status: str) -> dict:
    """Find pets by status with custom error handling.
    
    Args:
        status: Status values that need to be considered for filter (available, pending, sold)
        
    Returns:
        dict: Pet information or error details
    """
    try:
        # Assume find_pets_by_status is one of the tools generated by create_openapi_tools
        result = find_pets_by_status(status=status)
        return result
    except Exception as e:
        # Custom error handling
        return {
            "status": "error",
            "message": f"Could not retrieve pets with status '{status}': {str(e)}",
            "suggestion": "Try using one of these statuses: available, pending, sold"
        }

# Create an agent with the error handling wrapper
agent = Agent(
    name="robust_pet_agent",
    model="gemini-2.0-flash",
    tools=[find_pets_with_error_handling]
)
```

## Best Practices for OpenAPI Tools

### 1. Use Well-Documented OpenAPI Specs

Look for APIs with comprehensive OpenAPI specifications that include:
- Clear operation descriptions
- Parameter documentation
- Response schemas
- Examples

### 2. Handle Authentication Securely

Never hardcode API keys or tokens in your application code. Instead:
- Use environment variables
- Implement secure token storage
- Consider using a credential manager

```python
import os

# Load API key from environment variable
api_key = os.environ.get("API_KEY")

tools = create_openapi_tools(
    spec_path="api_spec.yaml",
    base_url="https://api.example.com",
    headers={"X-API-Key": api_key}
)
```

### 3. Implement Token Refresh

For OAuth-based APIs, implement token refresh logic:

```python
from google.adk.tools.oauth import OAuth2Session

oauth_session = OAuth2Session(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://auth.example.com/token",
    refresh_token_url="https://auth.example.com/token",
    auto_refresh_url="https://auth.example.com/token"
)

# This will automatically refresh the token if necessary
token = oauth_session.fetch_token()
```

### 4. Filter Operations

Most APIs have many operations, but your agent might only need a subset. Use operation filtering to keep things focused:

```python
# Only include specific operations
weather_tools = create_openapi_tools(
    spec_path="weather_api.yaml",
    base_url="https://api.weather.com",
    operation_ids=["getCurrentWeather", "getForecast"]
)
```

### 5. Add Context to Your Agent Instructions

Provide clear instructions about how and when to use the API operations:

```python
weather_agent = Agent(
    name="weather_assistant",
    model="gemini-2.0-flash",
    instruction="""
    You help users with weather information.
    
    For current weather use getCurrentWeather with a city parameter.
    For forecasts use getForecast with a city parameter and optional days parameter.
    
    Always confirm the city with the user before making API calls.
    Format temperatures in both Celsius and Fahrenheit.
    """,
    tools=weather_tools
)
```

## Advanced: Creating a Wrapper Class

For complex APIs, you might want to create a wrapper class:

```python
from google.adk.agents import Agent
from google.adk.tools.openapi import create_openapi_tools

class WeatherAPIWrapper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.tools = create_openapi_tools(
            spec_path="weather_api.yaml",
            base_url="https://api.weather.com",
            headers={"X-API-Key": api_key}
        )
        
        # Extract specific tool functions
        self.get_current_weather = next(t for t in self.tools if t.__name__ == "getCurrentWeather")
        self.get_forecast = next(t for t in self.tools if t.__name__ == "getForecast")
    
    def get_weather_for_city(self, city: str) -> dict:
        """Get current weather for a city with error handling.
        
        Args:
            city: City name
            
        Returns:
            dict: Weather information
        """
        try:
            return self.get_current_weather(city=city)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_forecast_for_city(self, city: str, days: int = 5) -> dict:
        """Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days (1-10)
            
        Returns:
            dict: Forecast information
        """
        try:
            return self.get_forecast(city=city, days=days)
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create the wrapper
weather_api = WeatherAPIWrapper(api_key="your-api-key")

# Create an agent with the wrapper methods
agent = Agent(
    name="weather_assistant",
    model="gemini-2.0-flash",
    tools=[weather_api.get_weather_for_city, weather_api.get_forecast_for_city]
)
```

## Conclusion

OpenAPI tools provide a powerful way to connect your agents to external APIs with minimal effort. By leveraging OpenAPI specifications, you can quickly add new capabilities to your agents without writing extensive code to handle API integration details.

Key benefits include:

1. **Rapid Integration**: Quickly add new APIs to your agents
2. **Standardization**: Leverage the widely adopted OpenAPI standard
3. **Comprehensive Coverage**: Automatically generate tools for all endpoints defined in the API spec
4. **Documentation**: Inherit parameter descriptions and other documentation from the OpenAPI spec

For more information on authentication methods for APIs, see the [Authentication](./7_Authentication.md) documentation.
