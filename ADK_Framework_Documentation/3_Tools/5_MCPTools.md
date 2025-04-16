# MCP Tools

## What are MCP Servers?

Model Context Protocol (MCP) servers provide tools and resources to agents, enabling them to access external APIs, databases, or services through a standardized protocol. MCP stands for Model Context Protocol, which is a protocol specification for enabling agents to interact with the outside world in a standardized way.

MCP servers act as intermediaries between your agent and external services, providing a consistent interface for various capabilities. This separation of concerns allows you to:

1. Add new capabilities to your agents without modifying your core agent code
2. Share tools across multiple agents and applications
3. Implement specialized functionality that can be maintained separately

## How MCP Tools Work

MCP tools in ADK communicate with MCP servers that follow the Model Context Protocol specification. Each MCP server can offer multiple tools, each with their own specific capabilities and parameter schemas.

When an agent uses an MCP tool, the following happens:

1. The agent determines it needs to use a specific capability (like weather data)
2. The agent calls the appropriate MCP tool with the required parameters
3. The MCP tool forwards the request to the connected MCP server
4. The MCP server processes the request, often by calling external APIs or services
5. The server returns the result back through the MCP tool to the agent
6. The agent incorporates the result into its reasoning process

## Setting Up MCP Tools

### Basic MCP Tool Setup

To use an MCP tool, you first need to connect to an MCP server and then create tools that reference specific capabilities provided by that server:

```python
from google.adk.agents import Agent
from google.adk.tools.mcp import MCPTool

# Connect to an MCP server providing weather data
weather_tool = MCPTool(
    server_name="weather-service",
    tool_name="get_weather",
    description="Gets current weather information for a location."
)

# Create an agent with the MCP tool
weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    instruction="Help users check the weather for different locations.",
    tools=[weather_tool]
)
```

### Usage with Parameters

MCP tools accept parameters that are passed to the server. The parameters vary depending on the specific tool:

```python
# The agent will use the weather tool like this:
response = weather_agent.run("What's the weather in San Francisco today?")

# Behind the scenes, the agent generates a call like:
# weather_tool.run(location="San Francisco")
```

## Example MCP Tools

MCP tools can provide various functionalities:

### 1. External API Access

```python
# Weather API tool
weather_tool = MCPTool(
    server_name="weather-service",
    tool_name="get_forecast",
    description="Gets weather forecast for a location."
)

# Stock market data tool
stock_tool = MCPTool(
    server_name="finance-service",
    tool_name="get_stock_price",
    description="Gets current stock price information."
)
```

### 2. Database Connections

```python
# Product database tool
product_tool = MCPTool(
    server_name="inventory-service",
    tool_name="search_products",
    description="Searches the product catalog for items matching criteria."
)

# Customer database tool
customer_tool = MCPTool(
    server_name="customer-service",
    tool_name="get_customer_info",
    description="Retrieves customer information given an identifier."
)
```

### 3. File System Access

```python
# Document retrieval tool
document_tool = MCPTool(
    server_name="document-service",
    tool_name="get_document",
    description="Retrieves a document from the company repository."
)
```

### 4. Specialized Computation

```python
# Advanced calculation tool
calculation_tool = MCPTool(
    server_name="math-service",
    tool_name="perform_simulation",
    description="Runs a mathematical simulation with provided parameters."
)
```

## Creating Your Own MCP Server

You can create your own MCP server to expose custom tools for your agents. The simplest way is to use the MCP Server library:

```bash
pip install mcp-server
```

Here's a basic example of creating a custom MCP server:

```python
from mcp_server import MCPServer, Tool

# Define tools
@Tool.define
def get_custom_data(parameter1: str, parameter2: int = 10) -> dict:
    """Get custom data based on parameters.
    
    Args:
        parameter1: The primary search term
        parameter2: Numeric parameter with default value
        
    Returns:
        dict: The requested data
    """
    # Your implementation here
    return {"status": "success", "data": {...}}

# Create and start the server
server = MCPServer()
server.add_tool(get_custom_data)
server.start()
```

Then you can connect your agent to this server:

```python
from google.adk.agents import Agent
from google.adk.tools.mcp import MCPTool

# Connect to your custom MCP server
custom_tool = MCPTool(
    server_name="localhost:5000",  # Default MCP server address
    tool_name="get_custom_data",
    description="Gets custom data based on parameters."
)

# Create an agent with your custom tool
agent = Agent(
    name="custom_data_agent",
    model="gemini-2.0-flash",
    tools=[custom_tool]
)
```

