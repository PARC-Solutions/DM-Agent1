# Tools Overview

## What is a Tool?

In the context of ADK, a Tool represents a specific capability provided to an AI agent, enabling it to perform actions and interact with the world beyond its core text generation and reasoning abilities. What distinguishes capable agents from basic language models is often their effective use of tools.

Technically, a tool is typically a modular code component—like a Python function, a class method, or even another specialized agent—designed to execute a distinct, predefined task. These tasks often involve interacting with external systems or data.

## Key Characteristics

Tools in ADK serve specific purposes such as:

* Querying databases
* Making API requests (e.g., fetching weather data, booking systems)
* Searching the web
* Executing code snippets
* Retrieving information from documents (RAG)
* Interacting with other software or services

**Extends Agent capabilities:** They empower agents to access real-time information, affect external systems, and overcome the knowledge limitations inherent in their training data.

**Execute predefined logic:** Crucially, tools execute specific, developer-defined logic. They do not possess their own independent reasoning capabilities like the agent's core Large Language Model (LLM). The LLM reasons about which tool to use, when, and with what inputs, but the tool itself just executes its designated function.

## How Agents Use Tools

Agents leverage tools dynamically through mechanisms often involving function calling. The process generally follows these steps:

1. **Analysis:** The LLM analyzes the user's request.
2. **Selection:** Based on the analysis, the LLM decides on which tool, if any, to execute, based on the tools available to the agent and the docstrings that describes each tool.
3. **Invocation:** The LLM generates the required arguments (inputs) for the selected tool and triggers its execution.
4. **Observation:** The agent receives the output (result) returned by the tool.
5. **Finalization:** The agent incorporates the tool's output into its ongoing reasoning process to formulate the next response, decide the subsequent step, or determine if the goal has been achieved.

Think of the tools as a specialized toolkit that the agent's intelligent core (the LLM) can access and utilize as needed to accomplish complex tasks.

## Tool Types in ADK

ADK offers flexibility by supporting several types of tools:

### 1. Function Tools

The most basic and commonly used tool type is a simple Python function. These are developer-defined functions that agents can call to perform specific tasks.

```python
def get_weather(city: str) -> dict:
    """Get weather information for a specific city.
    
    Args:
        city: The name of the city to get weather for
        
    Returns:
        dict: Weather information with status and data
    """
    # Implementation details
    return {"status": "success", "temperature": "72°F", "condition": "Sunny"}
```

Learn more: [Function Tools](./2_FunctionTools.md)

### 2. Third-Party Tools

ADK integrates seamlessly with tools from popular frameworks like LangChain and CrewAI.

```python
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import WikipediaQueryRun

# Create a LangChain tool and wrap it for ADK
wiki_tool = LangchainTool(WikipediaQueryRun())
```

Learn more: [Third-Party Tools](./3_ThirdPartyTools.md)

### 3. Google Cloud Tools

ADK provides specialized tools for integrating with Google Cloud services.

```python
from google.adk.tools.vertex import VertexEndpointPredictor
from google.adk.tools.bigquery import BigQueryTool

# Create Google Cloud tools
vertex_tool = VertexEndpointPredictor(project="my-project", endpoint_id="my-endpoint")
bigquery_tool = BigQueryTool(project="my-project")
```

Learn more: [Google Cloud Tools](./4_GoogleCloudTools.md)

### 4. MCP Tools

Model Context Protocol (MCP) tools allow your agents to interact with external services through a standardized protocol.

```python
from google.adk.tools.mcp import MCPTool

weather_tool = MCPTool(
    server_name="weather-service",
    tool_name="get_weather",
    description="Gets current weather information for a location."
)
```

Learn more: [MCP Tools](./5_MCPTools.md)

### 5. OpenAPI Tools

ADK supports generating tools from OpenAPI specifications, allowing quick integration with any API that provides an OpenAPI definition.

```python
from google.adk.tools.openapi import create_openapi_tools

weather_api_tools = create_openapi_tools(
    spec_path="weather_api_openapi.yaml",
    base_url="https://api.weather.com"
)
```

Learn more: [OpenAPI Tools](./6_OpenAPITools.md)

## Authentication for Tools

Many tools require authentication to access external services. ADK supports various authentication methods, from simple API keys to OAuth flows.

```python
from google.adk.tools.http import HTTPTool

# Tool with API key authentication
http_tool = HTTPTool(
    base_url="https://api.example.com",
    headers={"X-API-Key": "your-api-key"}
)
```

Learn more: [Authentication](./7_Authentication.md)

## Best Practices for Tools

When designing and implementing tools for your agents, consider these best practices:

### 1. Clear Documentation

Always provide detailed docstrings for your tools. The LLM uses this information to understand when and how to use the tool.

```python
def calculate_mortgage(principal: float, interest_rate: float, years: int) -> dict:
    """Calculate monthly mortgage payment and amortization details.
    
    This tool calculates the monthly payment amount and provides an amortization
    breakdown for a fixed-rate mortgage loan.
    
    Args:
        principal: The loan amount in dollars
        interest_rate: Annual interest rate as a percentage (e.g., 5.5 for 5.5%)
        years: Term of the loan in years
        
    Returns:
        dict: Contains monthly_payment, total_interest, and amortization_schedule
    """
    # Implementation...
```

### 2. Consistent Return Format

Standardize your tool return values for predictable agent handling:

```python
# Good: Consistent structure with status indicator
return {
    "status": "success",  # or "error"
    "data": {...},        # Main return data
    "message": "..."      # Optional explanation
}

# For errors:
return {
    "status": "error",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded, try again later"
}
```

### 3. Error Handling

Design tools to return structured errors rather than raising exceptions:

```python
def search_database(query: str) -> dict:
    """Search the database for information."""
    try:
        results = db.execute(query)
        return {"status": "success", "results": results}
    except ConnectionError:
        return {
            "status": "error",
            "error_type": "connection_error",
            "message": "Could not connect to database. Please try again later."
        }
    except QuerySyntaxError as e:
        return {
            "status": "error",
            "error_type": "syntax_error",
            "message": f"Invalid query syntax: {str(e)}"
        }
```

### 4. Type Hints

Always use appropriate type hints to help the LLM understand the expected inputs and outputs:

```python
def get_stock_price(
    symbol: str,
    exchange: str = "NASDAQ"
) -> dict:
    """Get current stock price information."""
    # Implementation...
```

### 5. Function Naming

Use clear, descriptive names that indicate what the tool does:

```python
# Good - clear purpose
def translate_text(text: str, target_language: str) -> dict:
    """Translate text to the target language."""
    # Implementation...

# Bad - unclear purpose
def process_text(text: str, lang: str) -> dict:
    """Process the text."""
    # Implementation...
```

## Next Steps

Explore the detailed documentation for each tool type:

- [Function Tools](./2_FunctionTools.md)
- [Third-Party Tools](./3_ThirdPartyTools.md)
- [Google Cloud Tools](./4_GoogleCloudTools.md)
- [MCP Tools](./5_MCPTools.md)
- [OpenAPI Tools](./6_OpenAPITools.md)
- [Authentication](./7_Authentication.md)
