# Tools

## What are Tools?

In the Agent Development Kit (ADK), **Tools** represent specific capabilities provided to an AI agent, enabling it to perform actions and interact with the world beyond its core text generation and reasoning abilities. Tools extend agents with functionality such as:

- Querying databases
- Making API requests
- Searching the web
- Executing code snippets
- Retrieving information from documents
- Interacting with other software or services

What distinguishes capable agents from basic language models is often their effective use of tools to overcome the knowledge limitations inherent in their training data.

## How Tools Work

Technically, a tool is a modular code component—like a Python function, a class method, or even another specialized agent—designed to execute a distinct, predefined task.

### Key Characteristics of Tools

- **Predefined Logic**: Tools execute specific, developer-defined logic. They do not possess their own independent reasoning capabilities like the agent's core LLM.
- **Input/Output Contract**: Tools have clearly defined inputs (parameters) and outputs (return values).
- **Self-Description**: Tools provide metadata (via docstrings and type hints) that help the agent understand when and how to use them.
- **External Integration**: Many tools serve as bridges to external services, APIs, or data sources.

## How Agents Use Tools

Agents leverage tools dynamically through a process involving:

1. **Analysis**: The LLM analyzes the user's request and determines if a tool is needed.
2. **Selection**: The LLM selects the appropriate tool based on the tools' descriptions.
3. **Invocation**: The LLM generates the required arguments for the selected tool and triggers its execution.
4. **Observation**: The agent receives the output returned by the tool.
5. **Response Formulation**: The agent incorporates the tool's output into its ongoing reasoning process to formulate the next response.

Here's a simplified example of how this works in practice:

```
User: "What's the weather in New York today?"

Agent (thinking): This is asking about current weather in New York.
I should use the get_weather tool.

Agent → Tool: Calls get_weather("New York")

Tool → Agent: Returns {"status": "success", "report": "Sunny, 75°F"}

Agent → User: "The weather in New York today is sunny with a temperature of 75°F."
```

## Creating Basic Tools

The simplest way to create a tool in ADK is to define a Python function with type hints and a detailed docstring:

```python
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.
    
    Args:
        city (str): The name of the city for which to retrieve the weather report.
        
    Returns:
        dict: status and result or error message.
    """
    # Tool implementation...
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "Sunny, 75°F"
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available."
        }
```

### Key Elements of a Good Tool

1. **Descriptive Name**: The function name should clearly indicate what the tool does.
2. **Type Hints**: Proper type annotations help the agent understand input/output types.
3. **Comprehensive Docstring**: Detailed description, parameter documentation, and return value information.
4. **Error Handling**: Return structured errors rather than raising exceptions.
5. **Consistent Return Format**: Standardized return structure with status indicators.

## Providing Tools to Agents

Once you've defined your tools, you can provide them to an agent:

```python
from google.adk.agents import Agent

# Define your tools
def get_weather(city: str) -> dict:
    """Weather tool implementation..."""
    # Implementation as shown above

def get_time(city: str) -> dict:
    """Time tool implementation..."""
    # Implementation here

# Create an agent with tools
agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description="An agent that provides weather and time information",
    tools=[get_weather, get_time]  # List of tools provided to the agent
)
```

## Tool Types in ADK

ADK supports several types of tools:

### 1. Function Tools

The most common type of tools are simple Python functions, as shown above. These are perfect for quick implementation of custom capabilities.

### 2. Agent-as-Tool

You can use one agent as a tool for another agent, enabling hierarchical agent structures:

```python
from google.adk.agents import Agent
from google.adk.tools.agent_as_tool import create_agent_tool

# Create a specialized agent
weather_specialist = Agent(
    name="weather_specialist",
    model="gemini-2.0-flash",
    description="Expert on weather patterns and forecasts"
)

# Convert it to a tool for use by another agent
weather_tool = create_agent_tool(
    agent=weather_specialist,
    name="ask_weather_expert",
    description="Consult a weather specialist for detailed weather information"
)

# Create a main agent that can use the weather specialist
main_agent = Agent(
    name="assistant",
    model="gemini-2.0-flash",
    description="General assistant that can answer various questions",
    tools=[weather_tool]  # The weather specialist is now a tool
)
```

### 3. Built-in Tools

ADK provides several ready-to-use tools for common tasks:

```python
from google.adk.agents import Agent
from google.adk.tools.google_search import GoogleSearch
from google.adk.tools.code_execution import PythonExecutor

# Create instances of built-in tools
search_tool = GoogleSearch(api_key="YOUR_API_KEY", cse_id="YOUR_CSE_ID")
code_tool = PythonExecutor()

# Create an agent with these tools
advanced_agent = Agent(
    name="advanced_assistant",
    model="gemini-2.0-flash",
    description="Assistant that can search the web and execute Python code",
    tools=[search_tool, code_tool]
)
```

### 4. Third-Party Tools

ADK can integrate tools from other frameworks like LangChain and CrewAI:

```python
from google.adk.agents import Agent
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper

# Create a LangChain tool
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

# Wrap it for use with ADK
wrapped_wiki = LangchainTool(wikipedia)

# Create an agent with the wrapped tool
info_agent = Agent(
    name="info_agent",
    model="gemini-2.0-flash",
    description="Agent that can answer questions using Wikipedia",
    tools=[wrapped_wiki]
)
```

## Best Practices for Tool Design

1. **Single Responsibility**: Each tool should do one thing well.
2. **Clear Documentation**: Provide comprehensive docstrings so the agent knows when and how to use the tool.
3. **Robust Error Handling**: Return structured error information rather than raising exceptions.
4. **Input Validation**: Validate inputs to prevent errors during execution.
5. **Reasonable Defaults**: Provide sensible default values for optional parameters.
6. **Consistent Return Structure**: Standardize return formats across your tools.

## Additional Tool Topics

For more detailed information on specific tool types and advanced usage, see:

- [Tools Overview](../3_Tools/1_ToolsOverview.md)
- [Function Tools](../3_Tools/2_FunctionTools.md)
- [Third-Party Tools](../3_Tools/3_ThirdPartyTools.md)
- [Google Cloud Tools](../3_Tools/4_GoogleCloudTools.md)
- [MCP Tools](../3_Tools/5_MCPTools.md)
- [OpenAPI Tools](../3_Tools/6_OpenAPITools.md)
- [Authentication](../3_Tools/7_Authentication.md)