## MCP Server Registration

For production use, you can register MCP servers in a configuration file:

```json
{
  "mcp_servers": [
    {
      "name": "weather-service",
      "url": "https://example.com/mcp/weather",
      "auth": {
        "type": "api_key",
        "api_key": "YOUR_API_KEY"
      }
    },
    {
      "name": "finance-service",
      "url": "https://finance-api.example.com/mcp",
      "auth": {
        "type": "oauth",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET"
      }
    }
  ]
}
```

Then load this configuration in your application:

```python
from google.adk.tools.mcp import load_mcp_config

# Load registered MCP servers
load_mcp_config("path/to/mcp_config.json")

# Now you can reference servers by name
weather_tool = MCPTool(
    server_name="weather-service",  # References the registered server
    tool_name="get_forecast"
)
```

## MCP Resources

In addition to tools (which are functions), MCP servers can also provide resources (which are data sources). Resources can be used as context by the agent:

```python
from google.adk.agents import Agent
from google.adk.tools.mcp import MCPResource

# Access a knowledge base provided by an MCP server
knowledge_resource = MCPResource(
    server_name="knowledge-service",
    resource_uri="/kb/customer-policies"
)

# Create an agent with access to the resource
agent = Agent(
    name="policy_agent",
    model="gemini-2.0-flash",
    instruction=f"""
    You are a customer service agent. 
    Use the following company policies to answer customer questions:
    
    {knowledge_resource.get_content()}
    """,
    tools=[...]
)
```

## Authentication with MCP Servers

MCP servers may require authentication. ADK supports various authentication methods:

### API Key Authentication

```python
from google.adk.tools.mcp import MCPTool, MCPAuth

# Create authentication configuration
auth = MCPAuth.api_key("your-api-key-here")

# Create a tool with authentication
weather_tool = MCPTool(
    server_name="weather-service",
    tool_name="get_forecast",
    auth=auth
)
```

### OAuth Authentication

```python
from google.adk.tools.mcp import MCPTool, MCPAuth

# Create OAuth authentication
auth = MCPAuth.oauth(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://auth.example.com/token"
)

# Create a tool with OAuth authentication
finance_tool = MCPTool(
    server_name="finance-service",
    tool_name="get_portfolio",
    auth=auth
)
```

## Error Handling with MCP Tools

When using MCP tools, you should handle potential errors:

```python
def get_weather_safely(location: str) -> dict:
    """Get weather information with proper error handling.
    
    Args:
        location: The location to get weather for
        
    Returns:
        dict: Weather information or error details
    """
    try:
        # Use the MCP tool
        result = weather_tool.run(location=location)
        return result
    except ConnectionError:
        # Handle connection issues
        return {
            "status": "error",
            "error_type": "connection_error",
            "message": "Could not connect to the weather service. Please try again later."
        }
    except Exception as e:
        # Handle other errors
        return {
            "status": "error",
            "error_type": "general_error",
            "message": f"An error occurred: {str(e)}"
        }

# Create an agent with the error-handling wrapper
agent = Agent(
    name="robust_weather_agent",
    model="gemini-2.0-flash",
    tools=[get_weather_safely]
)
```

## Best Practices for MCP Tools

1. **Tool Schema Documentation**: Ensure your MCP tools have clear descriptions and parameter documentation so agents understand when and how to use them.

2. **Error Handling**: Implement proper error handling for MCP tool calls, considering network issues, authentication problems, and server errors.

3. **Resource Management**: For long-running agent processes, implement connection pooling and resource cleanup for MCP server connections.

4. **Authentication Security**: Store authentication credentials securely and never hardcode them in your application code.

5. **Versioning**: Include version information when registering MCP servers to handle API changes gracefully.

6. **Fallback Mechanisms**: For critical functionality, consider providing alternative implementations if an MCP server becomes unavailable.

7. **Monitoring**: Implement logging and monitoring for MCP tool calls to track usage and identify issues.

## Conclusion

MCP tools provide a flexible and standardized way to extend your agents' capabilities through external services. By leveraging the Model Context Protocol, you can maintain a clean separation between your agent logic and the external services it needs to access.

This approach allows you to:
- Add new capabilities to your agents without modifying core code
- Share tools across multiple agents
- Maintain specialized functionality separately from your agent code
- Connect to third-party services through a consistent interface

As the MCP ecosystem grows, more pre-built servers will become available, further expanding the capabilities you can easily add to your agents.
