# Agent Development Kit (ADK)

## Overview

An open-source AI agent framework integrated with Gemini and Google

## What is Agent Development Kit?

Agent Development Kit (ADK) is a flexible and modular framework for developing and deploying AI agents. ADK can be used with popular LLMs and open-source generative AI tools and is designed with a focus on tight integration with the Google ecosystem and Gemini models. ADK makes it easy to get started with simple agents powered by Gemini models and Google AI tools while providing the control and structure needed for more complex agent architectures and orchestration.

### Get started:

```
pip install google-adk
```

## Key Features

### Flexible Orchestration

Define workflows using workflow agents (Sequential, Parallel, Loop) for predictable pipelines, or leverage LLM-driven dynamic routing (LLMAgent transfer) for adaptive behavior.

[Learn about agents]

### Multi-Agent Architecture

Build modular and scalable applications by composing multiple specialized agents in a hierarchy. Enable complex coordination and delegation.

[Explore multi-agent systems]

### Rich Tool Ecosystem

Access a growing ecosystem of ready-to-use pre-built tools (Search, Code Exec), create custom functions, integrate 3rd-party libraries (LangChain, CrewAI), or even use other agents as tools.

[Browse tools]

### Deployment Ready

Deploy your agents to run seamlessly anywhere – run locally, scale with Vertex AI Agent Engine, or integrate into custom infrastructure using Cloud Run or Docker.

[Deploy agents]

### Built-in Evaluation

Systematically assess agent performance by evaluating both the final response quality and the step-by-step execution trajectory against predefined test cases.

[Evaluate agents]

### Building Responsible Agents

Learn how to building powerful and trustworthy agents by implementing responsible AI patterns and best practices into your agent's design.

[Responsible agents]

---

*Preview*

This feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

# Get Started

## Get Started Overview

Agent Development Kit (ADK) is designed to empower developers to build, manage, evaluate and deploy AI-powered agents. It provides a robust and flexible environment for creating both conversational and non-conversational agents, capable of handling complex tasks and workflows.

## Installation

### Create & activate virtual environment

We recommend creating a virtual Python environment using venv:

```bash
python -m venv .venv
```

Now, you can activate the virtual environment using the appropriate command for your operating system and environment:

```bash
# Mac / Linux
source .venv/bin/activate

# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1
```

### Install ADK

```bash
pip install google-adk
```

(Optional) Verify your installation:

```bash
pip show google-adk
```

### Next steps

Try creating your first agent with the Quickstart

## Quickstart

This quickstart guides you through installing the Agent Development Kit (ADK), setting up a basic agent with multiple tools, and running it locally either in the terminal or in the interactive, browser-based dev UI.

This quickstart assumes a local IDE (VS Code, PyCharm, etc.) with Python 3.9+ and terminal access. This method runs the application entirely on your machine and is recommended for internal development.

### 1. Set up Environment & Install ADK

Create & Activate Virtual Environment (Recommended):

```bash
# Create
python -m venv .venv
# Activate (each new terminal)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

Install ADK:

```bash
pip install google-adk
```

### 2. Create Agent Project

#### Project structure

You will need to create the following project structure:

```
parent_folder/
    multi_tool_agent/
        __init__.py
        agent.py
        .env
```

Create the folder `multi_tool_agent`:

```bash
mkdir multi_tool_agent/
```

#### __init__.py

Now create an `__init__.py` file in the folder:

```bash
echo "from . import agent" > multi_tool_agent/__init__.py
```

Your `__init__.py` should now look like this:

```python
from . import agent
```

#### agent.py

Create an `agent.py` file in the same folder:

```bash
touch multi_tool_agent/agent.py
```

Copy and paste the following code into `agent.py`:

```python
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.
    
    Args:
        city (str): The name of the city for which to retrieve the weather report.
        
    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (41 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available."
        }

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.
    
    Args:
        city (str): The name of the city for which to retrieve the time.
        
    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}."
        }
    
    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    return {"status": "success", "report": report}

root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)
```

#### .env

Create a `.env` file in the same folder:

```bash
touch multi_tool_agent/.env
```

More instructions about this file are described in the next section on Set up the model.

### 3. Set up the model

Your agent's ability to understand user requests and generate responses is powered by a Large Language Model (LLM). Your agent needs to make secure calls to this external LLM service, which requires authentication credentials. Without valid authentication, the LLM service will deny the agent's requests, and the agent will be unable to function.

1. Get an API key from [Google AI Studio](https://ai.google.dev/).

2. Open the `.env` file located inside (`multi_tool_agent/`) and copy-paste the following code.

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
```

3. Replace `GOOGLE_API_KEY` with your actual `API KEY`.

## Quickstart (streaming)

The streaming quickstart builds on the standard quickstart, showing you how to implement streaming responses from your agent, which provides a more engaging and interactive user experience.

### 1. Set up Environment & Create Project Structure

Follow the same initial steps as in the standard quickstart:
- Create and activate a virtual environment
- Install ADK with `pip install google-adk`
- Set up your API key

### 2. Create a Streaming Agent

Create a new project directory and files:

```bash
mkdir streaming_agent
cd streaming_agent
touch __init__.py agent.py .env
```

In your `__init__.py` file:
```python
from . import agent
```

In your `.env` file, add your API key:
```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_API_KEY
```

### 3. Implement the Streaming Agent

In your `agent.py` file, implement a streaming agent:

```python
from google.adk.agents import Agent
from google.adk.server import run_local_server

# Create a simple agent with streaming enabled
streaming_agent = Agent(
    name="streaming_demo_agent",
    model="gemini-2.0-flash",
    description="I'm a helpful agent that demonstrates streaming responses.",
    # Enable streaming by setting this parameter
    enable_streaming=True
)

# Run the agent with a local development server
if __name__ == "__main__":
    run_local_server(streaming_agent)
```

### 4. Run the Streaming Agent

Execute your streaming agent with:

```bash
python -m streaming_agent.agent
```

### 5. Observe the Streaming Behavior

When interacting with your agent, you'll notice:
- Responses appear incrementally, word by word, providing a more conversational feel
- The streaming happens automatically when `enable_streaming=True` is set
- The client interface (terminal or browser) shows responses as they're generated

This streaming capability is particularly valuable for:
- Long responses, where users don't have to wait for the entire response to be generated
- Creating a more natural, conversational user experience
- Applications where immediate feedback is important

Note: Streaming is supported by both the terminal interface and the browser-based dev UI.

## Tutorial

This tutorial walks you through building your first multi-agent system - a more sophisticated application that demonstrates how to compose multiple specialized agents to work together.

### Prerequisites

Before starting this tutorial, ensure:
- You have completed the basic Quickstart
- You have a Python 3.9+ environment with ADK installed
- You understand the basic concept of agents and tools

### Overview: Building a Customer Support System

In this tutorial, we'll build a customer support system with two specialized agents:
1. **Router Agent**: Determines the type of customer inquiry
2. **Support Agent**: Handles specific customer support queries

This architecture demonstrates a multi-agent approach where each agent has a specialized role, and they work together to provide a comprehensive solution.

### 1. Project Setup

First, create a project directory:

```bash
mkdir support_system
cd support_system
touch __init__.py router_agent.py support_agent.py main.py .env
```

In your `.env` file, add your API key:
```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_API_KEY
```

In your `__init__.py` file:
```python
from . import router_agent, support_agent, main
```

### 2. Create the Router Agent

The router agent analyzes customer inquiries and routes them to the appropriate specialist. In `router_agent.py`:

```python
from google.adk.agents import Agent

# Knowledge base of product information used by the router
PRODUCT_INFO = {
    "basic_phone": {
        "name": "BasicPhone X1",
        "category": "smartphone",
        "price": "$199",
        "features": ["4G connectivity", "5-inch display", "3GB RAM"]
    },
    "premium_phone": {
        "name": "PremiumPhone Pro",
        "category": "smartphone",
        "price": "$999",
        "features": ["5G connectivity", "6.7-inch OLED display", "12GB RAM", "Water resistant"]
    }
}

def classify_inquiry(customer_inquiry: str) -> dict:
    """Classifies a customer inquiry by type.
    
    Args:
        customer_inquiry (str): The customer's inquiry text
        
    Returns:
        dict: Classification result with type and confidence
    """
    # In a real system, this might use a classifier model or more sophisticated logic
    inquiry_lower = customer_inquiry.lower()
    
    if "price" in inquiry_lower or "cost" in inquiry_lower or "how much" in inquiry_lower:
        return {"type": "pricing", "confidence": 0.9}
    elif "feature" in inquiry_lower or "spec" in inquiry_lower or "can it" in inquiry_lower:
        return {"type": "product_info", "confidence": 0.85}
    elif "problem" in inquiry_lower or "not working" in inquiry_lower or "issue" in inquiry_lower:
        return {"type": "technical_support", "confidence": 0.8}
    else:
        return {"type": "general_inquiry", "confidence": 0.7}

def get_product_info(product_id: str) -> dict:
    """Retrieves information about a specific product.
    
    Args:
        product_id (str): Identifier for the product
        
    Returns:
        dict: Product information or error message
    """
    product_id = product_id.lower()
    if product_id in PRODUCT_INFO:
        return {"status": "success", "info": PRODUCT_INFO[product_id]}
    else:
        return {
            "status": "error", 
            "message": f"Product '{product_id}' not found. Available products: {', '.join(PRODUCT_INFO.keys())}"
        }

# Create the router agent
router_agent = Agent(
    name="customer_inquiry_router",
    model="gemini-2.0-flash",
    description="I classify customer inquiries and route them to the appropriate department",
    instruction="""
    You are a router agent for a customer support system. Your job is to:
    1. Analyze each customer inquiry
    2. Use the classify_inquiry tool to determine the type of inquiry
    3. Provide routing instructions for handling the inquiry
    
    For product information requests, also use the get_product_info tool to retrieve
    detailed information about the product.
    
    Always respond with:
    1. The classification result
    2. Which specialist should handle this inquiry
    3. Any relevant product information (if applicable)
    4. A brief explanation of your routing decision
    """,
    tools=[classify_inquiry, get_product_info]
)
```

### 3. Create the Support Agent

The support agent handles the actual customer inquiries. In `support_agent.py`:

```python
from google.adk.agents import Agent

def search_knowledge_base(query: str, category: str = "general") -> dict:
    """Search the support knowledge base for information.
    
    Args:
        query (str): The search query
        category (str, optional): Category to search within. Defaults to "general".
        
    Returns:
        dict: Search results
    """
    # Simulated knowledge base responses
    knowledge_base = {
        "technical_support": {
            "restart": "To restart your device, hold the power button for 10 seconds, then turn it back on.",
            "battery": "If your battery is draining quickly, try closing background apps and reducing screen brightness.",
            "update": "To update your device, go to Settings > System > Software Update."
        },
        "pricing": {
            "discount": "We offer a 10% discount for students and senior citizens.",
            "warranty": "Extended warranty costs $49 for an additional year of coverage.",
            "shipping": "Standard shipping is free. Express shipping costs $15."
        },
        "general": {
            "hours": "Our support center is open Monday-Friday, 9am-5pm EST.",
            "contact": "You can reach us at support@example.com or call 1-800-555-1234.",
            "returns": "Products can be returned within 30 days with receipt for a full refund."
        }
    }
    
    # Select the appropriate category
    category_data = knowledge_base.get(category, knowledge_base["general"])
    
    # Search for relevant information
    results = {}
    query_terms = query.lower().split()
    for key, value in category_data.items():
        if any(term in key.lower() for term in query_terms):
            results[key] = value
    
    if results:
        return {"status": "success", "results": results}
    else:
        return {
            "status": "partial_success",
            "message": f"No exact matches found for '{query}' in category '{category}'.",
            "available_topics": list(category_data.keys())
        }

# Create the support agent
support_agent = Agent(
    name="customer_support_specialist",
    model="gemini-2.0-flash",
    description="I provide detailed customer support based on knowledge base information",
    instruction="""
    You are a customer support specialist. Your job is to:
    1. Understand the customer's inquiry
    2. Use the search_knowledge_base tool to find relevant information
    3. Provide a helpful, friendly response that addresses their specific question
    
    If the information isn't in our knowledge base, acknowledge this and suggest
    where they might find the information or offer to escalate their inquiry to a
    human specialist.
    
    Always be polite, professional, and empathetic in your responses.
    """,
    tools=[search_knowledge_base]
)
```

### 4. Combine Agents in Main Application

Now, let's create the main application that combines both agents. In `main.py`:

```python
from google.adk.agents import SequentialAgent
from google.adk.server import run_local_server
from .router_agent import router_agent
from .support_agent import support_agent

# Create a workflow agent that combines the router and support agent
support_system = SequentialAgent(
    name="customer_support_system",
    description="A two-stage customer support system that routes and responds to inquiries",
    agents=[router_agent, support_agent]
)

# Run the combined agent in a local server
if __name__ == "__main__":
    run_local_server(support_system)
```

### 5. Run the Multi-Agent System

Execute your support system with:

```bash
python -m support_system.main
```

You can now interact with your customer support system via the terminal or browser interface (typically at http://localhost:8080).

### 6. Testing the System

Try the following test inquiries:

1. "How much does the PremiumPhone Pro cost?"
2. "What are the features of the BasicPhone X1?"
3. "My phone's battery is draining too quickly, can you help?"
4. "What are your store hours?"

### What You've Learned

In this tutorial, you've built a multi-agent system where:
- The router agent analyzes and classifies customer inquiries
- The support agent provides detailed responses based on a knowledge base
- A sequential workflow connects these specialized agents

This architecture demonstrates key ADK concepts:
- Specialized agents with defined roles
- Tool usage for accessing external data
- Workflow agents for orchestration
- Multi-stage processing of user requests

### Next Steps

To extend this system, consider:
- Adding more specialized agents for different departments
- Implementing a real knowledge base connection
- Adding memory to track conversation history
- Creating a feedback loop for agent improvement

## Testing

Proper testing is essential for building reliable and robust agent applications. This guide covers approaches for testing your ADK agents, from basic unit tests to comprehensive integration testing.

### Unit Testing Your Agents

Unit tests verify that individual components of your agent system work correctly in isolation. These tests are fast to run and help catch issues early in the development process.

#### Testing Tools and Functions

Start by testing the individual tools your agent uses. Here's an example of testing a weather function tool:

```python
import unittest

# Import the function to test
from your_agent_package.tools import get_weather

class TestWeatherTool(unittest.TestCase):
    def test_get_weather_success(self):
        result = get_weather("New York")
        self.assertEqual(result["status"], "success")
        self.assertIn("temperature", result["report"])
    
    def test_get_weather_failure(self):
        result = get_weather("NonexistentCity")
        self.assertEqual(result["status"], "error")
        self.assertIn("error_message", result)

if __name__ == "__main__":
    unittest.main()
```

#### Testing Agent Behavior with Mocks

For testing the agent itself, you'll often want to mock the LLM and tool calls to control the testing environment:

```python
import unittest
from unittest.mock import patch, MagicMock
from google.adk.agents import Agent

class TestMyAgent(unittest.TestCase):
    @patch("google.adk.agents.LlmAgent._call_llm")
    def test_agent_response(self, mock_call_llm):
        # Setup the mock to return a predetermined response
        mock_response = MagicMock()
        mock_response.text = "The weather in New York is sunny."
        mock_call_llm.return_value = mock_response
        
        # Create the agent with mocked tools
        mock_weather_tool = MagicMock(return_value={"status": "success", "report": "Sunny, 25°C"})
        
        agent = Agent(
            name="test_agent",
            model="gemini-2.0-flash",
            tools=[mock_weather_tool]
        )
        
        # Test the agent's response
        response = agent.run("What's the weather in New York?")
        self.assertIn("sunny", response.text.lower())

if __name__ == "__main__":
    unittest.main()
```

### Integration Testing

Integration tests verify that the different components of your system work together correctly. For ADK agents, this typically means testing the interaction between:

1. The agent and its tools
2. Multiple agents in a workflow
3. The agent and external systems (like databases or APIs)

```python
import unittest
from google.adk.agents import Agent, SequentialAgent

class TestCustomerSupportSystem(unittest.TestCase):
    def setUp(self):
        # Create the actual components we want to test together
        self.router_agent = create_router_agent()
        self.support_agent = create_support_agent()
        
        # Combine them into a workflow
        self.support_system = SequentialAgent(
            name="test_support_system",
            agents=[self.router_agent, self.support_agent]
        )
    
    def test_end_to_end_pricing_query(self):
        # Test a complete customer journey
        response = self.support_system.run("How much does the premium phone cost?")
        
        # Verify the response contains pricing information
        self.assertIn("$999", response.text)
        
        # You can also inspect the session state or other outputs
        # to verify the correct path was taken through the system

if __name__ == "__main__":
    unittest.main()
```

### Testing with Agent Evaluation Framework

For more comprehensive testing, ADK's evaluation framework can be used to test both the agent's final responses and its trajectory (the sequence of actions taken):

```python
from google.adk.evaluation import evaluate_agent, TrajectoryEvaluator

# Define test cases
test_cases = [
    {
        "input": "What's the weather in New York?",
        "expected_output": {"contains": ["New York", "temperature"]},
        "expected_trajectory": ["determine_intent", "get_weather", "format_response"]
    },
    {
        "input": "What time is it in London?",
        "expected_output": {"contains": ["London", "time"]},
        "expected_trajectory": ["determine_intent", "get_current_time", "format_response"]
    }
]

# Create custom evaluators if needed
class CustomEvaluator(TrajectoryEvaluator):
    def evaluate(self, actual_trajectory, expected_trajectory):
        # Custom evaluation logic
        return {"score": 0.95, "details": "All critical steps were performed correctly"}

# Run the evaluation
results = evaluate_agent(
    agent=my_agent,
    test_cases=test_cases,
    evaluators=[CustomEvaluator()]
)

# Print results
print(f"Overall score: {results['overall_score']}")
for case_result in results['case_results']:
    print(f"Case: {case_result['input']}")
    print(f"Success: {case_result['success']}")
    print(f"Score: {case_result['score']}")
```

### Best Practices for Testing ADK Agents

1. **Test at different levels**: Unit test individual tools, integration test agent workflows, and end-to-end test complete user journeys.

2. **Mock external dependencies**: Use mocks for LLMs, APIs, and databases to create predictable, repeatable tests.

3. **Test edge cases**: Include tests for error handling, unexpected inputs, and boundary conditions.

4. **Automate tests**: Set up CI/CD pipelines to run tests automatically on code changes.

5. **Test for regressions**: When you fix a bug, add a test to ensure it doesn't reappear in the future.

6. **Consider performance**: Include tests for response time, especially for agents with complex workflows or large knowledge bases.

7. **Test across environments**: Ensure your agent works correctly in all deployment environments (development, staging, production).

## Sample Agents

The ADK repository includes several sample agents that demonstrate different capabilities and use cases. Exploring these examples is a great way to understand how to build your own agents with specific features.

### Basic Samples

#### Echo Agent

The Echo Agent is the simplest possible agent - it simply echoes back what the user says. This serves as a minimal starting point:

```python
from google.adk.agents import Agent

# Create a simple echo agent
echo_agent = Agent(
    name="echo_agent",
    model="gemini-2.0-flash",
    instruction="Echo back exactly what the user says, prefixed with 'You said: '"
)

# Run the agent
response = echo_agent.run("Hello, agent!")
print(response.text)  # Output: "You said: Hello, agent!"
```

#### Weather Agent

This sample demonstrates using tools to access external information:

```python
from google.adk.agents import Agent

def get_weather(location: str) -> dict:
    """Get weather for a specific location.
    
    Args:
        location: The city or region to get weather for
        
    Returns:
        dict: Weather information
    """
    # In a real app, this would call a weather API
    return {"temperature": "72°F", "condition": "Sunny", "location": location}

weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    instruction="Help users check weather. Use the get_weather tool when asked about weather.",
    tools=[get_weather]
)
```

### Advanced Samples

#### Multimodal Agent

This sample demonstrates handling image inputs:

```python
from google.adk.agents import Agent
import google.genai.types as types
from PIL import Image
import io

# Create a multimodal agent
image_agent = Agent(
    name="image_analyzer",
    model="gemini-2.0-pro-vision", # Vision-capable model
    instruction="Describe images that users send you in detail."
)

# Example usage with an image
def process_image(image_path):
    # Load image
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    # Create a Part object containing the image
    image_part = types.Part.from_data(data=image_bytes, mime_type="image/jpeg")
    
    # Run the agent with the image
    response = image_agent.run(
        "What's in this image?", 
        artifacts=[image_part]
    )
    return response.text
```

#### RAG (Retrieval-Augmented Generation) Agent

This sample demonstrates using a vector database for knowledge retrieval:

```python
from google.adk.agents import Agent
from google.adk.tools.rag import create_rag_tool

# In a real application, this would be your vector database
knowledge_base = [
    {"content": "ADK stands for Agent Development Kit", "metadata": {"source": "docs"}},
    {"content": "ADK was released by Google in 2024", "metadata": {"source": "docs"}}
]

# Create a RAG tool
rag_tool = create_rag_tool(
    knowledge_base=knowledge_base,
    embedding_model="text-embedding-3-small"
)

# Create an agent with the RAG tool
rag_agent = Agent(
    name="documentation_assistant",
    model="gemini-2.0-flash",
    instruction="""
    You are a documentation assistant. When users ask questions,
    use the search_knowledge_base tool to find relevant information
    before answering.
    """,
    tools=[rag_tool]
)
```

### How to Run the Samples

The sample agents can be run in different ways:

1. **Command line**: Use the ADK CLI to run agents interactively:
   ```bash
   python -m google.adk.cli run --agent path.to.your.agent
   ```

2. **Local server**: Run a development server for a browser-based UI:
   ```python
   from google.adk.server import run_local_server
   
   # Run your agent with a web UI
   run_local_server(your_agent)
   ```

3. **Import in your code**: Use the samples as a starting point for your own applications:
   ```python
   from your_module import sample_agent
   
   # Use the agent in your application
   response = sample_agent.run("Your input here")
   ```

### Learning from Samples

When exploring these samples, pay attention to:

1. **Agent Configuration**: How different parameters affect agent behavior
2. **Tool Integration**: How tools are defined and used by agents
3. **Prompt Engineering**: How instructions shape the agent's responses
4. **Error Handling**: How the samples handle edge cases and errors

The sample code is designed to be readable and educational, serving as a reference for your own agent development.

## About ADK

### Key Concepts

The Agent Development Kit (ADK) is built around several key concepts:

1. **Agents**: Self-contained execution units that can understand user requests, take actions, and generate responses.

2. **Tools**: Functions or integrations that extend an agent's capabilities beyond text generation.

3. **Sessions & Memory**: Infrastructure for maintaining conversation context and persistent knowledge.

4. **Runtime**: The execution engine that orchestrates agents, tools, and services.

5. **Evaluation**: Systems for testing and improving agent performance.

### Core Principles

ADK was designed with specific principles in mind:

1. **Modularity**: Components are decoupled and can be composed in various ways.

2. **Extensibility**: The framework is designed to be extended with custom components.

3. **Integration**: Built to work seamlessly with Google Cloud and AI services, while also supporting third-party tools.

4. **Developer Experience**: Focused on making agent development accessible and intuitive.

5. **Production Readiness**: Designed to support the full lifecycle from prototyping to production deployment.

### Technical Architecture

ADK follows a layered architecture:

1. **Core Layer**: Defines fundamental abstractions and interfaces.
   - Agent interfaces
   - Tool interfaces
   - Event system

2. **Service Layer**: Provides concrete implementations of core services.
   - LLM integrations
   - Session management
   - Artifact handling

3. **Orchestration Layer**: Coordinates the execution of agents and tools.
   - Runtime engine
   - Event processing
   - State management

4. **Developer Tools**: Utilities for building and testing agents.
   - CLI tools
   - Development server
   - Evaluation framework

### Project Status

ADK is an open-source project that continues to evolve. As of this documentation:

- The stable API includes core agent interfaces, tool integrations, and deployment options.
- Some features may be in preview and subject to change.
- The project welcomes community contributions (see Contributing Guide).

For the latest updates, check the [GitHub repository](https://github.com/google/adk-python) and release notes.

# Agents

## Agents Overview

In the Agent Development Kit (ADK), an **Agent** is a self-contained execution unit designed to act autonomously to achieve specific goals. Agents can perform tasks, interact with users, utilize external tools, and coordinate with other agents.

The foundation for all agents in ADK is the `BaseAgent` class. It serves as the fundamental blueprint. To create functional agents, you typically extend `BaseAgent` in one of three main ways, catering to different needs – from intelligent reasoning to structured process control.

## Core Agent Categories

ADK provides distinct agent categories to build sophisticated applications:

1. **LLM Agents** (`LLMAgent`, `Agent`): These agents utilize Large Language Models (LLMs) as their core engine to understand natural language, reason, plan, generate responses, and dynamically decide how to proceed or which tools to use, making them ideal for flexible, language-centric tasks. [Learn more about LLM Agents...]
    
    The LlmAgent (often aliased simply as Agent) is a core component in ADK, acting as the "thinking" part of your application. It leverages the power of a Large Language Model (LLM) for reasoning, understanding natural language, making decisions, generating responses, and interacting with tools.

    Unlike deterministic Workflow Agents that follow predefined execution paths, LlmAgent behavior is non-deterministic. It uses the LLM to interpret instructions and context, deciding dynamically how to proceed, which tools to use (if any), or whether to transfer control to another agent.

    Building an effective LlmAgent involves defining its identity, clearly guiding its behavior through instructions, and equipping it with the necessary tools and capabilities.

    Defining the Agent's Identity and Purpose
    First, you need to establish what the agent is and what it's for.

    name (Required): Every agent needs a unique string identifier. This name is crucial for internal operations, especially in multi-agent systems where agents need to refer to or delegate tasks to each other. Choose a descriptive name that reflects the agent's function (e.g., customer_support_router, billing_inquiry_agent). Avoid reserved names like user.

    description (Optional, Recommended for Multi-Agent): Provide a concise summary of the agent's capabilities. This description is primarily used by other LLM agents to determine if they should route a task to this agent. Make it specific enough to differentiate it from peers (e.g., "Handles inquiries about current billing statements," not just "Billing agent").

    model (Required): Specify the underlying LLM that will power this agent's reasoning. This is a string identifier like "gemini-2.0-flash". The choice of model impacts the agent's capabilities, cost, and performance. See the Models page for available options and considerations.


    # Example: Defining the basic identity
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="Answers user questions about the capital city of a given country."
        # instruction and tools will be added next
    )
    Guiding the Agent: Instructions (instruction)
    The instruction parameter is arguably the most critical for shaping an LlmAgent's behavior. It's a string (or a function returning a string) that tells the agent:

    Its core task or goal.
    Its personality or persona (e.g., "You are a helpful assistant," "You are a witty pirate").
    Constraints on its behavior (e.g., "Only answer questions about X," "Never reveal Y").
    How and when to use its tools. You should explain the purpose of each tool and the circumstances under which it should be called, supplementing any descriptions within the tool itself.
    The desired format for its output (e.g., "Respond in JSON," "Provide a bulleted list").
    Tips for Effective Instructions:

    Be Clear and Specific: Avoid ambiguity. Clearly state the desired actions and outcomes.
    Use Markdown: Improve readability for complex instructions using headings, lists, etc.
    Provide Examples (Few-Shot): For complex tasks or specific output formats, include examples directly in the instruction.
    Guide Tool Use: Don't just list tools; explain when and why the agent should use them.

    # Example: Adding instructions
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="Answers user questions about the capital city of a given country.",
        instruction="""You are an agent that provides the capital city of a country.
    When a user asks for the capital of a country:
    1. Identify the country name from the user's query.
    2. Use the `get_capital_city` tool to find the capital.
    3. Respond clearly to the user, stating the capital city.
    Example Query: "What's the capital of France?"
    Example Response: "The capital of France is Paris."
    """,
        # tools will be added next
    )
    (Note: For instructions that apply to all agents in a system, consider using global_instruction on the root agent, detailed further in the Multi-Agents section.)

    Equipping the Agent: Tools (tools)
    Tools give your LlmAgent capabilities beyond the LLM's built-in knowledge or reasoning. They allow the agent to interact with the outside world, perform calculations, fetch real-time data, or execute specific actions.

    tools (Optional): Provide a list of tools the agent can use. Each item in the list can be:
    A Python function (automatically wrapped as a FunctionTool).
    An instance of a class inheriting from BaseTool.
    An instance of another agent (AgentTool, enabling agent-to-agent delegation - see Multi-Agents).
    The LLM uses the function/tool names, descriptions (from docstrings or the description field), and parameter schemas to decide which tool to call based on the conversation and its instructions.


    # Define a tool function
    def get_capital_city(country: str) -> str:
    """Retrieves the capital city for a given country."""
    # Replace with actual logic (e.g., API call, database lookup)
    capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
    return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

    # Add the tool to the agent
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="Answers user questions about the capital city of a given country.",
        instruction="""You are an agent that provides the capital city of a country... (previous instruction text)""",
        tools=[get_capital_city] # Provide the function directly
    )
    Learn more about Tools in the Tools section.

    Advanced Configuration & Control
    Beyond the core parameters, LlmAgent offers several options for finer control:

    Fine-Tuning LLM Generation (generate_content_config)
    You can adjust how the underlying LLM generates responses using generate_content_config.

    generate_content_config (Optional): Pass an instance of google.genai.types.GenerateContentConfig to control parameters like temperature (randomness), max_output_tokens (response length), top_p, top_k, and safety settings.


    from google.genai import types

    agent = LlmAgent(
        # ... other params
        generate_content_config=types.GenerateContentConfig(
            temperature=0.2, # More deterministic output
            max_output_tokens=250
        )
    )
    Structuring Data (input_schema, output_schema, output_key)
    For scenarios requiring structured data exchange, you can use Pydantic models.

    input_schema (Optional): Define a Pydantic BaseModel class representing the expected input structure. If set, the user message content passed to this agent must be a JSON string conforming to this schema. Your instructions should guide the user or preceding agent accordingly.

    output_schema (Optional): Define a Pydantic BaseModel class representing the desired output structure. If set, the agent's final response must be a JSON string conforming to this schema.

    Constraint: Using output_schema enables controlled generation within the LLM but disables the agent's ability to use tools or transfer control to other agents. Your instructions must guide the LLM to produce JSON matching the schema directly.
    output_key (Optional): Provide a string key. If set, the text content of the agent's final response will be automatically saved to the session's state dictionary under this key (e.g., session.state[output_key] = agent_response_text). This is useful for passing results between agents or steps in a workflow.


    from pydantic import BaseModel, Field

    class CapitalOutput(BaseModel):
        capital: str = Field(description="The capital of the country.")

    structured_capital_agent = LlmAgent(
        # ... name, model, description
        instruction="""You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {"capital": "capital_name"}""",
        output_schema=CapitalOutput, # Enforce JSON output
        output_key="found_capital"  # Store result in state['found_capital']
        # Cannot use tools=[get_capital_city] effectively here
    )
    Managing Context (include_contents)
    Control whether the agent receives the prior conversation history.

    include_contents (Optional, Default: 'default'): Determines if the contents (history) are sent to the LLM.

    'default': The agent receives the relevant conversation history.
    'none': The agent receives no prior contents. It operates based solely on its current instruction and any input provided in the current turn (useful for stateless tasks or enforcing specific contexts).

    stateless_agent = LlmAgent(
        # ... other params
        include_contents='none'
    )
    Planning & Code Execution
    For more complex reasoning involving multiple steps or executing code:

    planner (Optional): Assign a BasePlanner instance to enable multi-step reasoning and planning before execution. (See Multi-Agents patterns).
    code_executor (Optional): Provide a BaseCodeExecutor instance to allow the agent to execute code blocks (e.g., Python) found in the LLM's response. (See Tools/Built-in tools).

    

2. **Workflow Agents** (`SequentialAgent`, `ParallelAgent`, `LoopAgent`): These specialized agents control the execution flow of other agents in predefined, deterministic patterns (sequence, parallel, or loop) without using an LLM for the flow control itself, perfect for structured processes needing predictable execution. [Explore Workflow Agents...]
    This section introduces "workflow agents" - specialized agents that control the execution flow of its sub-agents.

    Workflow agents are specialized components in ADK designed purely for orchestrating the execution flow of sub-agents. Their primary role is to manage how and when other agents run, defining the control flow of a process.

    Unlike LLM Agents, which use Large Language Models for dynamic reasoning and decision-making, Workflow Agents operate based on predefined logic. They determine the execution sequence according to their type (e.g., sequential, parallel, loop) without consulting an LLM for the orchestration itself. This results in deterministic and predictable execution patterns.

    ADK provides three core workflow agent types, each implementing a distinct execution pattern:

    1) Sequential Agents

        Executes sub-agents one after another, in sequence.

        The SequentialAgent
        The SequentialAgent is a workflow agent that executes its sub-agents in the order they are specified in the list.

        Use the SequentialAgent when you want the execution to occur in a fixed, strict order.

        Example
        You want to build an agent that can summarize any webpage, using two tools: get_page_contents and summarize_page. Because the agent must always call get_page_contents before calling summarize_page (you can't summarize from nothing!), you should build your agent using a SequentialAgent.
        As with other workflow agents, the SequentialAgent is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are only concerned only with their execution (i.e. in sequence), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

        How it works
        When the SequentialAgent's run_async() method is called, it performs the following actions:

        Iteration: It iterates through the sub_agents list in the order they were provided.
        Sub-Agent Execution: For each sub-agent in the list, it calls the sub-agent's run_async() method.
        Sequential Agent

    2) Loop Agents

    Repeatedly executes its sub-agents until a specific termination condition is met.

        The LoopAgent is a workflow agent that executes its sub-agents in a loop (i.e. iteratively). It repeatedly runs a sequence of agents for a specified number of iterations or until a termination condition is met.

        Use the LoopAgent when your workflow involves repetition or iterative refinement, such as like revising code.

        Example
        You want to build an agent that can generate images of food, but sometimes when you want to generate a specific number of items (e.g. 5 bananas), it generates a different number of those items in the image (e.g. an image of 7 bananas). You have two tools: generate_image, count_food_items. Because you want to keep generating images until it either correctly generates the specified number of items, or after a certain number of iterations, you should build your agent using a LoopAgent.
        As with other workflow agents, the LoopAgent is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are only concerned only with their execution (i.e. in a loop), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

        How it Works
        When the LoopAgent's run_async() method is called, it performs the following actions:

        Sub-Agent Execution: It iterates through the sub_agents list in order. For each sub-agent, it calls the agent's run_async() method.
        Termination Check:

        Crucially, the LoopAgent itself does not inherently decide when to stop looping. You must implement a termination mechanism to prevent infinite loops. Common strategies include:

        max_iterations: Set a maximum number of iterations in the LoopAgent. The loop will terminate after that many iterations.
        Escalation from sub-agent: Design one or more sub-agents to evaluate a condition (e.g., "Is the document quality good enough?", "Has a consensus been reached?"). If the condition is met, the sub-agent can signal termination (e.g., by raising a custom event, setting a flag in a shared context, or returning a specific value). Loop Agent

    Parallel Agents

    Executes multiple sub-agents in parallel.

        The ParallelAgent is a workflow agent that executes its sub-agents concurrently. This dramatically speeds up workflows where tasks can be performed independently.

        Use ParallelAgent when: For scenarios prioritizing speed and involving independent, resource-intensive tasks, a ParallelAgent facilitates efficient parallel execution. When sub-agents operate without dependencies, their tasks can be performed concurrently, significantly reducing overall processing time.

        As with other workflow agents, the ParallelAgent is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are only concerned only with their execution (i.e. in parallel), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

        Example
        This approach is particularly beneficial for operations like multi-source data retrieval or heavy computations, where parallelization yields substantial performance gains. Importantly, this strategy assumes no inherent need for shared state or direct information exchange between the concurrently executing agents.

        How it works
        When the ParallelAgent's run_async() method is called:

        Concurrent Execution: It initiates the run() method of each sub-agent present in the sub_agents list concurrently. This means all the agents start running at (approximately) the same time.
        Independent Branches: Each sub-agent operates in its own execution branch. There is no automatic sharing of conversation history or state between these branches during execution.
        Result Collection: The ParallelAgent manages the parallel execution and, typically, provides a way to access the results from each sub-agent after they have completed (e.g., through a list of results or events). The order of results may not be deterministic.
        Independent Execution and State Management
        It's crucial to understand that sub-agents within a ParallelAgent run independently. If you need communication or data sharing between these agents, you must implement it explicitly. Possible approaches include:

        Shared InvocationContext: You could pass a shared InvocationContext object to each sub-agent. This object could act as a shared data store. However, you'd need to manage concurrent access to this shared context carefully (e.g., using locks) to avoid race conditions.
        External State Management: Use an external database, message queue, or other mechanism to manage shared state and facilitate communication between agents.
        Post-Processing: Collect results from each branch, and then implement logic to coordinate data afterwards.
        Parallel Agent

    Why Use Workflow Agents?
    Workflow agents are essential when you need explicit control over how a series of tasks or agents are executed. They provide:

    Predictability: The flow of execution is guaranteed based on the agent type and configuration.
    Reliability: Ensures tasks run in the required order or pattern consistently.
    Structure: Allows you to build complex processes by composing agents within clear control structures.
    While the workflow agent manages the control flow deterministically, the sub-agents it orchestrates can themselves be any type of agent, including intelligent LlmAgent instances. This allows you to combine structured process control with flexible, LLM-powered task execution.

        Full Example: Parallel Web Research
        Imagine researching multiple topics simultaneously:

        Researcher Agent 1: An LlmAgent that researches "renewable energy sources."
        Researcher Agent 2: An LlmAgent that researches "electric vehicle technology."
        Researcher Agent 3: An LlmAgent that researches "carbon capture methods."


        ParallelAgent(sub_agents=[ResearcherAgent1, ResearcherAgent2, ResearcherAgent3])
        These research tasks are independent. Using a ParallelAgent allows them to run concurrently, potentially reducing the total research time significantly compared to running them sequentially. The results from each agent would be collected separately after they finish.

        Code

        from google.adk.agents.parallel_agent import ParallelAgent
        from google.adk.agents.llm_agent import LlmAgent
        from google.adk.sessions import InMemorySessionService
        from google.adk.runners import Runner
        from google.adk.tools import google_search
        from google.genai import types

        APP_NAME = "parallel_research_app"
        USER_ID = "research_user_01"
        SESSION_ID = "parallel_research_session"
        GEMINI_MODEL = "gemini-2.0-flash"

        # --- Define Researcher Sub-Agents ---

        # Researcher 1: Renewable Energy
        researcher_agent_1 = LlmAgent(
            name="RenewableEnergyResearcher",
            model=GEMINI_MODEL,
            instruction="""You are an AI Research Assistant specializing in energy.
            Research the latest advancements in 'renewable energy sources'.
            Use the Google Search tool provided.
            Summarize your key findings concisely (1-2 sentences).
            Output *only* the summary.
            """,
            description="Researches renewable energy sources.",
            tools=[google_search], # Provide the search tool
            # Save the result to session state
            output_key="renewable_energy_result"
        )

        # Researcher 2: Electric Vehicles
        researcher_agent_2 = LlmAgent(
            name="EVResearcher",
            model=GEMINI_MODEL,
            instruction="""You are an AI Research Assistant specializing in transportation.
            Research the latest developments in 'electric vehicle technology'.
            Use the Google Search tool provided.
            Summarize your key findings concisely (1-2 sentences).
            Output *only* the summary.
            """,
            description="Researches electric vehicle technology.",
            tools=[google_search], # Provide the search tool
            # Save the result to session state
            output_key="ev_technology_result"
        )

        # Researcher 3: Carbon Capture
        researcher_agent_3 = LlmAgent(
            name="CarbonCaptureResearcher",
            model=GEMINI_MODEL,
            instruction="""You are an AI Research Assistant specializing in climate solutions.
            Research the current state of 'carbon capture methods'.
            Use the Google Search tool provided.
            Summarize your key findings concisely (1-2 sentences).
            Output *only* the summary.
            """,
            description="Researches carbon capture methods.",
            tools=[google_search], # Provide the search tool
            # Save the result to session state
            output_key="carbon_capture_result"
        )

        # --- Create the ParallelAgent ---
        # This agent orchestrates the concurrent execution of the researchers.
        parallel_research_agent = ParallelAgent(
            name="ParallelWebResearchAgent",
            sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3]
        )

        # Session and Runner
        session_service = InMemorySessionService()
        session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        runner = Runner(agent=parallel_research_agent, app_name=APP_NAME, session_service=session_service)


        # Agent Interaction
        def call_agent(query):
            '''
            Helper function to call the agent with a query.
            '''
            content = types.Content(role='user', parts=[types.Part(text=query)])
            events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

            for event in events:
                if event.is_final_response():
                    final_response = event.content.parts[0].text
                    print("Agent Response: ", final_response)

        call_agent("research latest trends")

3. **Custom Agents**: Created by extending `BaseAgent` directly, these agents allow you to implement unique operational logic, specific control flows, or specialized integrations not covered by the standard types, catering to highly tailored application requirements. [Discover how to build Custom Agents...]
        Advanced Concept

    Building custom agents by directly implementing _run_async_impl provides powerful control but is more complex than using the predefined LlmAgent or standard WorkflowAgent types. We recommend understanding those foundational agent types first before tackling custom orchestration logic.

    Custom agents
    Custom agents provide the ultimate flexibility in ADK, allowing you to define arbitrary orchestration logic by inheriting directly from BaseAgent and implementing your own control flow. This goes beyond the predefined patterns of SequentialAgent, LoopAgent, and ParallelAgent, enabling you to build highly specific and complex agentic workflows.

    Introduction: Beyond Predefined Workflows
    What is a Custom Agent?
    A Custom Agent is essentially any class you create that inherits from google.adk.agents.BaseAgent and implements its core execution logic within the _run_async_impl asynchronous method. You have complete control over how this method calls other agents (sub-agents), manages state, and handles events.

    Why Use Them?
    While the standard Workflow Agents (SequentialAgent, LoopAgent, ParallelAgent) cover common orchestration patterns, you'll need a Custom agent when your requirements include:

    Conditional Logic: Executing different sub-agents or taking different paths based on runtime conditions or the results of previous steps.
    Complex State Management: Implementing intricate logic for maintaining and updating state throughout the workflow beyond simple sequential passing.
    External Integrations: Incorporating calls to external APIs, databases, or custom Python libraries directly within the orchestration flow control.
    Dynamic Agent Selection: Choosing which sub-agent(s) to run next based on dynamic evaluation of the situation or input.
    Unique Workflow Patterns: Implementing orchestration logic that doesn't fit the standard sequential, parallel, or loop structures.
    intro_components.png

    Implementing Custom Logic:
    The heart of any custom agent is the _run_async_impl method. This is where you define its unique behavior.

    Signature: async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
    Asynchronous Generator: It must be an async def function and return an AsyncGenerator. This allows it to yield events produced by sub-agents or its own logic back to the runner.
    ctx (InvocationContext): Provides access to crucial runtime information, most importantly ctx.session.state, which is the primary way to share data between steps orchestrated by your custom agent.
    Key Capabilities within _run_async_impl:

    Calling Sub-Agents: You invoke sub-agents (which are typically stored as instance attributes like self.my_llm_agent) using their run_async method and yield their events:


    async for event in self.some_sub_agent.run_async(ctx):
        # Optionally inspect or log the event
        yield event # Pass the event up
    Managing State: Read from and write to the session state dictionary (ctx.session.state) to pass data between sub-agent calls or make decisions:


    # Read data set by a previous agent
    previous_result = ctx.session.state.get("some_key")

    # Make a decision based on state
    if previous_result == "some_value":
        # ... call a specific sub-agent ...
    else:
        # ... call another sub-agent ...

    # Store a result for a later step (often done via a sub-agent's output_key)
    # ctx.session.state["my_custom_result"] = "calculated_value"
    Implementing Control Flow: Use standard Python constructs (if/elif/else, for/while loops, try/except) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

    Managing Sub-Agents and State
    Typically, a custom agent orchestrates other agents (like LlmAgent, LoopAgent, etc.).

    Initialization: You usually pass instances of these sub-agents into your custom agent's __init__ method and store them as instance attributes (e.g., self.story_generator = story_generator_instance). This makes them accessible within _run_async_impl.
    sub_agents List: When initializing the BaseAgent using super().__init__(...), you should pass a sub_agents list. This list tells the ADK framework about the agents that are part of this custom agent's immediate hierarchy. It's important for framework features like lifecycle management, introspection, and potentially future routing capabilities, even if your _run_async_impl calls the agents directly via self.xxx_agent. Include the agents that your custom logic directly invokes at the top level.
    State: As mentioned, ctx.session.state is the standard way sub-agents (especially LlmAgents using output_key) communicate results back to the orchestrator and how the orchestrator passes necessary inputs down.
    Design Pattern Example: StoryFlowAgent
    Let's illustrate the power of custom agents with an example pattern: a multi-stage content generation workflow with conditional logic.

    Goal: Create a system that generates a story, iteratively refines it through critique and revision, performs final checks, and crucially, regenerates the story if the final tone check fails.

    Why Custom? The core requirement driving the need for a custom agent here is the conditional regeneration based on the tone check. Standard workflow agents don't have built-in conditional branching based on the outcome of a sub-agent's task. We need custom Python logic (if tone == "negative": ...) within the orchestrator.

    Part 1: Simplified custom agent Initialization
    We define the StoryFlowAgent inheriting from BaseAgent. In __init__, we store the necessary sub-agents (passed in) as instance attributes and tell the BaseAgent framework about the top-level agents this custom agent will directly orchestrate.


    class StoryFlowAgent(BaseAgent):
        """
        Custom agent for a story generation and refinement workflow.

        This agent orchestrates a sequence of LLM agents to generate a story,
        critique it, revise it, check grammar and tone, and potentially
        regenerate the story if the tone is negative.
        """

        # --- Field Declarations for Pydantic ---
        # Declare the agents passed during initialization as class attributes with type hints
        story_generator: LlmAgent
        critic: LlmAgent
        reviser: LlmAgent
        grammar_check: LlmAgent
        tone_check: LlmAgent

        loop_agent: LoopAgent
        sequential_agent: SequentialAgent

        # model_config allows setting Pydantic configurations if needed, e.g., arbitrary_types_allowed
        model_config = {"arbitrary_types_allowed": True}

        def __init__(
            self,
            name: str,
            story_generator: LlmAgent,
            critic: LlmAgent,
            reviser: LlmAgent,
            grammar_check: LlmAgent,
            tone_check: LlmAgent,
        ):
            """
            Initializes the StoryFlowAgent.

            Args:
                name: The name of the agent.
                story_generator: An LlmAgent to generate the initial story.
                critic: An LlmAgent to critique the story.
                reviser: An LlmAgent to revise the story based on criticism.
                grammar_check: An LlmAgent to check the grammar.
                tone_check: An LlmAgent to analyze the tone.
            """
            # Create internal agents *before* calling super().__init__
            loop_agent = LoopAgent(
                name="CriticReviserLoop", sub_agents=[critic, reviser], max_iterations=2
            )
            sequential_agent = SequentialAgent(
                name="PostProcessing", sub_agents=[grammar_check, tone_check]
            )

            # Define the sub_agents list for the framework
            sub_agents_list = [
                story_generator,
                loop_agent,
                sequential_agent,
            ]

            # Pydantic will validate and assign them based on the class annotations.
            super().__init__(
                name=name,
                story_generator=story_generator,
                critic=critic,
                reviser=reviser,
                grammar_check=grammar_check,
                tone_check=tone_check,
                loop_agent=loop_agent,
                sequential_agent=sequential_agent,
                sub_agents=sub_agents_list, # Pass the sub_agents list directly
            )
    Part 2: Defining the Custom Execution Logic
    This method orchestrates the sub-agents using standard Python async/await and control flow.


        @override
        async def _run_async_impl(
            self, ctx: InvocationContext
        ) -> AsyncGenerator[Event, None]:
            """
            Implements the custom orchestration logic for the story workflow.
            Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
            """
            logger.info(f"[{self.name}] Starting story generation workflow.")

            # 1. Initial Story Generation
            logger.info(f"[{self.name}] Running StoryGenerator...")
            async for event in self.story_generator.run_async(ctx):
                logger.info(f"[{self.name}] Event from StoryGenerator: {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event

            # Check if story was generated before proceeding
            if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
                logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
                return # Stop processing if initial story failed

            logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")


            # 2. Critic-Reviser Loop
            logger.info(f"[{self.name}] Running CriticReviserLoop...")
            # Use the loop_agent instance attribute assigned during init
            async for event in self.loop_agent.run_async(ctx):
                logger.info(f"[{self.name}] Event from CriticReviserLoop: {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event

            logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

            # 3. Sequential Post-Processing (Grammar and Tone Check)
            logger.info(f"[{self.name}] Running PostProcessing...")
            # Use the sequential_agent instance attribute assigned during init
            async for event in self.sequential_agent.run_async(ctx):
                logger.info(f"[{self.name}] Event from PostProcessing: {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event

            # 4. Tone-Based Conditional Logic
            tone_check_result = ctx.session.state.get("tone_check_result")
            logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

            if tone_check_result == "negative":
                logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
                async for event in self.story_generator.run_async(ctx):
                    logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
                    yield event
            else:
                logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")
                pass

            logger.info(f"[{self.name}] Workflow finished.")
    Explanation of Logic:

    The initial story_generator runs. Its output is expected to be in ctx.session.state["current_story"].
    The loop_agent runs, which internally calls the critic and reviser sequentially for max_iterations times. They read/write current_story and criticism from/to the state.
    The sequential_agent runs, calling grammar_check then tone_check, reading current_story and writing grammar_suggestions and tone_check_result to the state.
    Custom Part: The if statement checks the tone_check_result from the state. If it's "negative", the story_generator is called again, overwriting the current_story in the state. Otherwise, the flow ends.
    Part 3: Defining the LLM Sub-Agents
    These are standard LlmAgent definitions, responsible for specific tasks. Their output_key parameter is crucial for placing results into the session.state where other agents or the custom orchestrator can access them.


    GEMINI_FLASH = "gemini-2.0-flash" # Define model constant
    # --- Define the individual LLM agents ---
    story_generator = LlmAgent(
        name="StoryGenerator",
        model=GEMINI_2_FLASH,
        instruction="""You are a story writer. Write a short story (around 100 words) about a cat,
    based on the topic provided in session state with key 'topic'""",
        input_schema=None,
        output_key="current_story",  # Key for storing output in session state
    )

    critic = LlmAgent(
        name="Critic",
        model=GEMINI_2_FLASH,
        instruction="""You are a story critic. Review the story provided in
    session state with key 'current_story'. Provide 1-2 sentences of constructive criticism
    on how to improve it. Focus on plot or character.""",
        input_schema=None,
        output_key="criticism",  # Key for storing criticism in session state
    )

    reviser = LlmAgent(
        name="Reviser",
        model=GEMINI_2_FLASH,
        instruction="""You are a story reviser. Revise the story provided in
    session state with key 'current_story', based on the criticism in
    session state with key 'criticism'. Output only the revised story.""",
        input_schema=None,
        output_key="current_story",  # Overwrites the original story
    )

    grammar_check = LlmAgent(
        name="GrammarCheck",
        model=GEMINI_2_FLASH,
        instruction="""You are a grammar checker. Check the grammar of the story
    provided in session state with key 'current_story'. Output only the suggested
    corrections as a list, or output 'Grammar is good!' if there are no errors.""",
        input_schema=None,
        output_key="grammar_suggestions",
    )

    tone_check = LlmAgent(
        name="ToneCheck",
        model=GEMINI_2_FLASH,
        instruction="""You are a tone analyzer. Analyze the tone of the story
    provided in session state with key 'current_story'. Output only one word: 'positive' if
    the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
    otherwise.""",
        input_schema=None,
        output_key="tone_check_result", # This agent's output determines the conditional flow
    )
    Part 4: Instantiating and Running the custom agent
    Finally, you instantiate your StoryFlowAgent and use the Runner as usual.


    # --- Create the custom agent instance ---
    story_flow_agent = StoryFlowAgent(
        name="StoryFlowAgent",
        story_generator=story_generator,
        critic=critic,
        reviser=reviser,
        grammar_check=grammar_check,
        tone_check=tone_check,
    )

    # --- Setup Runner and Session ---
    session_service = InMemorySessionService()
    initial_state = {"topic": "a brave kitten exploring a haunted house"}
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state # Pass initial state here
    )
    logger.info(f"Initial session state: {session.state}")

    runner = Runner(
        agent=story_flow_agent, # Pass the custom orchestrator agent
        app_name=APP_NAME,
        session_service=session_service
    )

    # --- Function to Interact with the Agent ---
    def call_agent(user_input_topic: str):
        """
        Sends a new topic to the agent (overwriting the initial one if needed)
        and runs the workflow.
        """
        current_session = session_service.get_session(app_name=APP_NAME, 
                                                    user_id=USER_ID, 
                                                    session_id=SESSION_ID)
        if not current_session:
            logger.error("Session not found!")
            return

        current_session.state["topic"] = user_input_topic
        logger.info(f"Updated session state topic to: {user_input_topic}")

        content = types.Content(role='user', parts=[types.Part(text=f"Generate a story about: {user_input_topic}")])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

        final_response = "No final response captured."
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
                final_response = event.content.parts[0].text

        print("\n--- Agent Interaction Result ---")
        print("Agent Final Response: ", final_response)

        final_session = session_service.get_session(app_name=APP_NAME, 
                                                    user_id=USER_ID, 
                                                    session_id=SESSION_ID)
        print("Final Session State:")
        import json
        print(json.dumps(final_session.state, indent=2))
        print("-------------------------------\n")

    # --- Run the Agent ---
    call_agent("a lonely robot finding a friend in a junkyard")
    (Note: The full runnable code, including imports and execution logic, can be found linked below.)

    Full Code Example
    Storyflow Agent

    # Full runnable code for the StoryFlowAgent example
    import logging
    from typing import AsyncGenerator
    from typing_extensions import override

    from google.adk.agents import LlmAgent, BaseAgent, LoopAgent, SequentialAgent
    from google.adk.agents.invocation_context import InvocationContext
    from google.genai import types
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.adk.events import Event
    from pydantic import BaseModel, Field

    # --- Constants ---
    APP_NAME = "story_app"
    USER_ID = "12345"
    SESSION_ID = "123344"
    GEMINI_2_FLASH = "gemini-2.0-flash"

    # --- Configure Logging ---
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


    # --- Custom Orchestrator Agent ---
    class StoryFlowAgent(BaseAgent):
        """
        Custom agent for a story generation and refinement workflow.

        This agent orchestrates a sequence of LLM agents to generate a story,
        critique it, revise it, check grammar and tone, and potentially
        regenerate the story if the tone is negative.
        """

        # --- Field Declarations for Pydantic ---
        # Declare the agents passed during initialization as class attributes with type hints
        story_generator: LlmAgent
        critic: LlmAgent
        reviser: LlmAgent
        grammar_check: LlmAgent
        tone_check: LlmAgent

        loop_agent: LoopAgent
        sequential_agent: SequentialAgent

        # model_config allows setting Pydantic configurations if needed, e.g., arbitrary_types_allowed
        model_config = {"arbitrary_types_allowed": True}

        def __init__(
            self,
            name: str,
            story_generator: LlmAgent,
            critic: LlmAgent,
            reviser: LlmAgent,
            grammar_check: LlmAgent,
            tone_check: LlmAgent,
        ):
            """
            Initializes the StoryFlowAgent.

            Args:
                name: The name of the agent.
                story_generator: An LlmAgent to generate the initial story.
                critic: An LlmAgent to critique the story.
                reviser: An LlmAgent to revise the story based on criticism.
                grammar_check: An LlmAgent to check the grammar.
                tone_check: An LlmAgent to analyze the tone.
            """
            # Create internal agents *before* calling super().__init__
            loop_agent = LoopAgent(
                name="CriticReviserLoop", sub_agents=[critic, reviser], max_iterations=2
            )
            sequential_agent = SequentialAgent(
                name="PostProcessing", sub_agents=[grammar_check, tone_check]
            )

            # Define the sub_agents list for the framework
            sub_agents_list = [
                story_generator,
                loop_agent,
                sequential_agent,
            ]

            # Pydantic will validate and assign them based on the class annotations.
            super().__init__(
                name=name,
                story_generator=story_generator,
                critic=critic,
                reviser=reviser,
                grammar_check=grammar_check,
                tone_check=tone_check,
                loop_agent=loop_agent,
                sequential_agent=sequential_agent,
                sub_agents=sub_agents_list, # Pass the sub_agents list directly
            )

        @override
        async def _run_async_impl(
            self, ctx: InvocationContext
        ) -> AsyncGenerator[Event, None]:
            """
            Implements the custom orchestration logic for the story workflow.
            Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
            """
            logger.info(f"[{self.name}] Starting story generation workflow.")

            # 1. Initial Story Generation
            logger.info(f"[{self.name}] Running StoryGenerator...")
            async for event in self.story_generator.run_async(ctx):
                logger.info(f"[{self.name}] Event from StoryGenerator: {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event

            # Check if story was generated before proceeding
            if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
                logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
                return # Stop processing if initial story failed

            logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")


            # 2. Critic-Reviser Loop
            logger.info(f"[{self.name}] Running CriticReviserLoop...")
            # Use the loop_agent instance attribute assigned during init
            async for event in self.loop_agent.run_async(ctx):
                logger.info(f"[{self.name}] Event from CriticReviserLoop: {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event

            logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

            # 3. Sequential Post-Processing (Grammar and Tone Check)
            logger.info(f"[{self.name}] Running PostProcessing...")
            # Use the sequential_agent instance attribute assigned during init
            async for event in self.sequential_agent.run_async(ctx):
                logger.info(f"[{self.name}] Event from PostProcessing: {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event

            # 4. Tone-Based Conditional Logic
            tone_check_result = ctx.session.state.get("tone_check_result")
            logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

            if tone_check_result == "negative":
                logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
                async for event in self.story_generator.run_async(ctx):
                    logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
                    yield event
            else:
                logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")
                pass

            logger.info(f"[{self.name}] Workflow finished.")

    # --- Define the individual LLM agents ---
    story_generator = LlmAgent(
        name="StoryGenerator",
        model=GEMINI_2_FLASH,
        instruction="""You are a story writer. Write a short story (around 100 words) about a cat,
    based on the topic provided in session state with key 'topic'""",
        input_schema=None,
        output_key="current_story",  # Key for storing output in session state
    )

    critic = LlmAgent(
        name="Critic",
        model=GEMINI_2_FLASH,
        instruction="""You are a story critic. Review the story provided in
    session state with key 'current_story'. Provide 1-2 sentences of constructive criticism
    on how to improve it. Focus on plot or character.""",
        input_schema=None,
        output_key="criticism",  # Key for storing criticism in session state
    )

    reviser = LlmAgent(
        name="Reviser",
        model=GEMINI_2_FLASH,
        instruction="""You are a story reviser. Revise the story provided in
    session state with key 'current_story', based on the criticism in
    session state with key 'criticism'. Output only the revised story.""",
        input_schema=None,
        output_key="current_story",  # Overwrites the original story
    )

    grammar_check = LlmAgent(
        name="GrammarCheck",
        model=GEMINI_2_FLASH,
        instruction="""You are a grammar checker. Check the grammar of the story
    provided in session state with key 'current_story'. Output only the suggested
    corrections as a list, or output 'Grammar is good!' if there are no errors.""",
        input_schema=None,
        output_key="grammar_suggestions",
    )

    tone_check = LlmAgent(
        name="ToneCheck",
        model=GEMINI_2_FLASH,
        instruction="""You are a tone analyzer. Analyze the tone of the story
    provided in session state with key 'current_story'. Output only one word: 'positive' if
    the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
    otherwise.""",
        input_schema=None,
        output_key="tone_check_result", # This agent's output determines the conditional flow
    )

    # --- Create the custom agent instance ---
    story_flow_agent = StoryFlowAgent(
        name="StoryFlowAgent",
        story_generator=story_generator,
        critic=critic,
        reviser=reviser,
        grammar_check=grammar_check,
        tone_check=tone_check,
    )

    # --- Setup Runner and Session ---
    session_service = InMemorySessionService()
    initial_state = {"topic": "a brave kitten exploring a haunted house"}
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state # Pass initial state here
    )
    logger.info(f"Initial session state: {session.state}")

    runner = Runner(
        agent=story_flow_agent, # Pass the custom orchestrator agent
        app_name=APP_NAME,
        session_service=session_service
    )

    # --- Function to Interact with the Agent ---
    def call_agent(user_input_topic: str):
        """
        Sends a new topic to the agent (overwriting the initial one if needed)
        and runs the workflow.
        """
        current_session = session_service.get_session(app_name=APP_NAME, 
                                                    user_id=USER_ID, 
                                                    session_id=SESSION_ID)
        if not current_session:
            logger.error("Session not found!")
            return

        current_session.state["topic"] = user_input_topic
        logger.info(f"Updated session state topic to: {user_input_topic}")

        content = types.Content(role='user', parts=[types.Part(text=f"Generate a story about: {user_input_topic}")])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

        final_response = "No final response captured."
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
                final_response = event.content.parts[0].text

        print("\n--- Agent Interaction Result ---")
        print("Agent Final Response: ", final_response)

        final_session = session_service.get_session(app_name=APP_NAME, 
                                                    user_id=USER_ID, 
                                                    session_id=SESSION_ID)
        print("Final Session State:")
        import json
        print(json.dumps(final_session.state, indent=2))
        print("-------------------------------\n")

    # --- Run the Agent ---
    call_agent("a lonely robot finding a friend in a junkyard")

### Agent Types Comparison

The following table provides a high-level comparison to help distinguish between the agent types:

| Feature | LLM Agent (`LLMAgent`) | Workflow Agent | Custom Agent (`BaseAgent` subclass) |
|---------|------------------------|----------------|-----------------------------------|
| Primary Function | Reasoning, Generation, Tool Use | Controlling Agent Execution Flow | Implementing Unique Logic/Integrations |
| Core Engine | Large Language Model (LLM) | Predefined Logic (Sequence, Parallel, Loop) | Custom Python Code |
| Determinism | Non-deterministic (Flexible) | Deterministic (Predictable) | Can be either, based on implementation |
| Primary Use | Language tasks, Dynamic decisions | Structured processes, Orchestration | Tailored requirements, Specific workflows |

## Agents Working Together: Multi-Agent Systems

While each agent type serves a distinct purpose, the true power often comes from combining multiple agents to form sophisticated AI applications:

* **LLM Agents** handle intelligent, language-based task execution.
* **Workflow Agents** manage the overall process flow using standard patterns.
* **Custom Agents** provide specialized capabilities or rules needed for unique integrations.

Understanding these core types is the first step toward building sophisticated, capable AI applications with ADK.

        As agentic applications grow in complexity, structuring them as a single, monolithic agent can become challenging to develop, maintain, and reason about. The Agent Development Kit (ADK) supports building sophisticated applications by composing multiple, distinct BaseAgent instances into a Multi-Agent System (MAS).

        In ADK, a multi-agent system is an application where different agents, often forming a hierarchy, collaborate or coordinate to achieve a larger goal. Structuring your application this way offers significant advantages, including enhanced modularity, specialization, reusability, maintainability, and the ability to define structured control flows using dedicated workflow agents.

        You can compose various types of agents derived from BaseAgent to build these systems:

        LLM Agents: Agents powered by large language models. (See LLM Agents)
        Workflow Agents: Specialized agents (SequentialAgent, ParallelAgent, LoopAgent) designed to manage the execution flow of their sub-agents. (See Workflow Agents)
        Custom agents: Your own agents inheriting from BaseAgent with specialized, non-LLM logic. (See Custom Agents)
        The following sections detail the core ADK primitives—such as agent hierarchy, workflow agents, and interaction mechanisms—that enable you to construct and manage these multi-agent systems effectively.

        2. ADK Primitives for Agent Composition
        ADK provides core building blocks—primitives—that enable you to structure and manage interactions within your multi-agent system.

        2.1. Agent Hierarchy (parent_agent, sub_agents)
        The foundation for structuring multi-agent systems is the parent-child relationship defined in BaseAgent.

        Establishing Hierarchy: You create a tree structure by passing a list of agent instances to the sub_agents argument when initializing a parent agent. ADK automatically sets the parent_agent attribute on each child agent during initialization (google.adk.agents.base_agent.py - model_post_init).
        Single Parent Rule: An agent instance can only be added as a sub-agent once. Attempting to assign a second parent will result in a ValueError.
        Importance: This hierarchy defines the scope for Workflow Agents and influences the potential targets for LLM-Driven Delegation. You can navigate the hierarchy using agent.parent_agent or find descendants using agent.find_agent(name).

        # Conceptual Example: Defining Hierarchy
        from google.adk.agents import LlmAgent, BaseAgent

        # Define individual agents
        greeter = LlmAgent(name="Greeter", model="gemini-2.0-flash")
        task_doer = BaseAgent(name="TaskExecutor") # Custom non-LLM agent

        # Create parent agent and assign children via sub_agents
        coordinator = LlmAgent(
            name="Coordinator",
            model="gemini-2.0-flash",
            description="I coordinate greetings and tasks.",
            sub_agents=[ # Assign sub_agents here
                greeter,
                task_doer
            ]
        )

        # Framework automatically sets:
        # assert greeter.parent_agent == coordinator
        # assert task_doer.parent_agent == coordinator
        2.2. Workflow Agents as Orchestrators
        ADK includes specialized agents derived from BaseAgent that don't perform tasks themselves but orchestrate the execution flow of their sub_agents.

        SequentialAgent: Executes its sub_agents one after another in the order they are listed.

        Context: Passes the same InvocationContext sequentially, allowing agents to easily pass results via shared state.

        # Conceptual Example: Sequential Pipeline
        from google.adk.agents import SequentialAgent, LlmAgent

        step1 = LlmAgent(name="Step1_Fetch", output_key="data") # Saves output to state['data']
        step2 = LlmAgent(name="Step2_Process", instruction="Process data from state key 'data'.")

        pipeline = SequentialAgent(name="MyPipeline", sub_agents=[step1, step2])
        # When pipeline runs, Step2 can access the state['data'] set by Step1.
        ParallelAgent: Executes its sub_agents in parallel. Events from sub-agents may be interleaved.

        Context: Modifies the InvocationContext.branch for each child agent (e.g., ParentBranch.ChildName), providing a distinct contextual path which can be useful for isolating history in some memory implementations.
        State: Despite different branches, all parallel children access the same shared session.state, enabling them to read initial state and write results (use distinct keys to avoid race conditions).

        # Conceptual Example: Parallel Execution
        from google.adk.agents import ParallelAgent, LlmAgent

        fetch_weather = LlmAgent(name="WeatherFetcher", output_key="weather")
        fetch_news = LlmAgent(name="NewsFetcher", output_key="news")

        gatherer = ParallelAgent(name="InfoGatherer", sub_agents=[fetch_weather, fetch_news])
        # When gatherer runs, WeatherFetcher and NewsFetcher run concurrently.
        # A subsequent agent could read state['weather'] and state['news'].
        LoopAgent: Executes its sub_agents sequentially in a loop.

        Termination: The loop stops if the optional max_iterations is reached, or if any sub-agent yields an Event with actions.escalate=True.
        Context & State: Passes the same InvocationContext in each iteration, allowing state changes (e.g., counters, flags) to persist across loops.

        # Conceptual Example: Loop with Condition
        from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
        from google.adk.events import Event, EventActions
        from google.adk.agents.invocation_context import InvocationContext
        from typing import AsyncGenerator

        class CheckCondition(BaseAgent): # Custom agent to check state
            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                status = ctx.session.state.get("status", "pending")
                is_done = (status == "completed")
                yield Event(author=self.name, actions=EventActions(escalate=is_done)) # Escalate if done

        process_step = LlmAgent(name="ProcessingStep") # Agent that might update state['status']

        poller = LoopAgent(
            name="StatusPoller",
            max_iterations=10,
            sub_agents=[process_step, CheckCondition(name="Checker")]
        )
        # When poller runs, it executes process_step then Checker repeatedly
        # until Checker escalates (state['status'] == 'completed') or 10 iterations pass.
        2.3. Interaction & Communication Mechanisms
        Agents within a system often need to exchange data or trigger actions in one another. ADK facilitates this through:

        a) Shared Session State (session.state)
        The most fundamental way for agents operating within the same invocation (and thus sharing the same Session object via the InvocationContext) to communicate passively.

        Mechanism: One agent (or its tool/callback) writes a value (context.state['data_key'] = processed_data), and a subsequent agent reads it (data = context.state.get('data_key')). State changes are tracked via CallbackContext.
        Convenience: The output_key property on LlmAgent automatically saves the agent's final response text (or structured output) to the specified state key.
        Nature: Asynchronous, passive communication. Ideal for pipelines orchestrated by SequentialAgent or passing data across LoopAgent iterations.
        See Also: State Management

        # Conceptual Example: Using output_key and reading state
        from google.adk.agents import LlmAgent, SequentialAgent

        agent_A = LlmAgent(name="AgentA", instruction="Find the capital of France.", output_key="capital_city")
        agent_B = LlmAgent(name="AgentB", instruction="Tell me about the city stored in state key 'capital_city'.")

        pipeline = SequentialAgent(name="CityInfo", sub_agents=[agent_A, agent_B])
        # AgentA runs, saves "Paris" to state['capital_city'].
        # AgentB runs, its instruction processor reads state['capital_city'] to get "Paris".
        b) LLM-Driven Delegation (Agent Transfer)
        Leverages an LlmAgent's understanding to dynamically route tasks to other suitable agents within the hierarchy.

        Mechanism: The agent's LLM generates a specific function call: transfer_to_agent(agent_name='target_agent_name').
        Handling: The AutoFlow, used by default when sub-agents are present or transfer isn't disallowed, intercepts this call. It identifies the target agent using root_agent.find_agent() and updates the InvocationContext to switch execution focus.
        Requires: The calling LlmAgent needs clear instructions on when to transfer, and potential target agents need distinct descriptions for the LLM to make informed decisions. Transfer scope (parent, sub-agent, siblings) can be configured on the LlmAgent.
        Nature: Dynamic, flexible routing based on LLM interpretation.

        # Conceptual Setup: LLM Transfer
        from google.adk.agents import LlmAgent

        booking_agent = LlmAgent(name="Booker", description="Handles flight and hotel bookings.")
        info_agent = LlmAgent(name="Info", description="Provides general information and answers questions.")

        coordinator = LlmAgent(
            name="Coordinator",
            instruction="You are an assistant. Delegate booking tasks to Booker and info requests to Info.",
            description="Main coordinator.",
            # AutoFlow is typically used implicitly here
            sub_agents=[booking_agent, info_agent]
        )
        # If coordinator receives "Book a flight", its LLM should generate:
        # FunctionCall(name='transfer_to_agent', args={'agent_name': 'Booker'})
        # ADK framework then routes execution to booking_agent.
        c) Explicit Invocation (AgentTool)
        Allows an LlmAgent to treat another BaseAgent instance as a callable function or Tool.

        Mechanism: Wrap the target agent instance in AgentTool and include it in the parent LlmAgent's tools list. AgentTool generates a corresponding function declaration for the LLM.
        Handling: When the parent LLM generates a function call targeting the AgentTool, the framework executes AgentTool.run_async. This method runs the target agent, captures its final response, forwards any state/artifact changes back to the parent's context, and returns the response as the tool's result.
        Nature: Synchronous (within the parent's flow), explicit, controlled invocation like any other tool.
        (Note: AgentTool needs to be imported and used explicitly).

        # Conceptual Setup: Agent as a Tool
        from google.adk.agents import LlmAgent, BaseAgent
        from google.adk.tools import agent_tool
        from pydantic import BaseModel

        # Define a target agent (could be LlmAgent or custom BaseAgent)
        class ImageGeneratorAgent(BaseAgent): # Example custom agent
            name: str = "ImageGen"
            description: str = "Generates an image based on a prompt."
            # ... internal logic ...
            async def _run_async_impl(self, ctx): # Simplified run logic
                prompt = ctx.session.state.get("image_prompt", "default prompt")
                # ... generate image bytes ...
                image_bytes = b"..."
                yield Event(author=self.name, content=types.Content(parts=[types.Part.from_bytes(image_bytes, "image/png")]))

        image_agent = ImageGeneratorAgent()
        image_tool = agent_tool.AgentTool(agent=image_agent) # Wrap the agent

        # Parent agent uses the AgentTool
        artist_agent = LlmAgent(
            name="Artist",
            model="gemini-2.0-flash",
            instruction="Create a prompt and use the ImageGen tool to generate the image.",
            tools=[image_tool] # Include the AgentTool
        )
        # Artist LLM generates a prompt, then calls:
        # FunctionCall(name='ImageGen', args={'image_prompt': 'a cat wearing a hat'})
        # Framework calls image_tool.run_async(...), which runs ImageGeneratorAgent.
        # The resulting image Part is returned to the Artist agent as the tool result.
        These primitives provide the flexibility to design multi-agent interactions ranging from tightly coupled sequential workflows to dynamic, LLM-driven delegation networks.

        3. Common Multi-Agent Patterns using ADK Primitives
        By combining ADK's composition primitives, you can implement various established patterns for multi-agent collaboration.

        Coordinator/Dispatcher Pattern
        Structure: A central LlmAgent (Coordinator) manages several specialized sub_agents.
        Goal: Route incoming requests to the appropriate specialist agent.
        ADK Primitives Used:
        Hierarchy: Coordinator has specialists listed in sub_agents.
        Interaction: Primarily uses LLM-Driven Delegation (requires clear descriptions on sub-agents and appropriate instruction on Coordinator) or Explicit Invocation (AgentTool) (Coordinator includes AgentTool-wrapped specialists in its tools).

        # Conceptual Code: Coordinator using LLM Transfer
        from google.adk.agents import LlmAgent

        billing_agent = LlmAgent(name="Billing", description="Handles billing inquiries.")
        support_agent = LlmAgent(name="Support", description="Handles technical support requests.")

        coordinator = LlmAgent(
            name="HelpDeskCoordinator",
            model="gemini-2.0-flash",
            instruction="Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
            description="Main help desk router.",
            # allow_transfer=True is often implicit with sub_agents in AutoFlow
            sub_agents=[billing_agent, support_agent]
        )
        # User asks "My payment failed" -> Coordinator's LLM should call transfer_to_agent(agent_name='Billing')
        # User asks "I can't log in" -> Coordinator's LLM should call transfer_to_agent(agent_name='Support')
        Sequential Pipeline Pattern
        Structure: A SequentialAgent contains sub_agents executed in a fixed order.
        Goal: Implement a multi-step process where the output of one step feeds into the next.
        ADK Primitives Used:
        Workflow: SequentialAgent defines the order.
        Communication: Primarily uses Shared Session State. Earlier agents write results (often via output_key), later agents read those results from context.state.

        # Conceptual Code: Sequential Data Pipeline
        from google.adk.agents import SequentialAgent, LlmAgent

        validator = LlmAgent(name="ValidateInput", instruction="Validate the input.", output_key="validation_status")
        processor = LlmAgent(name="ProcessData", instruction="Process data if state key 'validation_status' is 'valid'.", output_key="result")
        reporter = LlmAgent(name="ReportResult", instruction="Report the result from state key 'result'.")

        data_pipeline = SequentialAgent(
            name="DataPipeline",
            sub_agents=[validator, processor, reporter]
        )
        # validator runs -> saves to state['validation_status']
        # processor runs -> reads state['validation_status'], saves to state['result']
        # reporter runs -> reads state['result']
        Parallel Fan-Out/Gather Pattern
        Structure: A ParallelAgent runs multiple sub_agents concurrently, often followed by a later agent (in a SequentialAgent) that aggregates results.
        Goal: Execute independent tasks simultaneously to reduce latency, then combine their outputs.
        ADK Primitives Used:
        Workflow: ParallelAgent for concurrent execution (Fan-Out). Often nested within a SequentialAgent to handle the subsequent aggregation step (Gather).
        Communication: Sub-agents write results to distinct keys in Shared Session State. The subsequent "Gather" agent reads multiple state keys.

        # Conceptual Code: Parallel Information Gathering
        from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent

        fetch_api1 = LlmAgent(name="API1Fetcher", instruction="Fetch data from API 1.", output_key="api1_data")
        fetch_api2 = LlmAgent(name="API2Fetcher", instruction="Fetch data from API 2.", output_key="api2_data")

        gather_concurrently = ParallelAgent(
            name="ConcurrentFetch",
            sub_agents=[fetch_api1, fetch_api2]
        )

        synthesizer = LlmAgent(
            name="Synthesizer",
            instruction="Combine results from state keys 'api1_data' and 'api2_data'."
        )

        overall_workflow = SequentialAgent(
            name="FetchAndSynthesize",
            sub_agents=[gather_concurrently, synthesizer] # Run parallel fetch, then synthesize
        )
        # fetch_api1 and fetch_api2 run concurrently, saving to state.
        # synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].
        Hierarchical Task Decomposition
        Structure: A multi-level tree of agents where higher-level agents break down complex goals and delegate sub-tasks to lower-level agents.
        Goal: Solve complex problems by recursively breaking them down into simpler, executable steps.
        ADK Primitives Used:
        Hierarchy: Multi-level parent_agent/sub_agents structure.
        Interaction: Primarily LLM-Driven Delegation or Explicit Invocation (AgentTool) used by parent agents to assign tasks to children. Results are returned up the hierarchy (via tool responses or state).

        # Conceptual Code: Hierarchical Research Task
        from google.adk.agents import LlmAgent
        from google.adk.tools import agent_tool

        # Low-level tool-like agents
        web_searcher = LlmAgent(name="WebSearch", description="Performs web searches for facts.")
        summarizer = LlmAgent(name="Summarizer", description="Summarizes text.")

        # Mid-level agent combining tools
        research_assistant = LlmAgent(
            name="ResearchAssistant",
            model="gemini-2.0-flash",
            description="Finds and summarizes information on a topic.",
            tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
        )

        # High-level agent delegating research
        report_writer = LlmAgent(
            name="ReportWriter",
            model="gemini-2.0-flash",
            instruction="Write a report on topic X. Use the ResearchAssistant to gather information.",
            tools=[agent_tool.AgentTool(agent=research_assistant)]
            # Alternatively, could use LLM Transfer if research_assistant is a sub_agent
        )
        # User interacts with ReportWriter.
        # ReportWriter calls ResearchAssistant tool.
        # ResearchAssistant calls WebSearch and Summarizer tools.
        # Results flow back up.
        Review/Critique Pattern (Generator-Critic)
        Structure: Typically involves two agents within a SequentialAgent: a Generator and a Critic/Reviewer.
        Goal: Improve the quality or validity of generated output by having a dedicated agent review it.
        ADK Primitives Used:
        Workflow: SequentialAgent ensures generation happens before review.
        Communication: Shared Session State (Generator uses output_key to save output; Reviewer reads that state key). The Reviewer might save its feedback to another state key for subsequent steps.

        # Conceptual Code: Generator-Critic
        from google.adk.agents import SequentialAgent, LlmAgent

        generator = LlmAgent(
            name="DraftWriter",
            instruction="Write a short paragraph about subject X.",
            output_key="draft_text"
        )

        reviewer = LlmAgent(
            name="FactChecker",
            instruction="Review the text in state key 'draft_text' for factual accuracy. Output 'valid' or 'invalid' with reasons.",
            output_key="review_status"
        )

        # Optional: Further steps based on review_status

        review_pipeline = SequentialAgent(
            name="WriteAndReview",
            sub_agents=[generator, reviewer]
        )
        # generator runs -> saves draft to state['draft_text']
        # reviewer runs -> reads state['draft_text'], saves status to state['review_status']
        Iterative Refinement Pattern
        Structure: Uses a LoopAgent containing one or more agents that work on a task over multiple iterations.
        Goal: Progressively improve a result (e.g., code, text, plan) stored in the session state until a quality threshold is met or a maximum number of iterations is reached.
        ADK Primitives Used:
        Workflow: LoopAgent manages the repetition.
        Communication: Shared Session State is essential for agents to read the previous iteration's output and save the refined version.
        Termination: The loop typically ends based on max_iterations or a dedicated checking agent setting actions.escalate=True when the result is satisfactory.

        # Conceptual Code: Iterative Code Refinement
        from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
        from google.adk.events import Event, EventActions
        from google.adk.agents.invocation_context import InvocationContext
        from typing import AsyncGenerator

        # Agent to generate/refine code based on state['current_code'] and state['requirements']
        code_refiner = LlmAgent(
            name="CodeRefiner",
            instruction="Read state['current_code'] (if exists) and state['requirements']. Generate/refine Python code to meet requirements. Save to state['current_code'].",
            output_key="current_code" # Overwrites previous code in state
        )

        # Agent to check if the code meets quality standards
        quality_checker = LlmAgent(
            name="QualityChecker",
            instruction="Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.",
            output_key="quality_status"
        )

        # Custom agent to check the status and escalate if 'pass'
        class CheckStatusAndEscalate(BaseAgent):
            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                status = ctx.session.state.get("quality_status", "fail")
                should_stop = (status == "pass")
                yield Event(author=self.name, actions=EventActions(escalate=should_stop))

        refinement_loop = LoopAgent(
            name="CodeRefinementLoop",
            max_iterations=5,
            sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
        )
        # Loop runs: Refiner -> Checker -> StopChecker
        # State['current_code'] is updated each iteration.
        # Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
        Human-in-the-Loop Pattern
        Structure: Integrates human intervention points within an agent workflow.
        Goal: Allow for human oversight, approval, correction, or tasks that AI cannot perform.
        ADK Primitives Used (Conceptual):
        Interaction: Can be implemented using a custom Tool that pauses execution and sends a request to an external system (e.g., a UI, ticketing system) waiting for human input. The tool then returns the human's response to the agent.
        Workflow: Could use LLM-Driven Delegation (transfer_to_agent) targeting a conceptual "Human Agent" that triggers the external workflow, or use the custom tool within an LlmAgent.
        State/Callbacks: State can hold task details for the human; callbacks can manage the interaction flow.
        Note: ADK doesn't have a built-in "Human Agent" type, so this requires custom integration.

        # Conceptual Code: Using a Tool for Human Approval
        from google.adk.agents import LlmAgent, SequentialAgent
        from google.adk.tools import FunctionTool

        # --- Assume external_approval_tool exists ---
        # This tool would:
        # 1. Take details (e.g., request_id, amount, reason).
        # 2. Send these details to a human review system (e.g., via API).
        # 3. Poll or wait for the human response (approved/rejected).
        # 4. Return the human's decision.
        # async def external_approval_tool(amount: float, reason: str) -> str: ...
        approval_tool = FunctionTool(func=external_approval_tool)

        # Agent that prepares the request
        prepare_request = LlmAgent(
            name="PrepareApproval",
            instruction="Prepare the approval request details based on user input. Store amount and reason in state.",
            # ... likely sets state['approval_amount'] and state['approval_reason'] ...
        )

        # Agent that calls the human approval tool
        request_approval = LlmAgent(
            name="RequestHumanApproval",
            instruction="Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].",
            tools=[approval_tool],
            output_key="human_decision"
        )

        # Agent that proceeds based on human decision
        process_decision = LlmAgent(
            name="ProcessDecision",
            instruction="Check state key 'human_decision'. If 'approved', proceed. If 'rejected', inform user."
        )

        approval_workflow = SequentialAgent(
            name="HumanApprovalWorkflow",
            sub_agents=[prepare_request, request_approval, process_decision]
        )
        These patterns provide starting points for structuring your multi-agent systems. You can mix and match them as needed to create the most effective architecture for your specific application.

## What's Next?

Now that you have an overview of the different agent types available in ADK, dive deeper into how they work and how to use them effectively:

* **LLM Agents**: Explore how to configure agents powered by large language models, including setting instructions, providing tools, and enabling advanced features like planning and code execution.

* **Workflow Agents**: Learn how to orchestrate tasks using `SequentialAgent`, `ParallelAgent`, and `LoopAgent` for structured and predictable processes.

* **Custom Agents**: Discover the principles of extending `BaseAgent` to build agents with unique logic and integrations tailored to your specific needs.

# Tools

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

1. **Function Tools:** Tools created by you, tailored to your specific application's needs.
        What are function tools?
        When out-of-the-box tools don't fully meet specific requirements, developers can create custom function tools. This allows for tailored functionality, such as connecting to proprietary databases or implementing unique algorithms.

        For example, a function tool, "myfinancetool", might be a function that calculates a specific financial metric. ADK also supports long running functions, so if that calculation takes a while, the agent can continue working on other tasks.

        ADK offers several ways to create functions tools, each suited to different levels of complexity and control:

        Function Tool
        Long Running Function Tool
        Agents-as-a-Tool
        1. Function Tool
        Transforming a function into a tool is a straightforward way to integrate custom logic into your agents. This approach offers flexibility and quick integration.

        Parameters
        Define your function parameters using standard JSON-serializable types (e.g., string, integer, list, dictionary). It's important to avoid setting default values for parameters, as the language model (LLM) does not currently support interpreting them.

        Return Type
        The preferred return type for a Python Function Tool is a dictionary. This allows you to structure the response with key-value pairs, providing context and clarity to the LLM. If your function returns a type other than a dictionary, the framework automatically wraps it into a dictionary with a single key named "result".

        Strive to make your return values as descriptive as possible. For example, instead of returning a numeric error code, return a dictionary with an "error_message" key containing a human-readable explanation. Remember that the LLM, not a piece of code, needs to understand the result. As a best practice, include a "status" key in your return dictionary to indicate the overall outcome (e.g., "success", "error", "pending"), providing the LLM with a clear signal about the operation's state.

        Docstring
        The docstring of your function serves as the tool's description and is sent to the LLM. Therefore, a well-written and comprehensive docstring is crucial for the LLM to understand how to use the tool effectively. Clearly explain the purpose of the function, the meaning of its parameters, and the expected return values.

        Example
        Best Practices
        While you have considerable flexibility in defining your function, remember that simplicity enhances usability for the LLM. Consider these guidelines:

        Fewer Parameters are Better: Minimize the number of parameters to reduce complexity.
        Simple Data Types: Favor primitive data types like str and int over custom classes whenever possible.
        Meaningful Names: The function's name and parameter names significantly influence how the LLM interprets and utilizes the tool. Choose names that clearly reflect the function's purpose and the meaning of its inputs. Avoid generic names like do_stuff().
        2. Long Running Function Tool
        Designed for tasks that require a significant amount of processing time without blocking the agent's execution. This tool is a subclass of FunctionTool.

        When using a LongRunningFunctionTool, your Python function can initiate the long-running operation and optionally return an intermediate result to keep the model and user informed about the progress. The agent can then continue with other tasks. An example is the human-in-the-loop scenario where the agent needs human approval before proceeding with a task.

        How it Works
        You wrap a Python generator function (a function using yield) with LongRunningFunctionTool.

        Initiation: When the LLM calls the tool, your generator function starts executing.

        Intermediate Updates (yield): Your function should yield intermediate Python objects (typically dictionaries) periodically to report progress. The ADK framework takes each yielded value and sends it back to the LLM packaged within a FunctionResponse. This allows the LLM to inform the user (e.g., status, percentage complete, messages).

        Completion (return): When the task is finished, the generator function uses return to provide the final Python object result.

        Framework Handling: The ADK framework manages the execution. It sends each yielded value back as an intermediate FunctionResponse. When the generator completes, the framework sends the returned value as the content of the final FunctionResponse, signaling the end of the long-running operation to the LLM.

        Creating the Tool
        Define your generator function and wrap it using the LongRunningFunctionTool class:


        from google.adk.tools import LongRunningFunctionTool

        # Define your generator function (see example below)
        def my_long_task_generator(*args, **kwargs):
            # ... setup ...
            yield {"status": "pending", "message": "Starting task..."} # Framework sends this as FunctionResponse
            # ... perform work incrementally ...
            yield {"status": "pending", "progress": 50}               # Framework sends this as FunctionResponse
            # ... finish work ...
            return {"status": "completed", "result": "Final outcome"} # Framework sends this as final FunctionResponse

        # Wrap the function
        my_tool = LongRunningFunctionTool(func=my_long_task_generator)
        Intermediate Updates
        Yielding structured Python objects (like dictionaries) is crucial for providing meaningful updates. Include keys like:

        status: e.g., "pending", "running", "waiting_for_input"

        progress: e.g., percentage, steps completed

        message: Descriptive text for the user/LLM

        estimated_completion_time: If calculable

        Each value you yield is packaged into a FunctionResponse by the framework and sent to the LLM.

        Final Result
        The Python object your generator function returns is considered the final result of the tool execution. The framework packages this value (even if it's None) into the content of the final FunctionResponse sent back to the LLM, indicating the tool execution is complete.

        Example: File Processing Simulation
        Key aspects of this example
        process_large_file: This generator simulates a lengthy operation, yielding intermediate status/progress dictionaries.

        LongRunningFunctionTool: Wraps the generator; the framework handles sending yielded updates and the final return value as sequential FunctionResponses.

        Agent instruction: Directs the LLM to use the tool and understand the incoming FunctionResponse stream (progress vs. completion) for user updates.

        Final return: The function returns the final result dictionary, which is sent in the concluding FunctionResponse to indicate completion.

        3. Agent-as-a-Tool
        This powerful feature allows you to leverage the capabilities of other agents within your system by calling them as tools. The Agent-as-a-Tool enables you to invoke another agent to perform a specific task, effectively delegating responsibility. This is conceptually similar to creating a Python function that calls another agent and uses the agent's response as the function's return value.

        Key difference from sub-agents
        It's important to distinguish an Agent-as-a-Tool from a Sub-Agent.

        Agent-as-a-Tool: When Agent A calls Agent B as a tool (using Agent-as-a-Tool), Agent B's answer is passed back to Agent A, which then summarizes the answer and generates a response to the user. Agent A retains control and continues to handle future user input.

        Sub-agent: When Agent A calls Agent B as a sub-agent, the responsibility of answering the user is completely transferred to Agent B. Agent A is effectively out of the loop. All subsequent user input will be answered by Agent B.

        Usage
        To use an agent as a tool, wrap the agent with the AgentTool class.


        tools=[AgentTool(agent=agent_b)]
        Customization
        The AgentTool class provides the following attributes for customizing its behavior:

        skip_summarization: bool: If set to True, the framework will bypass the LLM-based summarization of the tool agent's response. This can be useful when the tool's response is already well-formatted and requires no further processing.
        Example
        How it works
        When the main_agent receives the long text, its instruction tells it to use the 'summarize' tool for long texts.
        The framework recognizes 'summarize' as an AgentTool that wraps the summary_agent.
        Behind the scenes, the main_agent will call the summary_agent with the long text as input.
        The summary_agent will process the text according to its instruction and generate a summary.
        The response from the summary_agent is then passed back to the main_agent.
        The main_agent can then take the summary and formulate its final response to the user (e.g., "Here's a summary of the text: ...")

   * **Functions/Methods:** Define standard synchronous functions or methods in your code (e.g., Python def).
        Transforming a function into a tool is a straightforward way to integrate custom logic into your agents. This approach offers flexibility and quick integration.

        Parameters
        Define your function parameters using standard JSON-serializable types (e.g., string, integer, list, dictionary). It's important to avoid setting default values for parameters, as the language model (LLM) does not currently support interpreting them.

        Return Type
        The preferred return type for a Python Function Tool is a dictionary. This allows you to structure the response with key-value pairs, providing context and clarity to the LLM. If your function returns a type other than a dictionary, the framework automatically wraps it into a dictionary with a single key named "result".

        Strive to make your return values as descriptive as possible. For example, instead of returning a numeric error code, return a dictionary with an "error_message" key containing a human-readable explanation. Remember that the LLM, not a piece of code, needs to understand the result. As a best practice, include a "status" key in your return dictionary to indicate the overall outcome (e.g., "success", "error", "pending"), providing the LLM with a clear signal about the operation's state.

        Docstring
        The docstring of your function serves as the tool's description and is sent to the LLM. Therefore, a well-written and comprehensive docstring is crucial for the LLM to understand how to use the tool effectively. Clearly explain the purpose of the function, the meaning of its parameters, and the expected return values.

        Example
        Best Practices
        While you have considerable flexibility in defining your function, remember that simplicity enhances usability for the LLM. Consider these guidelines:

        Fewer Parameters are Better: Minimize the number of parameters to reduce complexity.
        Simple Data Types: Favor primitive data types like str and int over custom classes whenever possible.
        Meaningful Names: The function's name and parameter names significantly influence how the LLM interprets and utilizes the tool. Choose names that clearly reflect the function's purpose and the meaning of its inputs. Avoid generic names like do_stuff().
        2. Long Running Function Tool
        Designed for tasks that require a significant amount of processing time without blocking the agent's execution. This tool is a subclass of FunctionTool.

        When using a LongRunningFunctionTool, your Python function can initiate the long-running operation and optionally return an intermediate result to keep the model and user informed about the progress. The agent can then continue with other tasks. An example is the human-in-the-loop scenario where the agent needs human approval before proceeding with a task.

        How it Works
        You wrap a Python generator function (a function using yield) with LongRunningFunctionTool.

        Initiation: When the LLM calls the tool, your generator function starts executing.

        Intermediate Updates (yield): Your function should yield intermediate Python objects (typically dictionaries) periodically to report progress. The ADK framework takes each yielded value and sends it back to the LLM packaged within a FunctionResponse. This allows the LLM to inform the user (e.g., status, percentage complete, messages).

        Completion (return): When the task is finished, the generator function uses return to provide the final Python object result.

        Framework Handling: The ADK framework manages the execution. It sends each yielded value back as an intermediate FunctionResponse. When the generator completes, the framework sends the returned value as the content of the final FunctionResponse, signaling the end of the long-running operation to the LLM.

        Creating the Tool
        Define your generator function and wrap it using the LongRunningFunctionTool class:


        from google.adk.tools import LongRunningFunctionTool

        # Define your generator function (see example below)
        def my_long_task_generator(*args, **kwargs):
            # ... setup ...
            yield {"status": "pending", "message": "Starting task..."} # Framework sends this as FunctionResponse
            # ... perform work incrementally ...
            yield {"status": "pending", "progress": 50}               # Framework sends this as FunctionResponse
            # ... finish work ...
            return {"status": "completed", "result": "Final outcome"} # Framework sends this as final FunctionResponse

        # Wrap the function
        my_tool = LongRunningFunctionTool(func=my_long_task_generator)
        Intermediate Updates
        Yielding structured Python objects (like dictionaries) is crucial for providing meaningful updates. Include keys like:

        status: e.g., "pending", "running", "waiting_for_input"

        progress: e.g., percentage, steps completed

        message: Descriptive text for the user/LLM

        estimated_completion_time: If calculable

        Each value you yield is packaged into a FunctionResponse by the framework and sent to the LLM.

        Final Result
        The Python object your generator function returns is considered the final result of the tool execution. The framework packages this value (even if it's None) into the content of the final FunctionResponse sent back to the LLM, indicating the tool execution is complete.

        Example: File Processing Simulation
        Key aspects of this example
        process_large_file: This generator simulates a lengthy operation, yielding intermediate status/progress dictionaries.

        LongRunningFunctionTool: Wraps the generator; the framework handles sending yielded updates and the final return value as sequential FunctionResponses.

        Agent instruction: Directs the LLM to use the tool and understand the incoming FunctionResponse stream (progress vs. completion) for user updates.

        Final return: The function returns the final result dictionary, which is sent in the concluding FunctionResponse to indicate completion.

        3. Agent-as-a-Tool
        This powerful feature allows you to leverage the capabilities of other agents within your system by calling them as tools. The Agent-as-a-Tool enables you to invoke another agent to perform a specific task, effectively delegating responsibility. This is conceptually similar to creating a Python function that calls another agent and uses the agent's response as the function's return value.

        Key difference from sub-agents
        It's important to distinguish an Agent-as-a-Tool from a Sub-Agent.

        Agent-as-a-Tool: When Agent A calls Agent B as a tool (using Agent-as-a-Tool), Agent B's answer is passed back to Agent A, which then summarizes the answer and generates a response to the user. Agent A retains control and continues to handle future user input.

        Sub-agent: When Agent A calls Agent B as a sub-agent, the responsibility of answering the user is completely transferred to Agent B. Agent A is effectively out of the loop. All subsequent user input will be answered by Agent B.

        Usage
        To use an agent as a tool, wrap the agent with the AgentTool class.


        tools=[AgentTool(agent=agent_b)]
        Customization
        The AgentTool class provides the following attributes for customizing its behavior:

        skip_summarization: bool: If set to True, the framework will bypass the LLM-based summarization of the tool agent's response. This can be useful when the tool's response is already well-formatted and requires no further processing.
        Example
        How it works
        When the main_agent receives the long text, its instruction tells it to use the 'summarize' tool for long texts.
        The framework recognizes 'summarize' as an AgentTool that wraps the summary_agent.
        Behind the scenes, the main_agent will call the summary_agent with the long text as input.
        The summary_agent will process the text according to its instruction and generate a summary.
        The response from the summary_agent is then passed back to the main_agent.
        The main_agent can then take the summary and formulate its final response to the user (e.g., "Here's a summary of the text: ...")
   * **Agents as Tools:** Use another, potentially specialized, agent as a tool for a parent agent.
   * **Long Running Function Tools:** Support for tools that perform asynchronous operations or take significant time to complete.

2. **Built-in Tools:** Ready-to-use tools provided by the framework for common tasks. Examples: Google Search, Code Execution, Retrieval-Augmented Generation (RAG).

3. **Third-Party Tools:** Integrate tools seamlessly from popular external libraries. Examples: LangChain Tools, CrewAI Tools.

Navigate to the respective documentation pages linked above for detailed information and examples for each tool type.

## Third Party Tools

ADK is designed to be highly extensible, allowing you to seamlessly integrate tools from other AI Agent frameworks like CrewAI and LangChain. This interoperability is crucial because it allows for faster development time and enables you to reuse existing tools.

### 1. Using LangChain Tools

ADK provides the `LangchainTool` wrapper to integrate tools from the LangChain ecosystem into your agents.

#### Example: Web Search using LangChain's Tavily tool

Tavily provides a search API that returns answers derived from real-time search results, intended for use by applications like AI agents.

```python
from google.adk.agents import Agent
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import TavilySearchResults

# Create the LangChain tool
tavily_search = TavilySearchResults(max_results=3, api_key="your-tavily-api-key")

# Wrap it for use with ADK
wrapped_tavily = LangchainTool(tavily_search)

# Create an agent with the wrapped tool
search_agent = Agent(
    name="web_search_agent",
    model="gemini-2.0-flash",
    instruction="Help users find information by searching the web when needed.",
    tools=[wrapped_tavily]
)

# Example usage
response = search_agent.run("What are the latest developments in quantum computing?")
print(response.text)
```

### 2. Using CrewAI Tools

Similar to LangChain, you can integrate tools from the CrewAI ecosystem:

```python
from google.adk.agents import Agent
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import WebsiteSearchTool

# Create the CrewAI tool
website_search = WebsiteSearchTool()

# Wrap it for use with ADK
wrapped_website_search = CrewaiTool(website_search)

# Create an agent with the wrapped tool
website_agent = Agent(
    name="website_search_agent",
    model="gemini-2.0-flash",
    instruction="Search websites for specific information when users request it.",
    tools=[wrapped_website_search]
)
```

### 3. Custom Tool Wrappers

You can also create custom wrappers for tools from other frameworks by implementing the appropriate adapter pattern:

```python
from google.adk.agents import BaseTool
from some_other_framework import ExternalTool

class CustomToolWrapper(BaseTool):
    """Wrapper for tools from another framework."""
    
    def __init__(self, external_tool):
        self.external_tool = external_tool
        
    def run(self, **kwargs):
        # Convert ADK format to the external tool's format
        external_result = self.external_tool.execute(**kwargs)
        
        # Convert the result back to ADK's expected format
        return {
            "status": "success",
            "result": external_result
        }
        
    def get_schema(self):
        # Define the schema based on the external tool
        return {
            "name": self.external_tool.name,
            "description": self.external_tool.description,
            "parameters": {
                # Map external tool parameters to ADK format
            }
        }
```

### Benefits of Tool Integration

Using third-party tools with ADK offers several advantages:

1. **Expanding Capabilities**: Access specialized tools without having to build them from scratch.
2. **Ecosystem Compatibility**: Work with established AI agent ecosystems and their community-developed tools.
3. **Faster Development**: Reduce development time by leveraging existing implementations.
4. **Best-of-Breed Approach**: Select the best tools from different frameworks for your specific use case.

## Google Cloud Tools

ADK provides seamless integration with Google Cloud services, allowing your agents to leverage Google's cloud infrastructure and AI capabilities.

### 1. Google Search

Access Google Search directly from your agents:

```python
from google.adk.agents import Agent
from google.adk.tools.google_search import GoogleSearch

# Create a Google Search tool
# Note: Requires proper API key setup
search_tool = GoogleSearch(api_key="YOUR_API_KEY", cse_id="YOUR_CSE_ID")

# Create an agent with the search tool
search_agent = Agent(
    name="google_search_agent",
    model="gemini-2.0-flash",
    instruction="Search for information on Google when users ask questions.",
    tools=[search_tool]
)

# Example usage
response = search_agent.run("What is the capital of France?")
```

### 2. Vertex AI Integration

Connect to Vertex AI services for advanced ML capabilities:

```python
from google.adk.agents import Agent
from google.adk.tools.vertex import VertexEndpointPredictor

# Create a tool that calls a deployed Vertex AI model endpoint
vertex_predictor = VertexEndpointPredictor(
    project="your-gcp-project",
    location="us-central1",
    endpoint_id="your-endpoint-id"
)

# Create an agent with the Vertex AI tool
specialized_agent = Agent(
    name="ml_prediction_agent",
    model="gemini-2.0-flash",
    instruction="Help users get predictions from our specialized ML model.",
    tools=[vertex_predictor]
)
```

### 3. BigQuery Integration

Query data from BigQuery tables:

```python
from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryTool

# Create a BigQuery tool
bq_tool = BigQueryTool(
    project="your-gcp-project",
    location="US"
)

# Create a data analysis agent
data_agent = Agent(
    name="data_analysis_agent",
    model="gemini-2.0-flash",
    instruction="""
    You help users analyze data from our BigQuery tables.
    When users ask about data, use the BigQuery tool to run SQL queries.
    Format results in a readable way.
    """,
    tools=[bq_tool]
)
```

## MCP Tools

MCP (Model Context Protocol) tools allow your agents to interact with external services through a standardized protocol.

### What are MCP Servers?

MCP servers provide tools and resources to agents, enabling them to access external APIs, databases, or services without needing to implement complex integration code.

### Setting Up MCP Tools

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

### Example MCP Tools

MCP tools can provide various functionalities:

1. **External API Access**: Connect to third-party APIs like weather services, financial data providers, or news sources.
2. **Database Connections**: Query databases or knowledge bases.
3. **File System Access**: Read and write files in controlled environments.
4. **Specialized Computation**: Perform complex calculations or run specialized algorithms.

## OpenAPI Tools

ADK supports generating tools from OpenAPI specifications, allowing you to quickly integrate with any API that provides an OpenAPI definition.

### Creating Tools from OpenAPI Specs

```python
from google.adk.agents import Agent
from google.adk.tools.openapi import create_openapi_tools

# Create tools from an OpenAPI specification
weather_api_tools = create_openapi_tools(
    spec_path="path/to/weather_api_openapi.yaml",
    base_url="https://api.weather.com",
    headers={"Authorization": f"Bearer {api_key}"}
)

# Create an agent with the OpenAPI tools
api_agent = Agent(
    name="weather_api_agent",
    model="gemini-2.0-flash",
    instruction="Help users get weather information using the Weather API.",
    tools=weather_api_tools
)
```

### Benefits of OpenAPI Tools

1. **Rapid Integration**: Quickly add support for new APIs without writing custom tool code.
2. **Standardization**: Leverage the industry-standard OpenAPI specification format.
3. **Comprehensive Coverage**: Automatically generate tools for all endpoints defined in the API spec.
4. **Documentation**: Inherit parameter descriptions and other documentation from the OpenAPI spec.

### Authenticating with Tools


            Core Concepts
        Many tools need to access protected resources (like user data in Google Calendar, Salesforce records, etc.) and require authentication. ADK provides a system to handle various authentication methods securely.

        The key components involved are:

        AuthScheme: Defines how an API expects authentication credentials (e.g., as an API Key in a header, an OAuth 2.0 Bearer token). ADK supports the same types of authentication schemes as OpenAPI 3.0. To know more about what each type of credential is, refer to OpenAPI doc: Authentication. ADK uses specific classes like APIKey, HTTPBearer, OAuth2, OpenIdConnectWithConfig.
        AuthCredential: Holds the initial information needed to start the authentication process (e.g., your application's OAuth Client ID/Secret, an API key value). It includes an auth_type (like API_KEY, OAUTH2, SERVICE_ACCOUNT) specifying the credential type.
        The general flow involves providing these details when configuring a tool. ADK then attempts to automatically exchange the initial credential for a usable one (like an access token) before the tool makes an API call. For flows requiring user interaction (like OAuth consent), a specific interactive process involving the Agent Client application is triggered.

        Supported Initial Credential Types
        API_KEY: For simple key/value authentication. Usually requires no exchange.
        HTTP: Can represent Basic Auth (not recommended/supported for exchange) or already obtained Bearer tokens. If it's a Bearer token, no exchange is needed.
        OAUTH2: For standard OAuth 2.0 flows. Requires configuration (client ID, secret, scopes) and often triggers the interactive flow for user consent.
        OPEN_ID_CONNECT: For authentication based on OpenID Connect. Similar to OAuth2, often requires configuration and user interaction.
        SERVICE_ACCOUNT: For Google Cloud Service Account credentials (JSON key or Application Default Credentials). Typically exchanged for a Bearer token.
        Configuring Authentication on Tools
        You set up authentication when defining your tool:

        RestApiTool / OpenAPIToolset: Pass auth_scheme and auth_credential during initialization

        GoogleApiToolSet Tools: ADK has built-in 1st party tools like Google Calendar, BigQuery etc,. Use the toolset's specific method.

        APIHubToolset / ApplicationIntegrationToolset: Pass auth_scheme and auth_credentialduring initialization, if the API managed in API Hub / provided by Application Integration requires authentication.

        WARNING

        Storing sensitive credentials like access tokens and especially refresh tokens directly in the session state might pose security risks depending on your session storage backend (SessionService) and overall application security posture.

        InMemorySessionService: Suitable for testing and development, but data is lost when the process ends. Less risk as it's transient.
        Database/Persistent Storage: Strongly consider encrypting the token data before storing it in the database using a robust encryption library (like cryptography) and managing encryption keys securely (e.g., using a key management service).
        Secure Secret Stores: For production environments, storing sensitive credentials in a dedicated secret manager (like Google Cloud Secret Manager or HashiCorp Vault) is the most recommended approach. Your tool could potentially store only short-lived access tokens or secure references (not the refresh token itself) in the session state, fetching the necessary secrets from the secure store when needed.
        Journey 1: Building Agentic Applications with Authenticated Tools
        This section focuses on using pre-existing tools (like those from RestApiTool/ OpenAPIToolset, APIHubToolset, GoogleApiToolSet, or custom FunctionTools) that require authentication within your agentic application. Your main responsibility is configuring the tools and handling the client-side part of interactive authentication flows (if required by the tool).

        Authentication

        1. Configuring Tools with Authentication
        When adding an authenticated tool to your agent, you need to provide its required AuthScheme and your application's initial AuthCredential.

        A. Using OpenAPI-based Toolsets (OpenAPIToolset, APIHubToolset, etc.)

        Pass the scheme and credential during toolset initialization. The toolset applies them to all generated tools. Here are few ways to create tools with authentication in ADK.


        API Key
        OAuth2
        Service Account
        OpenID connect
        Create a tool requiring an API Key.


        from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
        from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset
        auth_scheme, auth_credential = token_to_scheme_credential(
        "apikey", "query", "apikey", YOUR_API_KEY_STRING
        )
        sample_api_toolset = APIHubToolset(
        name="sample-api-requiring-api-key",
        description="A tool using an API protected by API Key",
        apihub_resource_name="...",
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
        )

        B. Using Google API Toolsets (e.g., calendar_tool_set)

        These toolsets often have dedicated configuration methods.

        Tip: For how to create a Google OAuth Client ID & Secret, see this guide: Get your Google API Client ID


        # Example: Configuring Google Calendar Tools
        from google.adk.tools.google_api_tool import calendar_tool_set

        client_id = "YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
        client_secret = "YOUR_GOOGLE_OAUTH_CLIENT_SECRET"

        calendar_tools = calendar_tool_set.get_tools()
        for tool in calendar_tools:
            # Use the specific configure method for this tool type
            tool.configure_auth(client_id=client_id, client_secret=client_secret)

        # agent = LlmAgent(..., tools=calendar_tools)
        2. Handling the Interactive OAuth/OIDC Flow (Client-Side)
        If a tool requires user login/consent (typically OAuth 2.0 or OIDC), the ADK framework pauses execution and signals your Agent Client application (the code calling runner.run_async, like your UI backend, CLI app, or Spark job) to handle the user interaction.

        Here's the step-by-step process for your client application:

        Step 1: Run Agent & Detect Auth Request

        Initiate the agent interaction using runner.run_async.
        Iterate through the yielded events.
        Look for a specific event where the agent calls the special function adk_request_credential. This event signals that user interaction is needed. Use helper functions to identify this event and extract necessary information.

        # runner = Runner(...)
        # session = session_service.create_session(...)
        # content = types.Content(...) # User's initial query

        print("\nRunning agent...")
        events_async = runner.run_async(
            session_id=session.id, user_id='user', new_message=content
        )

        auth_request_event_id, auth_config = None, None

        async for event in events_async:
            # Use helper to check for the specific auth request event
            if is_pending_auth_event(event):
                print("--> Authentication required by agent.")
                # Store the ID needed to respond later
                auth_request_event_id = get_function_call_id(event)
                # Get the AuthConfig containing the auth_uri etc.
                auth_config = get_function_call_auth_config(event)
                break # Stop processing events for now, need user interaction

        if not auth_request_event_id:
            print("\nAuth not required or agent finished.")
            # return # Or handle final response if received
        Helper functions helpers.py:


        from google.adk.events import Event
        from google.adk.auth import AuthConfig # Import necessary type

        def is_pending_auth_event(event: Event) -> bool:
        # Checks if the event is the special auth request function call
        return (
            event.content and event.content.parts and event.content.parts[0]
            and event.content.parts[0].function_call
            and event.content.parts[0].function_call.name == 'adk_request_credential'
            # Check if it's marked as long running (optional but good practice)
            and event.long_running_tool_ids
            and event.content.parts[0].function_call.id in event.long_running_tool_ids
        )

        def get_function_call_id(event: Event) -> str:
        # Extracts the ID of the function call (works for any call, including auth)
        if ( event and event.content and event.content.parts and event.content.parts[0]
            and event.content.parts[0].function_call and event.content.parts[0].function_call.id ):
            return event.content.parts[0].function_call.id
        raise ValueError(f'Cannot get function call id from event {event}')

        def get_function_call_auth_config(event: Event) -> AuthConfig:
            # Extracts the AuthConfig object from the arguments of the auth request event
            auth_config_dict = None
            try:
                auth_config_dict = event.content.parts[0].function_call.args.get('auth_config')
                if auth_config_dict and isinstance(auth_config_dict, dict):
                    # Reconstruct the AuthConfig object
                    return AuthConfig.model_validate(auth_config_dict)
                else:
                    raise ValueError("auth_config missing or not a dict in event args")
            except (AttributeError, IndexError, KeyError, TypeError, ValueError) as e:
                raise ValueError(f'Cannot get auth config from event {event}') from e
        Step 2: Redirect User for Authorization

        Get the authorization URL (auth_uri) from the auth_config extracted in the previous step.
        Crucially, append your application's redirect_uri as a query parameter to this auth_uri. This redirect_uri must be pre-registered with your OAuth provider (e.g., Google Cloud Console, Okta admin panel).
        Direct the user to this complete URL (e.g., open it in their browser).

        # (Continuing after detecting auth needed)

        if auth_request_event_id and auth_config:
            # Get the base authorization URL from the AuthConfig
            base_auth_uri = auth_config.exchanged_auth_credential.oauth2.auth_uri

            if base_auth_uri:
                redirect_uri = 'http://localhost:8000/callback' # MUST match your OAuth client config
                # Append redirect_uri (use urlencode in production)
                auth_request_uri = base_auth_uri + f'&redirect_uri={redirect_uri}'

                print("\n--- User Action Required ---")
                print(f'1. Please open this URL in your browser:\n   {auth_request_uri}\n')
                print(f'2. Log in and grant the requested permissions.')
                print(f'3. After authorization, you will be redirected to: {redirect_uri}')
                print(f'   Copy the FULL URL from your browser\'s address bar (it includes a `code=...`).')
                # Next step: Get this callback URL from the user (or your web server handler)
            else:
                print("ERROR: Auth URI not found in auth_config.")
                # Handle error
        Authentication

        Step 3. Handle the Redirect Callback (Client):

        Your application must have a mechanism (e.g., a web server route at the redirect_uri) to receive the user after they authorize the application with the provider.
        The provider redirects the user to your redirect_uri and appends an authorization_code (and potentially state, scope) as query parameters to the URL.
        Capture the full callback URL from this incoming request.
        (This step happens outside the main agent execution loop, in your web server or equivalent callback handler.)
        Step 4. Send Authentication Result Back to ADK (Client):

        Once you have the full callback URL (containing the authorization code), retrieve the auth_request_event_id and the AuthConfig object saved in Client Step 1.
        Update the Set the captured callback URL into the exchanged_auth_credential.oauth2.auth_response_uri field. Also ensure exchanged_auth_credential.oauth2.redirect_uri contains the redirect URI you used.
        Construct a Create a types.Content object containing a types.Part with a types.FunctionResponse.
        Set name to "adk_request_credential". (Note: This is a special name for ADK to proceed with authentication. Do not use other names.)
        Set id to the auth_request_event_id you saved.
        Set response to the serialized (e.g., .model_dump()) updated AuthConfig object.
        Call runner.run_async again for the same session, passing this FunctionResponse content as the new_message.

        # (Continuing after user interaction)

            # Simulate getting the callback URL (e.g., from user paste or web handler)
            auth_response_uri = await get_user_input(
                f'Paste the full callback URL here:\n> '
            )
            auth_response_uri = auth_response_uri.strip() # Clean input

            if not auth_response_uri:
                print("Callback URL not provided. Aborting.")
                return

            # Update the received AuthConfig with the callback details
            auth_config.exchanged_auth_credential.oauth2.auth_response_uri = auth_response_uri
            # Also include the redirect_uri used, as the token exchange might need it
            auth_config.exchanged_auth_credential.oauth2.redirect_uri = redirect_uri

            # Construct the FunctionResponse Content object
            auth_content = types.Content(
                role='user', # Role can be 'user' when sending a FunctionResponse
                parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            id=auth_request_event_id,       # Link to the original request
                            name='adk_request_credential', # Special framework function name
                            response=auth_config.model_dump() # Send back the *updated* AuthConfig
                        )
                    )
                ],
            )

            # --- Resume Execution ---
            print("\nSubmitting authentication details back to the agent...")
            events_async_after_auth = runner.run_async(
                session_id=session.id,
                user_id='user',
                new_message=auth_content, # Send the FunctionResponse back
            )

            # --- Process Final Agent Output ---
            print("\n--- Agent Response after Authentication ---")
            async for event in events_async_after_auth:
                # Process events normally, expecting the tool call to succeed now
                print(event) # Print the full event for inspection
        Step 5: ADK Handles Token Exchange & Tool Retry and gets Tool result

        ADK receives the FunctionResponse for adk_request_credential.
        It uses the information in the updated AuthConfig (including the callback URL containing the code) to perform the OAuth token exchange with the provider's token endpoint, obtaining the access token (and possibly refresh token).
        ADK internally makes these tokens available (often via tool_context.get_auth_response() or by updating session state).
        ADK automatically retries the original tool call (the one that initially failed due to missing auth).
        This time, the tool finds the valid tokens and successfully executes the authenticated API call.
        The agent receives the actual result from the tool and generates its final response to the user.
        Journey 2: Building Custom Tools (FunctionTool) Requiring Authentication
        This section focuses on implementing the authentication logic inside your custom Python function when creating a new ADK Tool. We will implement a FunctionTool as an example.

        Prerequisites
        Your function signature must include tool_context: ToolContext. ADK automatically injects this object, providing access to state and auth mechanisms.


        from google.adk.tools import FunctionTool, ToolContext
        from typing import Dict

        def my_authenticated_tool_function(param1: str, ..., tool_context: ToolContext) -> dict:
            # ... your logic ...
            pass

        my_tool = FunctionTool(func=my_authenticated_tool_function)
        Authentication Logic within the Tool Function
        Implement the following steps inside your function:

        Step 1: Check for Cached & Valid Credentials:

        Inside your tool function, first check if valid credentials (e.g., access/refresh tokens) are already stored from a previous run in this session. Credentials for the current sessions should be stored in tool_context.invocation_context.session.state (a dictionary of state) Check existence of existing credentials by checking tool_context.invocation_context.session.state.get(credential_name, None).


        # Inside your tool function
        TOKEN_CACHE_KEY = "my_tool_tokens" # Choose a unique key
        SCOPES = ["scope1", "scope2"] # Define required scopes

        creds = None
        cached_token_info = tool_context.state.get(TOKEN_CACHE_KEY)
        if cached_token_info:
            try:
                creds = Credentials.from_authorized_user_info(cached_token_info, SCOPES)
                if not creds.valid and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    tool_context.state[TOKEN_CACHE_KEY] = json.loads(creds.to_json()) # Update cache
                elif not creds.valid:
                    creds = None # Invalid, needs re-auth
                    tool_context.state.pop(TOKEN_CACHE_KEY, None)
            except Exception as e:
                print(f"Error loading/refreshing cached creds: {e}")
                creds = None
                tool_context.state.pop(TOKEN_CACHE_KEY, None)

        if creds and creds.valid:
            # Skip to Step 5: Make Authenticated API Call
            pass
        else:
            # Proceed to Step 2...
            pass
        Step 2: Check for Auth Response from Client

        If Step 1 didn't yield valid credentials, check if the client just completed the interactive flow by calling auth_response_config = tool_context.get_auth_response().
        This returns the updated AuthConfig object sent back by the client (containing the callback URL in auth_response_uri).

        # Use auth_scheme and auth_credential configured in the tool.
        # exchanged_credential: AuthCredential|None

        exchanged_credential = tool_context.get_auth_response(AuthConfig(
        auth_scheme=auth_scheme,
        raw_auth_credential=auth_credential,
        ))
        # If exchanged_credential is not None, then there is already an exchanged credetial from the auth response. Use it instea, and skip to step 5
        Step 3: Initiate Authentication Request

        If no valid credentials (Step 1.) and no auth response (Step 2.) are found, the tool needs to start the OAuth flow. Define the AuthScheme and initial AuthCredential and call tool_context.request_credential(). Return a status indicating authorization is needed.


        # Use auth_scheme and auth_credential configured in the tool.

        tool_context.request_credential(AuthConfig(
            auth_scheme=auth_scheme,
            raw_auth_credential=auth_credential,
        ))
        return {'pending': true, 'message': 'Awaiting user authentication.'}

        # By setting request_credential, ADK detects a pending authentication event. It pauses execution and ask end user to login.
        Step 4: Exchange Authorization Code for Tokens

        ADK automatically generates oauth authorization URL and presents it to your Agent Client application. Once a user completes the login flow following the authorization URL, ADK extracts the authentication callback url from Agent Client applications, automatically parses the auth code, and generates auth token. At the next Tool call, tool_context.get_auth_response in step 2 will contain a valid credential to use in subsequent API calls.

        Step 5: Cache Obtained Credentials

        After successfully obtaining the token from ADK (Step 2) or if the token is still valid (Step 1), immediately store the new Credentials object in tool_context.state (serialized, e.g., as JSON) using your cache key.


        # Inside your tool function, after obtaining 'creds' (either refreshed or newly exchanged)
        # Cache the new/refreshed tokens
        tool_context.state[TOKEN_CACHE_KEY] = json.loads(creds.to_json())
        print(f"DEBUG: Cached/updated tokens under key: {TOKEN_CACHE_KEY}")
        # Proceed to Step 6 (Make API Call)
        Step 6: Make Authenticated API Call

        Once you have a valid Credentials object (creds from Step 1 or Step 4), use it to make the actual call to the protected API using the appropriate client library (e.g., googleapiclient, requests). Pass the credentials=creds argument.
        Include error handling, especially for HttpError 401/403, which might mean the token expired or was revoked between calls. If you get such an error, consider clearing the cached token (tool_context.state.pop(...)) and potentially returning the auth_required status again to force re-authentication.

        # Inside your tool function, using the valid 'creds' object
        # Ensure creds is valid before proceeding
        if not creds or not creds.valid:
        return {"status": "error", "error_message": "Cannot proceed without valid credentials."}

        try:
        service = build("calendar", "v3", credentials=creds) # Example
        api_result = service.events().list(...).execute()
        # Proceed to Step 7
        except Exception as e:
        # Handle API errors (e.g., check for 401/403, maybe clear cache and re-request auth)
        print(f"ERROR: API call failed: {e}")
        return {"status": "error", "error_message": f"API call failed: {e}"}
        Step 7: Return Tool Result

        After a successful API call, process the result into a dictionary format that is useful for the LLM.
        Crucially, include a along with the data.

        # Inside your tool function, after successful API call
            processed_result = [...] # Process api_result for the LLM
            return {"status": "success", "data": processed_result}

## Authentication

Proper authentication is crucial when your agent tools need to access secure resources or APIs.

### API Key Authentication

The simplest form of authentication is using API keys:

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

### OAuth Authentication

For more complex authentication flows like OAuth:

```python
from google.adk.agents import Agent
from google.adk.tools.oauth import OAuthTool

# Set up OAuth authentication
oauth_tool = OAuthTool(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorization_endpoint="https://auth.example.com/authorize",
    token_endpoint="https://auth.example.com/token",
    scopes=["read", "write"]
)

# Create an agent with the OAuth tool
oauth_agent = Agent(
    name="oauth_agent",
    model="gemini-2.0-flash",
    instruction="Securely access and modify user data through the authenticated API.",
    tools=[oauth_tool]
)
```

### Google Cloud Authentication

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

### Security Best Practices

When implementing authentication in your agent tools:

1. **Never hardcode credentials** in your source code.
2. **Use environment variables** or secure credential stores.
3. **Implement the principle of least privilege** by requesting only the permissions your agent needs.
4. **Rotate credentials** regularly, especially for production deployments.
5. **Audit tool access** to monitor and detect potential security issues.

## Referencing Tool in Agent's Instructions

Within an agent's instructions, you can directly reference a tool by using its **function name**. If the tool's **function name** and **docstring** are sufficiently descriptive, your instructions can primarily focus on **when the Large Language Model (LLM) should utilize the tool**. This promotes clarity and helps the model understand the intended use of each tool.

It is **crucial to clearly instruct the agent on how to handle different return values** that a tool might produce. For example, if a tool returns an error message, your instructions should specify whether the agent should retry the operation, give up on the task, or request additional information from the user.

# Deploy

## Deploying Your Agent

Once you've built and tested your agent using ADK, the next step is to deploy it so it can be accessed, queried, and used in production or integrated with other applications. Deployment moves your agent from your local development machine to a scalable and reliable environment.

## Deployment Options

Your ADK agent can be deployed to a range of different environments based on your needs for production readiness or custom flexibility:

### Agent Engine in Vertex AI

[Agent Engine](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-engine/agent-engine-introduction) is a fully managed auto-scaling service on Google Cloud specifically designed for deploying, managing, and scaling AI agents built with frameworks such as ADK.

Learn more about [deploying your agent to Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-engine/deploy-adk-agent).

        Deploy to Vertex AI Agent Engine
        Agent Engine is a fully managed Google Cloud service enabling developers to deploy, manage, and scale AI agents in production. Agent Engine handles the infrastructure to scale agents in production so you can focus on creating intelligent and impactful applications.


        from vertexai import agent_engines

        remote_app = agent_engines.create(
            agent_engine=root_agent,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]",
            ]
        )
        Install Vertex AI SDK
        Agent Engine is part of the Vertex AI SDK for Python. For more information, you can review the Agent Engine quickstart documentation.

        Install the Vertex AI SDK

        pip install google-cloud-aiplatform[adk,agent_engines]
        Info

        Agent Engine only supported Python version >=3.9 and <=3.12.

        Initialization

        import vertexai

        PROJECT_ID = "your-project-id"
        LOCATION = "us-central1"
        STAGING_BUCKET = "gs://your-google-cloud-storage-bucket"

        vertexai.init(
            project=PROJECT_ID,
            location=LOCATION,
            staging_bucket=STAGING_BUCKET,
        )
        For LOCATION, you can check out the list of supported regions in Agent Engine.

        Create your agent
        You can use the sample agent below, which has two tools (to get weather or retrieve the time in a specified city):


        import datetime
        from zoneinfo import ZoneInfo
        from google.adk.agents import Agent

        def get_weather(city: str) -> dict:
            """Retrieves the current weather report for a specified city.

            Args:
                city (str): The name of the city for which to retrieve the weather report.

            Returns:
                dict: status and result or error msg.
            """
            if city.lower() == "new york":
                return {
                    "status": "success",
                    "report": (
                        "The weather in New York is sunny with a temperature of 25 degrees"
                        " Celsius (41 degrees Fahrenheit)."
                    ),
                }
            else:
                return {
                    "status": "error",
                    "error_message": f"Weather information for '{city}' is not available.",
                }


        def get_current_time(city: str) -> dict:
            """Returns the current time in a specified city.

            Args:
                city (str): The name of the city for which to retrieve the current time.

            Returns:
                dict: status and result or error msg.
            """

            if city.lower() == "new york":
                tz_identifier = "America/New_York"
            else:
                return {
                    "status": "error",
                    "error_message": (
                        f"Sorry, I don't have timezone information for {city}."
                    ),
                }

            tz = ZoneInfo(tz_identifier)
            now = datetime.datetime.now(tz)
            report = (
                f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
            )
            return {"status": "success", "report": report}


        root_agent = Agent(
            name="weather_time_agent",
            model="gemini-2.0-flash",
            description=(
                "Agent to answer questions about the time and weather in a city."
            ),
            instruction=(
                "You are a helpful agent who can answer user questions about the time and weather in a city."
            ),
            tools=[get_weather, get_current_time],
        )
        Prepare your agent for Agent Engine
        Use reasoning_engines.AdkApp() to wrap your agent to make it deployable to Agent Engine


        from vertexai.preview import reasoning_engines

        app = reasoning_engines.AdkApp(
            agent=root_agent,
            enable_tracing=True,
        )
        Try your agent locally
        You can try it locally before deploying to Agent Engine.

        Create session (local)

        session = app.create_session(user_id="u_123")
        session
        Expected output for create_session (local):


        Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
        List sessions (local)

        app.list_sessions(user_id="u_123")
        Expected output for list_sessions (local):


        ListSessionsResponse(session_ids=['c6a33dae-26ef-410c-9135-b434a528291f'])
        Get a specific session (local)

        session = app.get_session(user_id="u_123", session_id=session.id)
        session
        Expected output for get_session (local):


        Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743681991.95696)
        Send queries to your agent (local)

        for event in app.stream_query(
            user_id="u_123",
            session_id=session.id,
            message="whats the weather in new york",
        ):
        print(event)
        Expected output for stream_query (local):


        {'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
        {'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
        {'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
        Deploy your agent to Agent Engine

        from vertexai import agent_engines

        remote_app = agent_engines.create(
            agent_engine=root_agent,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]"   
            ]
        )
        This step may take several minutes to finish.

        Grant the deployed agent permissions
        Before proceeding to query your agent on Agent Engine, your deployed agent must first be granted additional permissions before it can use managed sessions. Managed sessions are a built-in component of Agent Engine that enables agents to keep track of the state of a conversation. Without granting the deploy agent the permissions below, you may see errors when querying your deployed agent.

        You can follow the instructions in Set up your service agent permissions to grant the following permissions via the IAM admin page:

        Vertex AI User (roles/aiplatform.user) to your service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com service account
        Try your agent on Agent Engine
        Create session (remote)

        remote_session = remote_app.create_session(user_id="u_456")
        remote_session
        Expected output for create_session (remote):


        {'events': [],
        'user_id': 'u_456',
        'state': {},
        'id': '7543472750996750336',
        'app_name': '7917477678498709504',
        'last_update_time': 1743683353.030133}
        id is the session ID, and app_name is the resource ID of the deployed agent on Agent Engine.

        List sessions (remote)

        remote_app.list_sessions(user_id="u_456")
        Get a specific session (remote)

        remote_app.get_session(user_id="u_456", session_id=remote_session["id"])
        Note

        While using your agent locally, session ID is stored in session.id, when using your agent remotely on Agent Engine, session ID is stored in remote_session["id"].

        Send queries to your agent (remote)

        for event in remote_app.stream_query(
            user_id="u_456",
            session_id=remote_session["id"],
            message="whats the weather in new york",
        ):
            print(event)
        Expected output for stream_query (remote):


        {'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
        {'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
        {'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
        Clean up
        After you've finished, it's a good practice to clean up your cloud resources. You can delete the deployed Agent Engine instance to avoid any unexpected charges on your Google Cloud account.


        remote_app.delete(force=True)
        force=True will also delete any child resources that were generated from the deployed agent, such as sessions.
### Cloud Run

[Cloud Run](https://cloud.google.com/run) is a managed auto-scaling compute platform on Google Cloud that enables you to run your agent as a container-based application.

Learn more about [deploying your agent to Cloud Run](https://cloud.google.com/run/docs/quickstarts/deploy-container).
        Cloud Run is a fully managed platform that enables you to run your code directly on top of Google's scalable infrastructure.

        To deploy your agent, you can use either the adk deploy cloud_run command (recommended), or with gcloud run deploy command through Cloud Run.

        Agent sample
        For each of the commands, we will reference a capital_agent sample defined on the LLM agent page. We will assume it's in a capital_agent directory.

        To proceed, confirm that your agent code is configured as follows:

        Agent code is in a file called agent.py within your agent directory.
        Your agent variable is named root_agent.
        __init__.py is within your agent directory and contains from . import agent.
        Environment variables
        Set your environment variables as described in the Setup and Installation guide.


        export GOOGLE_CLOUD_PROJECT=your-project-id
        export GOOGLE_CLOUD_LOCATION=us-central1 # Or your preferred location
        export GOOGLE_GENAI_USE_VERTEXAI=True
        (Replace your-project-id with your actual GCP project ID)

        Deployment commands

        adk CLI
        gcloud CLI
        adk CLI
        The adk deploy cloud_run command deploys your agent code to Google Cloud Run.

        Ensure you have authenticated with Google Cloud (gcloud auth login and gcloud config set project <your-project-id>).

        Setup environment variables
        Optional but recommended: Setting environment variables can make the deployment commands cleaner.


        # Set your Google Cloud Project ID
        export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

        # Set your desired Google Cloud Location
        export GOOGLE_CLOUD_LOCATION="us-central1" # Example location

        # Set the path to your agent code directory
        export AGENT_PATH="./capital_agent" # Assuming capital_agent is in the current directory

        # Set a name for your Cloud Run service (optional)
        export SERVICE_NAME="capital-agent-service"

        # Set an application name (optional)
        export APP_NAME="capital-agent-app"
        Command usage
        Minimal command

        adk deploy cloud_run \
        --project=$GOOGLE_CLOUD_PROJECT \
        --region=$GOOGLE_CLOUD_LOCATION \
        $AGENT_PATH
        Full command with optional flags

        adk deploy cloud_run \
        --project=$GOOGLE_CLOUD_PROJECT \
        --region=$GOOGLE_CLOUD_LOCATION \
        --service_name=$SERVICE_NAME \
        --app_name=$APP_NAME \
        --with_ui \
        $AGENT_PATH
        Arguments
        AGENT_PATH: (Required) Positional argument specifying the path to the directory containing your agent's source code (e.g., $AGENT_PATH in the examples, or capital_agent/). This directory must contain at least an __init__.py and your main agent file (e.g., agent.py).
        Options
        --project TEXT: (Required) Your Google Cloud project ID (e.g., $GOOGLE_CLOUD_PROJECT).
        --region TEXT: (Required) The Google Cloud location for deployment (e.g., $GOOGLE_CLOUD_LOCATION, us-central1).
        --service_name TEXT: (Optional) The name for the Cloud Run service (e.g., $SERVICE_NAME). Defaults to adk-default-service-name.
        --app_name TEXT: (Optional) The application name for the ADK API server (e.g., $APP_NAME). Defaults to the name of the directory specified by AGENT_PATH (e.g., capital_agent if AGENT_PATH is ./capital_agent).
        --agent_engine_id TEXT: (Optional) If you are using a managed session service via Vertex AI Agent Engine, provide its resource ID here.
        --port INTEGER: (Optional) The port number the ADK API server will listen on within the container. Defaults to 8000.
        --with_ui: (Optional) If included, deploys the ADK dev UI alongside the agent API server. By default, only the API server is deployed.
        --temp_folder TEXT: (Optional) Specifies a directory for storing intermediate files generated during the deployment process. Defaults to a timestamped folder in the system's temporary directory. (Note: This option is generally not needed unless troubleshooting issues).
        --help: Show the help message and exit.
        Authenticated access
        During the deployment process, you might be prompted: Allow unauthenticated invocations to [your-service-name] (y/N)?.

        Enter y to allow public access to your agent's API endpoint without authentication.
        Enter N (or press Enter for the default) to require authentication (e.g., using an identity token as shown in the "Testing your agent" section).
        Upon successful execution, the command will deploy your agent to Cloud Run and provide the URL of the deployed service.


        Testing your agent
        Once your agent is deployed to Cloud Run, you can interact with it via the deployed UI (if enabled) or directly with its API endpoints using tools like curl. You'll need the service URL provided after deployment.


        UI Testing
        API Testing (curl)
        UI Testing
        If you deployed your agent with the UI enabled:

        adk CLI: You included the --with_ui flag during deployment.
        gcloud CLI: You set SERVE_WEB_INTERFACE = True in your main.py.
        You can test your agent by simply navigating to the Cloud Run service URL provided after deployment in your web browser.


        # Example URL format
        # https://your-service-name-abc123xyz.a.run.app
        The ADK dev UI allows you to interact with your agent, manage sessions, and view execution details directly in the browser.

        To verify your agent is working as intended, you can:

        Select your agent from the dropdown menu.
        Type a message and verify that you receive an expected response from your agent.
        If you experience any unexpected behavior, check the Cloud Run console logs.

### GKE (Google Kubernetes Engine)

For more complex deployments or when you need more control over your infrastructure, you can deploy your ADK agents to Google Kubernetes Engine.

        GKE is Google Clouds managed Kubernetes service. It allows you to deploy and manage containerized applications using Kubernetes.

        To deploy your agent you will need to have a Kubernetes cluster running on GKE. You can create a cluster using the Google Cloud Console or the gcloud command line tool.

        Agent sample
        For each of the commands, we will reference a capital_agent sample defined in on the LLM agent page. We will assume it's in a capital_agent directory.

        To proceed, confirm that your agent code is configured as follows:

        Agent code is in a file called agent.py within your agent directory.
        Your agent variable is named root_agent.
        __init__.py is within your agent directory and contains from . import agent.
        Environment variables
        Set your environment variables as described in the Setup and Installation guide. You also need to install the kubectl command line tool. You can find instructions to do so in the Google Kubernetes Engine Documentation.


        export GOOGLE_CLOUD_PROJECT=your-project-id # Your GCP project ID
        export GOOGLE_CLOUD_LOCATION=us-central1 # Or your preferred location
        export GOOGLE_GENAI_USE_VERTEXAI=true # Set to true if using Vertex AI
        export GOOGLE_CLOUD_PROJECT_NUMBER=$(gcloud projects describe --format json $GOOGLE_CLOUD_PROJECT | jq -r ".projectNumber")
        If you don't have jq installed, you can use the following command to get the project number:


        gcloud projects describe $GOOGLE_CLOUD_PROJECT
        And copy the project number from the output.


        export GOOGLE_CLOUD_PROJECT_NUMBER=YOUR_PROJECT_NUMBER
        Deployment commands
        gcloud CLI
        You can deploy your agent to GKE using the gcloud and kubectl cli and Kubernetes manifest files.

        Ensure you have authenticated with Google Cloud (gcloud auth login and gcloud config set project <your-project-id>).

        Create a GKE cluster
        You can create a GKE cluster using the gcloud command line tool. This example creates an Autopilot cluster named adk-cluster in the us-central1 region.

        If creating a GKE Standard cluster, make sure Workload Identity is enabled. Workload Identity is enabled by default in an AutoPilot cluster.


        gcloud container clusters create-auto adk-cluster \
            --location=$GOOGLE_CLOUD_LOCATION \
            --project=$GOOGLE_CLOUD_PROJECT
        After creating the cluster, you need to connect to it using kubectl. This command configures kubectl to use the credentials for your new cluster.


        gcloud container clusters get-credentials adk-cluster \
            --location=$GOOGLE_CLOUD_LOCATION \
            --project=$GOOGLE_CLOUD_PROJECT
        Artifact Registry
        You need to create a Google Artifact Registry repository to store your container images. You can do this using the gcloud command line tool.


        gcloud artifacts repositories create adk-repo \
            --repository-format=docker \
            --location=$GOOGLE_CLOUD_LOCATION \
            --description="ADK repository"
        Project Structure
        Organize your project files as follows:


        your-project-directory/
        ├── capital_agent/
        │   ├── __init__.py
        │   └── agent.py       # Your agent code (see "Agent sample" tab)
        ├── main.py            # FastAPI application entry point
        ├── requirements.txt   # Python dependencies
        └── Dockerfile         # Container build instructions
        Create the following files (main.py, requirements.txt, Dockerfile) in the root of your-project-directory/.

        Code files
        This file sets up the FastAPI application using get_fast_api_app() from ADK:

        main.py

        import os

        import uvicorn
        from fastapi import FastAPI
        from google.adk.cli.fast_api import get_fast_api_app

        # Get the directory where main.py is located
        AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
        # Example session DB URL (e.g., SQLite)
        SESSION_DB_URL = "sqlite:///./sessions.db"
        # Example allowed origins for CORS
        ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
        # Set web=True if you intend to serve a web interface, False otherwise
        SERVE_WEB_INTERFACE = True

        # Call the function to get the FastAPI app instance
        # Ensure the agent directory name ('capital_agent') matches your agent folder
        app: FastAPI = get_fast_api_app(
            agent_dir=AGENT_DIR,
            session_db_url=SESSION_DB_URL,
            allow_origins=ALLOWED_ORIGINS,
            web=SERVE_WEB_INTERFACE,
        )

        # You can add more FastAPI routes or configurations below if needed
        # Example:
        # @app.get("/hello")
        # async def read_root():
        #     return {"Hello": "World"}

        if __name__ == "__main__":
            # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
            uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        Note: We specify agent_dir to the directory main.py is in and use os.environ.get("PORT", 8080) for Cloud Run compatibility.

        List the necessary Python packages:

        requirements.txt

        google_adk
        # Add any other dependencies your agent needs
        Define the container image:

        Dockerfile

        FROM python:3.13-slim
        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        RUN adduser --disabled-password --gecos "" myuser && \
            chown -R myuser:myuser /app

        COPY . .

        USER myuser

        ENV PATH="/home/myuser/.local/bin:$PATH"

        CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
        Build the container image
        Build the container image using the gcloud command line tool. This example builds the image and tags it as adk-repo/adk-agent:latest.


        gcloud builds submit \
            --tag $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest \
            --project=$GOOGLE_CLOUD_PROJECT \
            .
        Configure Kubernetes Service Account for Vertex AI
        If your agent uses Vertex AI, you need to create a Kubernetes service account with the necessary permissions. This example creates a service account named adk-agent-sa and binds it to the Vertex AI User role.


        kubectl create serviceaccount adk-agent-sa

        gcloud projects add-iam-policy-binding projects/mofilabs \
            --role=roles/aiplatform.user \
            --member=principal://iam.googleapis.com/projects/598464211339/locations/global/workloadIdentityPools/mofilabs.svc.id.goog/subject/ns/default/sa/adk-agent-sa \
            --condition=None
        Create the Kuberentes manifest files
        Create a Kubernetes deployment manifest file named deployment.yaml in your project directory. This file defines how to deploy your application on GKE.

        deployment.yaml

        cat <<  EOF > deployment.yaml
        apiVersion: apps/v1
        kind: Deployment
        metadata:
        name: adk-agent
        spec:
        replicas: 1
        selector:
            matchLabels:
            app: adk-agent
        template:
            metadata:
            labels:
                app: adk-agent
            spec:
            serviceAccount: adk-agent-sa
            containers:
            - name: adk-agent
                image: $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:v0.0.4
                resources:
                limits:
                    memory: "128Mi"
                    cpu: "500m"
                    ephemeral-storage: "128Mi"
                requests:
                    memory: "128Mi"
                    cpu: "500m"
                    ephemeral-storage: "128Mi"
                ports:
                - containerPort: 8080
                env:
                - name: PORT
                    value: "8080"
                - name: GOOGLE_CLOUD_PROJECT
                    value: GOOGLE_CLOUD_PROJECT
                - name: GOOGLE_CLOUD_LOCATION
                    value: GOOGLE_CLOUD_LOCATION
                - name: GOOGLE_GENAI_USE_VERTEXAI
                    value: GOOGLE_GENAI_USE_VERTEXAI
                # Add any other necessary environment variables your agent might need
        ---
        apiVersion: v1
        kind: Service
        metadata:
        name: adk-agent
        spec:       
        type: LoadBalancer
        ports:
            - port: 80
            targetPort: 8080
        selector:
            app: adk-agent
        EOF
        Deploy the Application
        Deploy the application using the kubectl command line tool. This command applies the deployment and service manifest files to your GKE cluster.


        kubectl apply -f deployment.yaml
        After a few moments, you can check the status of your deployment using:


        kubectl get pods -l=app=adk-agent
        This command lists the pods associated with your deployment. You should see a pod with a status of Running.

        Once the pod is running, you can check the status of the service using:


        kubectl get service adk-agent
        If the output shows a External IP, it means your service is accessible from the internet. It may take a few minutes for the external IP to be assigned.

        You can get the external IP address of your service using:


        kubectl get svc adk-agent -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'
        Testing your agent
        Once your agent is deployed to GKE, you can interact with it via the deployed UI (if enabled) or directly with its API endpoints using tools like curl. You'll need the service URL provided after deployment.


        UI Testing
        API Testing (curl)
        UI Testing
        If you deployed your agent with the UI enabled:

        You can test your agent by simply navigating to the kubernetes service URL in your web browser.

        The ADK dev UI allows you to interact with your agent, manage sessions, and view execution details directly in the browser.

        To verify your agent is working as intended, you can:

        Select your agent from the dropdown menu.
        Type a message and verify that you receive an expected response from your agent.
        If you experience any unexpected behavior, check the pod logs for your agent using:


        kubectl logs -l app=adk-agent

# Sessions & Memory

## Introduction to Conversational Context: Session, State, and Memory

### Why Context Matters

Meaningful, multi-turn conversations require agents to understand context. Just like humans, they need to recall what's been said and done to maintain continuity and avoid repetition. The Agent Development Kit (ADK) provides structured ways to manage this context through `Session`, `State`, and `Memory`.

### Core Concepts

Think of interacting with your agent as having distinct conversation threads, potentially drawing upon long-term knowledge.

1. **Session**: The Current Conversation Thread
   * Represents a single, ongoing interaction between a user and your agent system.
   * A `Session` can also hold temporary data (`State`) relevant only during this conversation.
        Session: Tracking Individual Conversations
        Following our Introduction, let's dive into the Session. Think back to the idea of a "conversation thread." Just like you wouldn't start every text message from scratch, agents need context from the ongoing interaction. Session is the ADK object designed specifically to track and manage these individual conversation threads.

        The Session Object
        When a user starts interacting with your agent, the SessionService creates a Session object (google.adk.sessions.Session). This object acts as the container holding everything related to that one specific chat thread. Here are its key properties:

        Identification (id, app_name, user_id): Unique labels for the conversation.
        id: A unique identifier for this specific conversation thread, essential for retrieving it later.
        app_name: Identifies which agent application this conversation belongs to.
        user_id: Links the conversation to a particular user.
        History (events): A chronological sequence of all interactions (Event objects – user messages, agent responses, tool actions) that have occurred within this specific thread.
        Session Data (state): A place to store temporary data relevant only to this specific, ongoing conversation. This acts as a scratchpad for the agent during the interaction. We will cover how to use and manage state in detail in the next section.
        Activity Tracking (last_update_time): A timestamp indicating the last time an event was added to this conversation thread.
        Example: Examining Session Properties

        from google.adk.sessions import InMemorySessionService, Session

        # Create a simple session to examine its properties
        temp_service = InMemorySessionService()
        example_session: Session = temp_service.create_session(
            app_name="my_app",
            user_id="example_user",
            state={"initial_key": "initial_value"} # State can be initialized
        )

        print(f"--- Examining Session Properties ---")
        print(f"ID (`id`):                {example_session.id}")
        print(f"Application Name (`app_name`): {example_session.app_name}")
        print(f"User ID (`user_id`):         {example_session.user_id}")
        print(f"State (`state`):           {example_session.state}") # Note: Only shows initial state here
        print(f"Events (`events`):         {example_session.events}") # Initially empty
        print(f"Last Update (`last_update_time`): {example_session.last_update_time:.2f}")
        print(f"---------------------------------")

        # Clean up (optional for this example)
        temp_service.delete_session(app_name=example_session.app_name,
                                    user_id=example_session.user_id, session_id=example_session.id)
        (Note: The state shown above is only the initial state. State updates happen via events, as discussed in the State section.)

        Managing Sessions with a SessionService
        You don't typically create or manage Session objects directly. Instead, you use a SessionService. This service acts as the central manager responsible for the entire lifecycle of your conversation sessions.

        Its core responsibilities include:

        Starting New Conversations: Creating fresh Session objects when a user begins an interaction.
        Resuming Existing Conversations: Retrieving a specific Session (using its ID) so the agent can continue where it left off.
        Saving Progress: Appending new interactions (Event objects) to a session's history. This is also the mechanism through which session state gets updated (more in the State section).
        Listing Conversations: Finding the active session threads for a particular user and application.
        Cleaning Up: Deleting Session objects and their associated data when conversations are finished or no longer needed.
        SessionService Implementations
        ADK provides different SessionService implementations, allowing you to choose the storage backend that best suits your needs:

        InMemorySessionService

        How it works: Stores all session data directly in the application's memory.
        Persistence: None. All conversation data is lost if the application restarts.
        Requires: Nothing extra.
        Best for: Quick tests, local development, examples, and scenarios where long-term persistence isn't required.

        from google.adk.sessions import InMemorySessionService
        session_service = InMemorySessionService()
        DatabaseSessionService

        How it works: Connects to a relational database (e.g., PostgreSQL, MySQL, SQLite) to store session data persistently in tables.
        Persistence: Yes. Data survives application restarts.
        Requires: A configured database and the sqlalchemy library (pip install google-adk[database]).
        Best for: Applications needing reliable, persistent storage that you manage yourself.

        # Requires: pip install google-adk[database]
        from google.adk.sessions import DatabaseSessionService
        # Example using a local SQLite file:
        db_url = "sqlite:///./my_agent_data.db"
        session_service = DatabaseSessionService(db_url=db_url)
        VertexAiSessionService

        How it works: Uses Google Cloud's Vertex AI infrastructure via API calls for session management.
        Persistence: Yes. Data is managed reliably and scalably by Google Cloud.
        Requires: A Google Cloud project, appropriate permissions, necessary SDKs (pip install google-adk[vertexai]), and the Reasoning Engine resource name/ID.
        Best for: Scalable production applications deployed on Google Cloud, especially when integrating with other Vertex AI features.

        # Requires: pip install google-adk[vertexai]
        # Plus GCP setup and authentication
        from google.adk.sessions import VertexAiSessionService

        PROJECT_ID = "your-gcp-project-id"
        LOCATION = "us-central1"
        # The app_name used with this service should be the Reasoning Engine ID or name
        REASONING_ENGINE_APP_NAME = "projects/your-gcp-project-id/locations/us-central1/reasoningEngines/your-engine-id"

        session_service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION)
        # Use REASONING_ENGINE_APP_NAME when calling service methods, e.g.:
        # session_service.create_session(app_name=REASONING_ENGINE_APP_NAME, ...)
        Choosing the right SessionService is key to defining how your agent's conversation history and temporary data are stored and persist.

        The Session Lifecycle
        Session lifecycle

        Here’s a simplified flow of how Session and SessionService work together during a conversation turn:

        Start or Resume: A user sends a message. Your application's Runner uses the SessionService to either create_session (for a new chat) or get_session (to retrieve an existing one).
        Context Provided: The Runner gets the appropriate Session object from the service, providing the agent with access to its state and events.
        Agent Processing: The agent uses the current user message, its instructions, and potentially the session state and events history to decide on a response.
        Response & State Update: The agent generates a response (and potentially flags data to be updated in the state). The Runner packages this as an Event.
        Save Interaction: The Runner calls session_service.append_event(...) with the Session and the new Event. The service adds the Event to the history and updates the session's state in storage based on information within the event. The session's last_update_time is also updated.
        Ready for Next: The agent's response goes to the user. The updated Session is now stored by the SessionService, ready for the next turn (which restarts the cycle at step 1, usually with get_session).
        End Conversation: When the conversation is over, ideally your application calls session_service.delete_session(...) to clean up the stored session data.
        This cycle highlights how the SessionService ensures conversational continuity by managing the history and state associated with each Session object.

2. **State** (`session.state`): Data Within the Current Conversation
   * Data stored within a specific `Session`.
   * Used to manage information relevant only to the current, active conversation thread (e.g., items in a shopping cart during this chat, user preferences mentioned in this session).

        Within each Session (our conversation thread), the state attribute acts like the agent's dedicated scratchpad for that specific interaction. While session.events holds the full history, session.state is where the agent stores and updates dynamic details needed during the conversation.

        What is session.state?
        Conceptually, session.state is a dictionary holding key-value pairs. It's designed for information the agent needs to recall or track to make the current conversation effective:

        Personalize Interaction: Remember user preferences mentioned earlier (e.g., 'user_preference_theme': 'dark').
        Track Task Progress: Keep tabs on steps in a multi-turn process (e.g., 'booking_step': 'confirm_payment').
        Accumulate Information: Build lists or summaries (e.g., 'shopping_cart_items': ['book', 'pen']).
        Make Informed Decisions: Store flags or values influencing the next response (e.g., 'user_is_authenticated': True).
        Key Characteristics of State
        Structure: Serializable Key-Value Pairs

        Data is stored as key: value.
        Keys: Always strings (str). Use clear names (e.g., 'departure_city', 'user:language_preference').
        Values: Must be serializable. This means they can be easily saved and loaded by the SessionService. Stick to basic Python types like strings, numbers, booleans, and simple lists or dictionaries containing only these basic types. (See API documentation for precise details).
        ⚠️ Avoid Complex Objects: Do not store non-serializable Python objects (custom class instances, functions, connections, etc.) directly in the state. Store simple identifiers if needed, and retrieve the complex object elsewhere.
        Mutability: It Changes

        The contents of the state are expected to change as the conversation evolves.
        Persistence: Depends on SessionService

        Whether state survives application restarts depends on your chosen service:
        InMemorySessionService: Not Persistent. State is lost on restart.
        DatabaseSessionService / VertexAiSessionService: Persistent. State is saved reliably.
        Organizing State with Prefixes: Scope Matters
        Prefixes on state keys define their scope and persistence behavior, especially with persistent services:

        No Prefix (Session State):

        Scope: Specific to the current session (id).
        Persistence: Only persists if the SessionService is persistent (Database, VertexAI).
        Use Cases: Tracking progress within the current task (e.g., 'current_booking_step'), temporary flags for this interaction (e.g., 'needs_clarification').
        Example: session.state['current_intent'] = 'book_flight'
        user: Prefix (User State):

        Scope: Tied to the user_id, shared across all sessions for that user (within the same app_name).
        Persistence: Persistent with Database or VertexAI. (Stored by InMemory but lost on restart).
        Use Cases: User preferences (e.g., 'user:theme'), profile details (e.g., 'user:name').
        Example: session.state['user:preferred_language'] = 'fr'
        app: Prefix (App State):

        Scope: Tied to the app_name, shared across all users and sessions for that application.
        Persistence: Persistent with Database or VertexAI. (Stored by InMemory but lost on restart).
        Use Cases: Global settings (e.g., 'app:api_endpoint'), shared templates.
        Example: session.state['app:global_discount_code'] = 'SAVE10'
        temp: Prefix (Temporary Session State):

        Scope: Specific to the current session processing turn.
        Persistence: Never Persistent. Guaranteed to be discarded, even with persistent services.
        Use Cases: Intermediate results needed only immediately, data you explicitly don't want stored.
        Example: session.state['temp:raw_api_response'] = {...}
        How the Agent Sees It: Your agent code interacts with the combined state through the single session.state dictionary. The SessionService handles fetching/merging state from the correct underlying storage based on prefixes.

        How State is Updated: Recommended Methods
        State should always be updated as part of adding an Event to the session history using session_service.append_event(). This ensures changes are tracked, persistence works correctly, and updates are thread-safe.

        1. The Easy Way: output_key (for Agent Text Responses)

        This is the simplest method for saving an agent's final text response directly into the state. When defining your LlmAgent, specify the output_key:


        from google.adk.agents import LlmAgent
        from google.adk.sessions import InMemorySessionService, Session
        from google.adk.runners import Runner
        from google.genai.types import Content, Part

        # Define agent with output_key
        greeting_agent = LlmAgent(
            name="Greeter",
            model="gemini-2.0-flash", # Use a valid model
            instruction="Generate a short, friendly greeting.",
            output_key="last_greeting" # Save response to state['last_greeting']
        )

        # --- Setup Runner and Session ---
        app_name, user_id, session_id = "state_app", "user1", "session1"
        session_service = InMemorySessionService()
        runner = Runner(
            agent=greeting_agent,
            app_name=app_name,
            session_service=session_service
        )
        session = session_service.create_session(app_name=app_name, 
                                                user_id=user_id, 
                                                session_id=session_id)
        print(f"Initial state: {session.state}")

        # --- Run the Agent ---
        # Runner handles calling append_event, which uses the output_key
        # to automatically create the state_delta.
        user_message = Content(parts=[Part(text="Hello")])
        for event in runner.run(user_id=user_id, 
                                session_id=session_id, 
                                new_message=user_message):
            if event.is_final_response():
            print(f"Agent responded.") # Response text is also in event.content

        # --- Check Updated State ---
        updated_session = session_service.get_session(app_name, user_id, session_id)
        print(f"State after agent run: {updated_session.state}")
        # Expected output might include: {'last_greeting': 'Hello there! How can I help you today?'}
        Behind the scenes, the Runner uses the output_key to create the necessary EventActions with a state_delta and calls append_event.

        2. The Standard Way: EventActions.state_delta (for Complex Updates)

        For more complex scenarios (updating multiple keys, non-string values, specific scopes like user: or app:, or updates not tied directly to the agent's final text), you manually construct the state_delta within EventActions.


        from google.adk.sessions import InMemorySessionService, Session
        from google.adk.events import Event, EventActions
        from google.genai.types import Part, Content
        import time

        # --- Setup ---
        session_service = InMemorySessionService()
        app_name, user_id, session_id = "state_app_manual", "user2", "session2"
        session = session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state={"user:login_count": 0, "task_status": "idle"}
        )
        print(f"Initial state: {session.state}")

        # --- Define State Changes ---
        current_time = time.time()
        state_changes = {
            "task_status": "active",              # Update session state
            "user:login_count": session.state.get("user:login_count", 0) + 1, # Update user state
            "user:last_login_ts": current_time,   # Add user state
            "temp:validation_needed": True        # Add temporary state (will be discarded)
        }

        # --- Create Event with Actions ---
        actions_with_update = EventActions(state_delta=state_changes)
        # This event might represent an internal system action, not just an agent response
        system_event = Event(
            invocation_id="inv_login_update",
            author="system", # Or 'agent', 'tool' etc.
            actions=actions_with_update,
            timestamp=current_time
            # content might be None or represent the action taken
        )

        # --- Append the Event (This updates the state) ---
        session_service.append_event(session, system_event)
        print("`append_event` called with explicit state delta.")

        # --- Check Updated State ---
        updated_session = session_service.get_session(app_name=app_name,
                                                    user_id=user_id, 
                                                    session_id=session_id)
        print(f"State after event: {updated_session.state}")
        # Expected: {'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp>}
        # Note: 'temp:validation_needed' is NOT present.
        What append_event Does:

        Adds the Event to session.events.
        Reads the state_delta from the event's actions.
        Applies these changes to the state managed by the SessionService, correctly handling prefixes and persistence based on the service type.
        Updates the session's last_update_time.
        Ensures thread-safety for concurrent updates.
        ⚠️ A Warning About Direct State Modification
        Avoid directly modifying the session.state dictionary after retrieving a session (e.g., retrieved_session.state['key'] = value).

        Why this is strongly discouraged:

        Bypasses Event History: The change isn't recorded as an Event, losing auditability.
        Breaks Persistence: Changes made this way will likely NOT be saved by DatabaseSessionService or VertexAiSessionService. They rely on append_event to trigger saving.
        Not Thread-Safe: Can lead to race conditions and lost updates.
        Ignores Timestamps/Logic: Doesn't update last_update_time or trigger related event logic.
        Recommendation: Stick to updating state via output_key or EventActions.state_delta within the append_event flow for reliable, trackable, and persistent state management. Use direct access only for reading state.

        Best Practices for State Design Recap
        Minimalism: Store only essential, dynamic data.
        Serialization: Use basic, serializable types.
        Descriptive Keys & Prefixes: Use clear names and appropriate prefixes (user:, app:, temp:, or none).
        Shallow Structures: Avoid deep nesting where possible.
        Standard Update Flow: Rely on append_event.

3. **Memory**: Searchable, Cross-Session Information
   * Represents a store of information that might span multiple past sessions or include external data sources.
   * It acts as a knowledge base the agent can search to recall information or context beyond the immediate conversation.

        Memory: Long-Term Knowledge with MemoryService
        We've seen how Session tracks the history (events) and temporary data (state) for a single, ongoing conversation. But what if an agent needs to recall information from past conversations or access external knowledge bases? This is where the concept of Long-Term Knowledge and the MemoryService come into play.

        Think of it this way:

        Session / State: Like your short-term memory during one specific chat.
        Long-Term Knowledge (MemoryService): Like a searchable archive or knowledge library the agent can consult, potentially containing information from many past chats or other sources.
        The MemoryService Role
        The BaseMemoryService defines the interface for managing this searchable, long-term knowledge store. Its primary responsibilities are:

        Ingesting Information (add_session_to_memory): Taking the contents of a (usually completed) Session and adding relevant information to the long-term knowledge store.
        Searching Information (search_memory): Allowing an agent (typically via a Tool) to query the knowledge store and retrieve relevant snippets or context based on a search query.
        MemoryService Implementations
        ADK provides different ways to implement this long-term knowledge store:

        InMemoryMemoryService

        How it works: Stores session information in the application's memory and performs basic keyword matching for searches.
        Persistence: None. All stored knowledge is lost if the application restarts.
        Requires: Nothing extra.
        Best for: Prototyping, simple testing, scenarios where only basic keyword recall is needed and persistence isn't required.

        from google.adk.memory import InMemoryMemoryService
        memory_service = InMemoryMemoryService()
        VertexAiRagMemoryService

        How it works: Leverages Google Cloud's Vertex AI RAG (Retrieval-Augmented Generation) service. It ingests session data into a specified RAG Corpus and uses powerful semantic search capabilities for retrieval.
        Persistence: Yes. The knowledge is stored persistently within the configured Vertex AI RAG Corpus.
        Requires: A Google Cloud project, appropriate permissions, necessary SDKs (pip install google-adk[vertexai]), and a pre-configured Vertex AI RAG Corpus resource name/ID.
        Best for: Production applications needing scalable, persistent, and semantically relevant knowledge retrieval, especially when deployed on Google Cloud.

        # Requires: pip install google-adk[vertexai]
        # Plus GCP setup, RAG Corpus, and authentication
        from google.adk.memory import VertexAiRagMemoryService

        # The RAG Corpus name or ID
        RAG_CORPUS_RESOURCE_NAME = "projects/your-gcp-project-id/locations/us-central1/ragCorpora/your-corpus-id"
        # Optional configuration for retrieval
        SIMILARITY_TOP_K = 5
        VECTOR_DISTANCE_THRESHOLD = 0.7

        memory_service = VertexAiRagMemoryService(
            rag_corpus=RAG_CORPUS_RESOURCE_NAME,
            similarity_top_k=SIMILARITY_TOP_K,
            vector_distance_threshold=VECTOR_DISTANCE_THRESHOLD
        )
        How Memory Works in Practice
        The typical workflow involves these steps:

        Session Interaction: A user interacts with an agent via a Session, managed by a SessionService. Events are added, and state might be updated.
        Ingestion into Memory: At some point (often when a session is considered complete or has yielded significant information), your application calls memory_service.add_session_to_memory(session). This extracts relevant information from the session's events and adds it to the long-term knowledge store (in-memory dictionary or RAG Corpus).
        Later Query: In a different (or the same) session, the user might ask a question requiring past context (e.g., "What did we discuss about project X last week?").
        Agent Uses Memory Tool: An agent equipped with a memory-retrieval tool (like the built-in load_memory tool) recognizes the need for past context. It calls the tool, providing a search query (e.g., "discussion project X last week").
        Search Execution: The tool internally calls memory_service.search_memory(app_name, user_id, query).
        Results Returned: The MemoryService searches its store (using keyword matching or semantic search) and returns relevant snippets as a SearchMemoryResponse containing a list of MemoryResult objects (each potentially holding events from a relevant past session).
        Agent Uses Results: The tool returns these results to the agent, usually as part of the context or function response. The agent can then use this retrieved information to formulate its final answer to the user.
        Example: Adding and Searching Memory
        This example demonstrates the basic flow using the InMemory services for simplicity.

        Full Code

        import asyncio
        from google.adk.agents import LlmAgent
        from google.adk.sessions import InMemorySessionService, Session
        from google.adk.memory import InMemoryMemoryService # Import MemoryService
        from google.adk.runners import Runner
        from google.adk.tools import load_memory # Tool to query memory
        from google.genai.types import Content, Part

        # --- Constants ---
        APP_NAME = "memory_example_app"
        USER_ID = "mem_user"
        MODEL = "gemini-2.0-flash" # Use a valid model

        # --- Agent Definitions ---
        # Agent 1: Simple agent to capture information
        info_capture_agent = LlmAgent(
            model=MODEL,
            name="InfoCaptureAgent",
            instruction="Acknowledge the user's statement.",
            # output_key="captured_info" # Could optionally save to state too
        )

        # Agent 2: Agent that can use memory
        memory_recall_agent = LlmAgent(
            model=MODEL,
            name="MemoryRecallAgent",
            instruction="Answer the user's question. Use the 'load_memory' tool "
                        "if the answer might be in past conversations.",
            tools=[load_memory] # Give the agent the tool
        )

        # --- Services and Runner ---
        session_service = InMemorySessionService()
        memory_service = InMemoryMemoryService() # Use in-memory for demo

        runner = Runner(
            # Start with the info capture agent
            agent=info_capture_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service # Provide the memory service to the Runner
        )

        # --- Scenario ---

        # Turn 1: Capture some information in a session
        print("--- Turn 1: Capturing Information ---")
        session1_id = "session_info"
        session1 = session_service.create_session(APP_NAME, USER_ID, session1_id)
        user_input1 = Content(parts=[Part(text="My favorite project is Project Alpha.")])

        # Run the agent
        final_response_text = "(No final response)"
        for event in runner.run(USER_ID, session1_id, user_input1):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
        print(f"Agent 1 Response: {final_response_text}")

        # Get the completed session
        completed_session1 = session_service.get_session(APP_NAME, USER_ID, session1_id)

        # Add this session's content to the Memory Service
        print("\n--- Adding Session 1 to Memory ---")
        memory_service.add_session_to_memory(completed_session1)
        print("Session added to memory.")

        # Turn 2: In a *new* (or same) session, ask a question requiring memory
        print("\n--- Turn 2: Recalling Information ---")
        session2_id = "session_recall" # Can be same or different session ID
        session2 = session_service.create_session(APP_NAME, USER_ID, session2_id)

        # Switch runner to the recall agent
        runner.agent = memory_recall_agent
        user_input2 = Content(parts=[Part(text="What is my favorite project?")])

        # Run the recall agent
        print("Running MemoryRecallAgent...")
        final_response_text_2 = "(No final response)"
        for event in runner.run(USER_ID, session2_id, user_input2):
            print(f"  Event: {event.author} - Type: {'Text' if event.content and event.content.parts and event.content.parts[0].text else ''}"
                f"{'FuncCall' if event.get_function_calls() else ''}"
                f"{'FuncResp' if event.get_function_responses() else ''}")
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text_2 = event.content.parts[0].text
                print(f"Agent 2 Final Response: {final_response_text_2}")
                break # Stop after final response

        #Expected Event Sequence for Turn 2:
        #1. User sends "What is my favorite project?"
        #2. Agent (LLM) decides to call `load_memory` tool with a query like "favorite project".
        #3. Runner executes the `load_memory` tool, which calls `memory_service.search_memory`.
        #4. `InMemoryMemoryService` finds the relevant text ("My favorite project is Project Alpha.") from session1.
        #5. Tool returns this text in a FunctionResponse event.
        #6. Agent (LLM) receives the function response, processes the retrieved text.
        #7. Agent generates the final answer (e.g., "Your favorite project is Project 

### Managing Context: Services

ADK provides services to manage these concepts:

1. **SessionService**: Manages Conversation Threads (`Session` objects)
   * Creates, retrieves, and updates conversation sessions
   * Ensures the agent has the right history and state for the current turn.

2. **MemoryService**: Manages the Long-Term Knowledge Store (`Memory`)
   * Handles ingesting information (often from completed `Session`s) into the long-term store.
   * Provides methods to search this stored knowledge based on queries.

**Implementations**: ADK offers different implementations for both `SessionService` and `MemoryService`, allowing you to choose the storage backend that best fits your application's needs. Notably, in-memory implementations are provided for both services; these are designed specifically for local quick testing and development. It's important to remember that all data stored using these in-memory options (sessions, state, or long-term knowledge) is lost when your application restarts. For persistence and scalability beyond local testing, ADK also offers database and cloud-based service options.

### In Summary:

* **Session & State**: Focus on the here and now – the history and temporary data of the single, active conversation. Managed primarily by `SessionService`.

* **Memory**: Focuses on the past and external information – a searchable archive potentially spanning across conversations. Managed by `MemoryService`.

# Artifacts

## Overview

In ADK, **Artifacts** represent a crucial mechanism for managing named, versioned binary data associated either with a specific user interaction session or persistently with a user across multiple sessions. They allow your agents and tools to handle data beyond simple text strings, enabling richer interactions involving files, images, audio, and other binary formats.

## What are Artifacts?
In ADK, Artifacts represent a crucial mechanism for managing named, versioned binary data associated either with a specific user interaction session or persistently with a user across multiple sessions. They allow your agents and tools to handle data beyond simple text strings, enabling richer interactions involving files, images, audio, and other binary formats.

What are Artifacts?
Definition: An Artifact is essentially a piece of binary data (like the content of a file) identified by a unique filename string within a specific scope (session or user). Each time you save an artifact with the same filename, a new version is created.

Representation: Artifacts are consistently represented using the standard google.genai.types.Part object. The core data is typically stored within the inline_data attribute of the Part, which itself contains:

data: The raw binary content as bytes.
mime_type: A string indicating the type of the data (e.g., 'image/png', 'application/pdf'). This is essential for correctly interpreting the data later.

# Example of how an artifact might be represented as a types.Part
import google.genai.types as types

# Assume 'image_bytes' contains the binary data of a PNG image
image_bytes = b'\x89PNG\r\n\x1a\n...' # Placeholder for actual image bytes

image_artifact = types.Part(
    inline_data=types.Blob(
        mime_type="image/png",
        data=image_bytes
    )
)

# You can also use the convenience constructor:
# image_artifact_alt = types.Part.from_data(data=image_bytes, mime_type="image/png")

print(f"Artifact MIME Type: {image_artifact.inline_data.mime_type}")
print(f"Artifact Data (first 10 bytes): {image_artifact.inline_data.data[:10]}...")
Persistence & Management: Artifacts are not stored directly within the agent or session state. Their storage and retrieval are managed by a dedicated Artifact Service (an implementation of BaseArtifactService, defined in google.adk.artifacts.base_artifact_service.py). ADK provides implementations like InMemoryArtifactService (for testing/temporary storage, defined in google.adk.artifacts.in_memory_artifact_service.py) and GcsArtifactService (for persistent storage using Google Cloud Storage, defined in google.adk.artifacts.gcs_artifact_service.py). The chosen service handles versioning automatically when you save data.

Why Use Artifacts?
While session state is suitable for storing small pieces of configuration or conversational context (like strings, numbers, booleans, or small dictionaries/lists), Artifacts are designed for scenarios involving binary or large data:

Handling Non-Textual Data: Easily store and retrieve images, audio clips, video snippets, PDFs, spreadsheets, or any other file format relevant to your agent's function.
Persisting Large Data: Session state is generally not optimized for storing large amounts of data. Artifacts provide a dedicated mechanism for persisting larger blobs without cluttering the session state.
User File Management: Provide capabilities for users to upload files (which can be saved as artifacts) and retrieve or download files generated by the agent (loaded from artifacts).
Sharing Outputs: Enable tools or agents to generate binary outputs (like a PDF report or a generated image) that can be saved via save_artifact and later accessed by other parts of the application or even in subsequent sessions (if using user namespacing).
Caching Binary Data: Store the results of computationally expensive operations that produce binary data (e.g., rendering a complex chart image) as artifacts to avoid regenerating them on subsequent requests.
In essence, whenever your agent needs to work with file-like binary data that needs to be persisted, versioned, or shared, Artifacts managed by an ArtifactService are the appropriate mechanism within ADK.

Common Use Cases
Artifacts provide a flexible way to handle binary data within your ADK applications.

Here are some typical scenarios where they prove valuable:

Generated Reports/Files:

A tool or agent generates a report (e.g., a PDF analysis, a CSV data export, an image chart).
The tool uses tool_context.save_artifact("monthly_report_oct_2024.pdf", report_part) to store the generated file.
The user can later ask the agent to retrieve this report, which might involve another tool using tool_context.load_artifact("monthly_report_oct_2024.pdf") or listing available reports using tool_context.list_artifacts().
Handling User Uploads:

A user uploads a file (e.g., an image for analysis, a document for summarization) through a front-end interface.
The application backend receives the file, creates a types.Part from its bytes and MIME type, and uses the runner.session_service (or similar mechanism outside a direct agent run) or a dedicated tool/callback within a run via context.save_artifact to store it, potentially using the user: namespace if it should persist across sessions (e.g., user:uploaded_image.jpg).
An agent can then be prompted to process this uploaded file, using context.load_artifact("user:uploaded_image.jpg") to retrieve it.
Storing Intermediate Binary Results:

An agent performs a complex multi-step process where one step generates intermediate binary data (e.g., audio synthesis, simulation results).
This data is saved using context.save_artifact with a temporary or descriptive name (e.g., "temp_audio_step1.wav").
A subsequent agent or tool in the flow (perhaps in a SequentialAgent or triggered later) can load this intermediate artifact using context.load_artifact to continue the process.
Persistent User Data:

Storing user-specific configuration or data that isn't a simple key-value state.
An agent saves user preferences or a profile picture using context.save_artifact("user:profile_settings.json", settings_part) or context.save_artifact("user:avatar.png", avatar_part).
These artifacts can be loaded in any future session for that user to personalize their experience.
Caching Generated Binary Content:

An agent frequently generates the same binary output based on certain inputs (e.g., a company logo image, a standard audio greeting).
Before generating, a before_tool_callback or before_agent_callback checks if the artifact exists using context.load_artifact.
If it exists, the cached artifact is used, skipping the generation step.
If not, the content is generated, and context.save_artifact is called in an after_tool_callback or after_agent_callback to cache it for next time.
Core Concepts
Understanding artifacts involves grasping a few key components: the service that manages them, the data structure used to hold them, and how they are identified and versioned.

Artifact Service (BaseArtifactService)
Role: The central component responsible for the actual storage and retrieval logic for artifacts. It defines how and where artifacts are persisted.

Interface: Defined by the abstract base class BaseArtifactService (google.adk.artifacts.base_artifact_service.py). Any concrete implementation must provide methods for:

save_artifact(...) -> int: Stores the artifact data and returns its assigned version number.
load_artifact(...) -> Optional[types.Part]: Retrieves a specific version (or the latest) of an artifact.
list_artifact_keys(...) -> list[str]: Lists the unique filenames of artifacts within a given scope.
delete_artifact(...) -> None: Removes an artifact (and potentially all its versions, depending on implementation).
list_versions(...) -> list[int]: Lists all available version numbers for a specific artifact filename.
Configuration: You provide an instance of an artifact service (e.g., InMemoryArtifactService, GcsArtifactService) when initializing the Runner. The Runner then makes this service available to agents and tools via the InvocationContext.


from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService # Or GcsArtifactService
from google.adk.agents import LlmAgent # Any agent
from google.adk.sessions import InMemorySessionService

# Example: Configuring the Runner with an Artifact Service
my_agent = LlmAgent(name="artifact_user_agent", model="gemini-2.0-flash")
artifact_service = InMemoryArtifactService() # Choose an implementation
session_service = InMemorySessionService()

runner = Runner(
    agent=my_agent,
    app_name="my_artifact_app",
    session_service=session_service,
    artifact_service=artifact_service # Provide the service instance here
)
# Now, contexts within runs managed by this runner can use artifact methods
Artifact Data (google.genai.types.Part)
Standard Representation: Artifact content is universally represented using the google.genai.types.Part object, the same structure used for parts of LLM messages.

Key Attribute (inline_data): For artifacts, the most relevant attribute is inline_data, which is a google.genai.types.Blob object containing:

data (bytes): The raw binary content of the artifact.
mime_type (str): A standard MIME type string (e.g., 'application/pdf', 'image/png', 'audio/mpeg') describing the nature of the binary data. This is crucial for correct interpretation when loading the artifact.
Creation: You typically create a Part for an artifact using its from_data class method or by constructing it directly with a Blob.


import google.genai.types as types

# Example: Creating an artifact Part from raw bytes
pdf_bytes = b'%PDF-1.4...' # Your raw PDF data
pdf_mime_type = "application/pdf"

# Using the constructor
pdf_artifact = types.Part(
    inline_data=types.Blob(data=pdf_bytes, mime_type=pdf_mime_type)
)

# Using the convenience class method (equivalent)
pdf_artifact_alt = types.Part.from_data(data=pdf_bytes, mime_type=pdf_mime_type)

print(f"Created artifact with MIME type: {pdf_artifact.inline_data.mime_type}")
Filename (str)
Identifier: A simple string used to name and retrieve an artifact within its specific namespace (see below).
Uniqueness: Filenames must be unique within their scope (either the session or the user namespace).
Best Practice: Use descriptive names, potentially including file extensions (e.g., "monthly_report.pdf", "user_avatar.jpg"), although the extension itself doesn't dictate behavior – the mime_type does.
Versioning (int)
Automatic Versioning: The artifact service automatically handles versioning. When you call save_artifact, the service determines the next available version number (typically starting from 0 and incrementing) for that specific filename and scope.
Returned by save_artifact: The save_artifact method returns the integer version number that was assigned to the newly saved artifact.
Retrieval:
load_artifact(..., version=None) (default): Retrieves the latest available version of the artifact.
load_artifact(..., version=N): Retrieves the specific version N.
Listing Versions: The list_versions method (on the service, not context) can be used to find all existing version numbers for an artifact.
Namespacing (Session vs. User)
Concept: Artifacts can be scoped either to a specific session or more broadly to a user across all their sessions within the application. This scoping is determined by the filename format and handled internally by the ArtifactService.

Default (Session Scope): If you use a plain filename like "report.pdf", the artifact is associated with the specific app_name, user_id, and session_id. It's only accessible within that exact session context.

Internal Path (Example): app_name/user_id/session_id/report.pdf/<version> (as seen in GcsArtifactService._get_blob_name and InMemoryArtifactService._artifact_path)

User Scope ("user:" prefix): If you prefix the filename with "user:", like "user:profile.png", the artifact is associated only with the app_name and user_id. It can be accessed or updated from any session belonging to that user within the app.

Internal Path (Example): app_name/user_id/user/user:profile.png/<version> (The user: prefix is often kept in the final path segment for clarity, as seen in the service implementations).

Use Case: Ideal for data that belongs to the user themselves, independent of a specific conversation, such as profile pictures, user preferences files, or long-term reports.

# Example illustrating namespace difference (conceptual)

# Session-specific artifact filename
session_report_filename = "summary.txt"

# User-specific artifact filename
user_config_filename = "user:settings.json"

# When saving 'summary.txt', it's tied to the current session ID.
# When saving 'user:settings.json', it's tied only to the user ID.
These core concepts work together to provide a flexible system for managing binary data within the ADK framework.

Interacting with Artifacts (via Context Objects)
The primary way you interact with artifacts within your agent's logic (specifically within callbacks or tools) is through methods provided by the CallbackContext and ToolContext objects. These methods abstract away the underlying storage details managed by the ArtifactService.

Prerequisite: Configuring the ArtifactService
Before you can use any artifact methods via the context objects, you must provide an instance of a BaseArtifactService implementation (like InMemoryArtifactService or GcsArtifactService) when initializing your Runner.


from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService # Or GcsArtifactService
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService

# Your agent definition
agent = LlmAgent(name="my_agent", model="gemini-2.0-flash")

# Instantiate the desired artifact service
artifact_service = InMemoryArtifactService()

# Provide it to the Runner
runner = Runner(
    agent=agent,
    app_name="artifact_app",
    session_service=InMemorySessionService(),
    artifact_service=artifact_service # Service must be provided here
)
If no artifact_service is configured in the InvocationContext (which happens if it's not passed to the Runner), calling save_artifact, load_artifact, or list_artifacts on the context objects will raise a ValueError.

Accessing Methods
The artifact interaction methods are available directly on instances of CallbackContext (passed to agent and model callbacks) and ToolContext (passed to tool callbacks). Remember that ToolContext inherits from CallbackContext.

Saving Artifacts
Method:

context.save_artifact(filename: str, artifact: types.Part) -> int
Available Contexts: CallbackContext, ToolContext.

Action:

Takes a filename string (which may include the "user:" prefix for user-scoping) and a types.Part object containing the artifact data (usually in artifact.inline_data).
Passes this information to the underlying artifact_service.save_artifact.
The service stores the data, assigns the next available version number for that filename and scope.
Crucially, the context automatically records this action by adding an entry to the current event's actions.artifact_delta dictionary (defined in google.adk.events.event_actions.py). This delta maps the filename to the newly assigned version.
Returns: The integer version number assigned to the saved artifact.

Code Example (within a hypothetical tool or callback):


import google.genai.types as types
from google.adk.agents.callback_context import CallbackContext # Or ToolContext

async def save_generated_report(context: CallbackContext, report_bytes: bytes):
    """Saves generated PDF report bytes as an artifact."""
    report_artifact = types.Part.from_data(
        data=report_bytes,
        mime_type="application/pdf"
    )
    filename = "generated_report.pdf"

    try:
        version = context.save_artifact(filename=filename, artifact=report_artifact)
        print(f"Successfully saved artifact '{filename}' as version {version}.")
        # The event generated after this callback will contain:
        # event.actions.artifact_delta == {"generated_report.pdf": version}
    except ValueError as e:
        print(f"Error saving artifact: {e}. Is ArtifactService configured?")
    except Exception as e:
        # Handle potential storage errors (e.g., GCS permissions)
        print(f"An unexpected error occurred during artifact save: {e}")

# --- Example Usage Concept ---
# report_data = b'...' # Assume this holds the PDF bytes
# await save_generated_report(callback_context, report_data)
Loading Artifacts
Method:

context.load_artifact(filename: str, version: Optional[int] = None) -> Optional[types.Part]
Available Contexts: CallbackContext, ToolContext.

Action:

Takes a filename string (potentially including "user:").
Optionally takes an integer version. If version is None (the default), it requests the latest version from the service. If a specific integer is provided, it requests that exact version.
Calls the underlying artifact_service.load_artifact.
The service attempts to retrieve the specified artifact.
Returns: A types.Part object containing the artifact data if found, or None if the artifact (or the specified version) does not exist.

Code Example (within a hypothetical tool or callback):


import google.genai.types as types
from google.adk.agents.callback_context import CallbackContext # Or ToolContext

async def process_latest_report(context: CallbackContext):
    """Loads the latest report artifact and processes its data."""
    filename = "generated_report.pdf"
    try:
        # Load the latest version
        report_artifact = context.load_artifact(filename=filename)

        if report_artifact and report_artifact.inline_data:
            print(f"Successfully loaded latest artifact '{filename}'.")
            print(f"MIME Type: {report_artifact.inline_data.mime_type}")
            # Process the report_artifact.inline_data.data (bytes)
            pdf_bytes = report_artifact.inline_data.data
            print(f"Report size: {len(pdf_bytes)} bytes.")
            # ... further processing ...
        else:
            print(f"Artifact '{filename}' not found.")

        # Example: Load a specific version (if version 0 exists)
        # specific_version_artifact = context.load_artifact(filename=filename, version=0)
        # if specific_version_artifact:
        #     print(f"Loaded version 0 of '{filename}'.")

    except ValueError as e:
        print(f"Error loading artifact: {e}. Is ArtifactService configured?")
    except Exception as e:
        # Handle potential storage errors
        print(f"An unexpected error occurred during artifact load: {e}")

# --- Example Usage Concept ---
# await process_latest_report(callback_context)
Listing Artifact Filenames (Tool Context Only)
Method:

tool_context.list_artifacts() -> list[str]
Available Context: ToolContext only. This method is not available on the base CallbackContext.

Action: Calls the underlying artifact_service.list_artifact_keys to get a list of all unique artifact filenames accessible within the current scope (including both session-specific files and user-scoped files prefixed with "user:").

Returns: A sorted list of str filenames.

Code Example (within a tool function):


from google.adk.tools.tool_context import ToolContext

def list_user_files(tool_context: ToolContext) -> str:
    """Tool to list available artifacts for the user."""
    try:
        available_files = tool_context.list_artifacts()
        if not available_files:
            return "You have no saved artifacts."
        else:
            # Format the list for the user/LLM
            file_list_str = "\n".join([f"- {fname}" for fname in available_files])
            return f"Here are your available artifacts:\n{file_list_str}"
    except ValueError as e:
        print(f"Error listing artifacts: {e}. Is ArtifactService configured?")
        return "Error: Could not list artifacts."
    except Exception as e:
        print(f"An unexpected error occurred during artifact list: {e}")
        return "Error: An unexpected error occurred while listing artifacts."

# This function would typically be wrapped in a FunctionTool
# from google.adk.tools import FunctionTool
# list_files_tool = FunctionTool(func=list_user_files)
These context methods provide a convenient and consistent way to manage binary data persistence within ADK, regardless of the chosen backend storage implementation (InMemoryArtifactService, GcsArtifactService, etc.).

Available Implementations
ADK provides concrete implementations of the BaseArtifactService interface, offering different storage backends suitable for various development stages and deployment needs. These implementations handle the details of storing, versioning, and retrieving artifact data based on the app_name, user_id, session_id, and filename (including the user: namespace prefix).

InMemoryArtifactService
Source File: google.adk.artifacts.in_memory_artifact_service.py
Storage Mechanism: Uses a Python dictionary (self.artifacts) held in the application's memory to store artifacts. The dictionary keys represent the artifact path (incorporating app, user, session/user-scope, and filename), and the values are lists of types.Part, where each element in the list corresponds to a version (index 0 is version 0, index 1 is version 1, etc.).
Key Features:
Simplicity: Requires no external setup or dependencies beyond the core ADK library.
Speed: Operations are typically very fast as they involve in-memory dictionary lookups and list manipulations.
Ephemeral: All stored artifacts are lost when the Python process running the application terminates. Data does not persist between application restarts.
Use Cases:
Ideal for local development and testing where persistence is not required.
Suitable for short-lived demonstrations or scenarios where artifact data is purely temporary within a single run of the application.
Instantiation:

from google.adk.artifacts import InMemoryArtifactService

# Simply instantiate the class
in_memory_service = InMemoryArtifactService()

# Then pass it to the Runner
# runner = Runner(..., artifact_service=in_memory_service)
GcsArtifactService
Source File: google.adk.artifacts.gcs_artifact_service.py
Storage Mechanism: Leverages Google Cloud Storage (GCS) for persistent artifact storage. Each version of an artifact is stored as a separate object within a specified GCS bucket.
Object Naming Convention: It constructs GCS object names (blob names) using a hierarchical path structure, typically:
Session-scoped: {app_name}/{user_id}/{session_id}/{filename}/{version}
User-scoped: {app_name}/{user_id}/user/{filename}/{version} (Note: The service handles the user: prefix in the filename to determine the path structure).
Key Features:
Persistence: Artifacts stored in GCS persist across application restarts and deployments.
Scalability: Leverages the scalability and durability of Google Cloud Storage.
Versioning: Explicitly stores each version as a distinct GCS object.
Configuration Required: Needs configuration with a target GCS bucket_name.
Permissions Required: The application environment needs appropriate credentials and IAM permissions to read from and write to the specified GCS bucket.
Use Cases:
Production environments requiring persistent artifact storage.
Scenarios where artifacts need to be shared across different application instances or services (by accessing the same GCS bucket).
Applications needing long-term storage and retrieval of user or session data.
Instantiation:

from google.adk.artifacts import GcsArtifactService

# Specify the GCS bucket name
gcs_bucket_name = "your-gcs-bucket-for-adk-artifacts" # Replace with your bucket name

try:
    gcs_service = GcsArtifactService(bucket_name=gcs_bucket_name)
    print(f"GcsArtifactService initialized for bucket: {gcs_bucket_name}")
    # Ensure your environment has credentials to access this bucket.
    # e.g., via Application Default Credentials (ADC)

    # Then pass it to the Runner
    # runner = Runner(..., artifact_service=gcs_service)

except Exception as e:
    # Catch potential errors during GCS client initialization (e.g., auth issues)
    print(f"Error initializing GcsArtifactService: {e}")
    # Handle the error appropriately - maybe fall back to InMemory or raise
Choosing the appropriate ArtifactService implementation depends on your application's requirements for data persistence, scalability, and operational environment.

Best Practices
To use artifacts effectively and maintainably:

Choose the Right Service: Use InMemoryArtifactService for rapid prototyping, testing, and scenarios where persistence isn't needed. Use GcsArtifactService (or implement your own BaseArtifactService for other backends) for production environments requiring data persistence and scalability.
Meaningful Filenames: Use clear, descriptive filenames. Including relevant extensions (.pdf, .png, .wav) helps humans understand the content, even though the mime_type dictates programmatic handling. Establish conventions for temporary vs. persistent artifact names.
Specify Correct MIME Types: Always provide an accurate mime_type when creating the types.Part for save_artifact. This is critical for applications or tools that later load_artifact to interpret the bytes data correctly. Use standard IANA MIME types where possible.
Understand Versioning: Remember that load_artifact() without a specific version argument retrieves the latest version. If your logic depends on a specific historical version of an artifact, be sure to provide the integer version number when loading.
Use Namespacing (user:) Deliberately: Only use the "user:" prefix for filenames when the data truly belongs to the user and should be accessible across all their sessions. For data specific to a single conversation or session, use regular filenames without the prefix.
Error Handling:
Always check if an artifact_service is actually configured before calling context methods (save_artifact, load_artifact, list_artifacts) – they will raise a ValueError if the service is None. Wrap calls in try...except ValueError.
Check the return value of load_artifact, as it will be None if the artifact or version doesn't exist. Don't assume it always returns a Part.
Be prepared to handle exceptions from the underlying storage service, especially with GcsArtifactService (e.g., google.api_core.exceptions.Forbidden for permission issues, NotFound if the bucket doesn't exist, network errors).
Size Considerations: Artifacts are suitable for typical file sizes, but be mindful of potential costs and performance impacts with extremely large files, especially with cloud storage. InMemoryArtifactService can consume significant memory if storing many large artifacts. Evaluate if very large data might be better handled through direct GCS links or other specialized storage solutions rather than passing entire byte arrays in-memory.
Cleanup Strategy: For persistent storage like GcsArtifactService, artifacts remain until explicitly deleted. If artifacts represent temporary data or have a limited lifespan, implement a strategy for cleanup. This might involve:
Using GCS lifecycle policies on the bucket.
Building specific tools or administrative functions that utilize the artifact_service.delete_artifact method (note: delete is not exposed via context objects for safety).
Carefully managing filenames to allow pattern-based deletion if needed.

# Callbacks

## Callbacks: Observe, Customize, and Control Agent Behavior

### Introduction: What are Callbacks and Why Use Them?

Callbacks are a cornerstone feature of ADK, providing a powerful mechanism to hook into an agent's execution process. They allow you to observe, customize, and even control the agent's behavior at specific, predefined points without modifying the core ADK framework code.

#### What are they?

In essence, callbacks are standard Python functions that you define. You then associate these functions with an agent when you create it. The ADK framework automatically calls your functions at key stages in the agent's lifecycle, such as:

* Before or after the agent's main processing logic runs.
* Before sending a request to, or after receiving a response from, the Large Language Model (LLM).
* Before executing a tool (like a Python function or another agent) or after it finishes.

#### Why use them?

Callbacks unlock significant flexibility and enable advanced agent capabilities:

* **Observe & Debug**: Log detailed information at critical steps for monitoring and troubleshooting.
* **Customize & Control**: Modify data flowing through the agent (like LLM requests or tool results) or even bypass certain steps entirely based on your logic.
* **Implement Guardrails**: Enforce safety rules, validate inputs/outputs, or prevent disallowed operations.
* **Manage State**: Read or dynamically update the agent's session state during execution.

#### How are they added?

You register callbacks by passing your defined Python functions as arguments to the agent's constructor (`__init__`) when you create an instance of `Agent` or `LlmAgent`.

```python
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional

# --- Define your callback function ---
def my_before_model_logic(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    print(f"Callback running before model call for agent: {callback_context.agent_name}")
    # ... your custom logic here ...
    return None # Allow the model call to proceed

# --- Register it during Agent creation ---
my_agent = LlmAgent(
    name="MyCallbackAgent",
    model="gemini-2.0-flash",
    instruction="Be helpful.",
    # Other agent parameters...
    before_model_callback=my_before_model_logic # Pass the function here
)
```
Types of Callbacks
The framework provides different types of callbacks that trigger at various stages of an agent's execution. Understanding when each callback fires and what context it receives is key to using them effectively.

Agent Lifecycle Callbacks
These callbacks are available on any agent that inherits from BaseAgent (including LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, etc).

Before Agent Callback
When: Called immediately before the agent's _run_async_impl (or _run_live_impl) method is executed. It runs after the agent's InvocationContext is created but before its core logic begins.

Purpose: Ideal for setting up resources or state needed only for this specific agent's run, performing validation checks on the session state (callback_context.state) before execution starts, logging the entry point of the agent's activity, or potentially modifying the invocation context before the core logic uses it.

Code
After Agent Callback
When: Called immediately after the agent's _run_async_impl (or _run_live_impl) method successfully completes. It does not run if the agent was skipped due to before_agent_callback returning content or if end_invocation was set during the agent's run.

Purpose: Useful for cleanup tasks, post-execution validation, logging the completion of an agent's activity, modifying final state, or augmenting/replacing the agent's final output.

Code
LLM Interaction Callbacks
These callbacks are specific to LlmAgent and provide hooks around the interaction with the Large Language Model.

Before Model Callback
When: Called just before the generate_content_async (or equivalent) request is sent to the LLM within an LlmAgent's flow.

Purpose: Allows inspection and modification of the request going to the LLM. Use cases include adding dynamic instructions, injecting few-shot examples based on state, modifying model config, implementing guardrails (like profanity filters), or implementing request-level caching.

Return Value Effect:
If the callback returns None, the LLM continues its normal workflow. If the callback returns an LlmResponse object, then the call to the LLM is skipped. The returned LlmResponse is used directly as if it came from the model. This is powerful for implementing guardrails or caching.

Code
After Model Callback
When: Called just after a response (LlmResponse) is received from the LLM, before it's processed further by the invoking agent.

Purpose: Allows inspection or modification of the raw LLM response. Use cases include

logging model outputs,
reformatting responses,
censoring sensitive information generated by the model,
parsing structured data from the LLM response and storing it in callback_context.state
or handling specific error codes.
Code
Tool Execution Callbacks
These callbacks are also specific to LlmAgent and trigger around the execution of tools (including FunctionTool, AgentTool, etc.) that the LLM might request.

Before Tool Callback
When: Called just before a specific tool's run_async method is invoked, after the LLM has generated a function call for it.

Purpose: Allows inspection and modification of tool arguments, performing authorization checks before execution, logging tool usage attempts, or implementing tool-level caching.

Return Value Effect:

If the callback returns None, the tool's run_async method is executed with the (potentially modified) args.
If a dictionary is returned, the tool's run_async method is skipped. The returned dictionary is used directly as the result of the tool call. This is useful for caching or overriding tool behavior.
Code
After Tool Callback
When: Called just after the tool's run_async method completes successfully.

Purpose: Allows inspection and modification of the tool's result before it's sent back to the LLM (potentially after summarization). Useful for logging tool results, post-processing or formatting results, or saving specific parts of the result to the session state.

Return Value Effect:

If the callback returns None, the original tool_response is used.
If a new dictionary is returned, it replaces the original tool_response. This allows modifying or filtering the result seen by the LLM.

Design Patterns and Best Practices for Callbacks
Callbacks offer powerful hooks into the agent lifecycle. Here are common design patterns illustrating how to leverage them effectively in ADK, followed by best practices for implementation.

Design Patterns
These patterns demonstrate typical ways to enhance or control agent behavior using callbacks:

1. Guardrails & Policy Enforcement
Pattern: Intercept requests before they reach the LLM or tools to enforce rules.
How: Use before_model_callback to inspect the LlmRequest prompt or before_tool_callback to inspect tool arguments (args). If a policy violation is detected (e.g., forbidden topics, profanity), return a predefined response (LlmResponse or dict) to block the operation and optionally update context.state to log the violation.
Example: A before_model_callback checks llm_request.contents for sensitive keywords and returns a standard "Cannot process this request" LlmResponse if found, preventing the LLM call.
2. Dynamic State Management
Pattern: Read from and write to session state within callbacks to make agent behavior context-aware and pass data between steps.
How: Access callback_context.state or tool_context.state. Modifications (state['key'] = value) are automatically tracked in the subsequent Event.actions.state_delta for persistence by the SessionService.
Example: An after_tool_callback saves a transaction_id from the tool's result to tool_context.state['last_transaction_id']. A later before_agent_callback might read state['user_tier'] to customize the agent's greeting.
3. Logging and Monitoring
Pattern: Add detailed logging at specific lifecycle points for observability and debugging.
How: Implement callbacks (e.g., before_agent_callback, after_tool_callback, after_model_callback) to print or send structured logs containing information like agent name, tool name, invocation ID, and relevant data from the context or arguments.
Example: Log messages like INFO: [Invocation: e-123] Before Tool: search_api - Args: {'query': 'ADK'}.
4. Caching
Pattern: Avoid redundant LLM calls or tool executions by caching results.
How: In before_model_callback or before_tool_callback, generate a cache key based on the request/arguments. Check context.state (or an external cache) for this key. If found, return the cached LlmResponse or result dict directly, skipping the actual operation. If not found, allow the operation to proceed and use the corresponding after_ callback (after_model_callback, after_tool_callback) to store the new result in the cache using the key.
Example: before_tool_callback for get_stock_price(symbol) checks state[f"cache:stock:{symbol}"]. If present, returns the cached price; otherwise, allows the API call and after_tool_callback saves the result to the state key.
5. Request/Response Modification
Pattern: Alter data just before it's sent to the LLM/tool or just after it's received.
How:
before_model_callback: Modify llm_request (e.g., add system instructions based on state).
after_model_callback: Modify the returned LlmResponse (e.g., format text, filter content).
before_tool_callback: Modify the tool args dictionary.
after_tool_callback: Modify the tool_response dictionary.
Example: before_model_callback appends "User language preference: Spanish" to llm_request.config.system_instruction if context.state['lang'] == 'es'.
6. Conditional Skipping of Steps
Pattern: Prevent standard operations (agent run, LLM call, tool execution) based on certain conditions.
How: Return a value from a before_ callback (Content from before_agent_callback, LlmResponse from before_model_callback, dict from before_tool_callback). The framework interprets this returned value as the result for that step, skipping the normal execution.
Example: before_tool_callback checks tool_context.state['api_quota_exceeded']. If True, it returns {'error': 'API quota exceeded'}, preventing the actual tool function from running.
7. Tool-Specific Actions (Authentication & Summarization Control)
Pattern: Handle actions specific to the tool lifecycle, primarily authentication and controlling LLM summarization of tool results.
How: Use ToolContext within tool callbacks (before_tool_callback, after_tool_callback).
Authentication: Call tool_context.request_credential(auth_config) in before_tool_callback if credentials are required but not found (e.g., via tool_context.get_auth_response or state check). This initiates the auth flow.
Summarization: Set tool_context.actions.skip_summarization = True if the raw dictionary output of the tool should be passed back to the LLM or potentially displayed directly, bypassing the default LLM summarization step.
Example: A before_tool_callback for a secure API checks for an auth token in state; if missing, it calls request_credential. An after_tool_callback for a tool returning structured JSON might set skip_summarization = True.
8. Artifact Handling
Pattern: Save or load session-related files or large data blobs during the agent lifecycle.
How: Use callback_context.save_artifact / tool_context.save_artifact to store data (e.g., generated reports, logs, intermediate data). Use load_artifact to retrieve previously stored artifacts. Changes are tracked via Event.actions.artifact_delta.
Example: An after_tool_callback for a "generate_report" tool saves the output file using tool_context.save_artifact("report.pdf", report_part). A before_agent_callback might load a configuration artifact using callback_context.load_artifact("agent_config.json").
Best Practices for Callbacks
Keep Focused: Design each callback for a single, well-defined purpose (e.g., just logging, just validation). Avoid monolithic callbacks.
Mind Performance: Callbacks execute synchronously within the agent's processing loop. Avoid long-running or blocking operations (network calls, heavy computation). Offload if necessary, but be aware this adds complexity.
Handle Errors Gracefully: Use try...except blocks within your callback functions. Log errors appropriately and decide if the agent invocation should halt or attempt recovery. Don't let callback errors crash the entire process.
Manage State Carefully:
Be deliberate about reading from and writing to context.state. Changes are immediately visible within the current invocation and persisted at the end of the event processing.
Use specific state keys rather than modifying broad structures to avoid unintended side effects.
Consider using state prefixes (State.APP_PREFIX, State.USER_PREFIX, State.TEMP_PREFIX) for clarity, especially with persistent SessionService implementations.
Consider Idempotency: If a callback performs actions with external side effects (e.g., incrementing an external counter), design it to be idempotent (safe to run multiple times with the same input) if possible, to handle potential retries in the framework or your application.
Test Thoroughly: Unit test your callback functions using mock context objects. Perform integration tests to ensure callbacks function correctly within the full agent flow.
Ensure Clarity: Use descriptive names for your callback functions. Add clear docstrings explaining their purpose, when they run, and any side effects (especially state modifications).
Use Correct Context Type: Always use the specific context type provided (CallbackContext for agent/model, ToolContext for tools) to ensure access to the appropriate methods and properties.
By applying these patterns and best practices, you can effectively use callbacks to create more robust, observable, and customized agent behaviors in ADK.


# Runtime

What is runtime?
The ADK Runtime is the underlying engine that powers your agent application during user interactions. It's the system that takes your defined agents, tools, and callbacks and orchestrates their execution in response to user input, managing the flow of information, state changes, and interactions with external services like LLMs or storage.

Think of the Runtime as the "engine" of your agentic application. You define the parts (agents, tools), and the Runtime handles how they connect and run together to fulfill a user's request.

Core Idea: The Event Loop
At its heart, the ADK Runtime operates on an Event Loop. This loop facilitates a back-and-forth communication between the Runner component and your defined "Execution Logic" (which includes your Agents, the LLM calls they make, Callbacks, and Tools).

intro_components.png

In simple terms:

The Runner receives a user query and asks the main Agent to start processing.
The Agent (and its associated logic) runs until it has something to report (like a response, a request to use a tool, or a state change) – it then yields an Event.
The Runner receives this Event, processes any associated actions (like saving state changes via Services), and forwards the event onwards (e.g., to the user interface).
Only after the Runner has processed the event does the Agent's logic resume from where it paused, now potentially seeing the effects of the changes committed by the Runner.
This cycle repeats until the agent has no more events to yield for the current user query.
This event-driven loop is the fundamental pattern governing how ADK executes your agent code.

The Heartbeat: The Event Loop - Inner workings
The Event Loop is the core operational pattern defining the interaction between the Runner and your custom code (Agents, Tools, Callbacks, collectively referred to as "Execution Logic" or "Logic Components" in the design document). It establishes a clear division of responsibilities:

Runner's Role (Orchestrator)
The Runner acts as the central coordinator for a single user invocation. Its responsibilities in the loop are:

Initiation: Receives the end user's query (new_message) and typically appends it to the session history via the SessionService.
Kick-off: Starts the event generation process by calling the main agent's execution method (e.g., agent_to_run.run_async(...)).
Receive & Process: Waits for the agent logic to yield an Event. Upon receiving an event, the Runner promptly processes it. This involves:
Using configured Services (SessionService, ArtifactService, MemoryService) to commit changes indicated in event.actions (like state_delta, artifact_delta).
Performing other internal bookkeeping.
Yield Upstream: Forwards the processed event onwards (e.g., to the calling application or UI for rendering).
Iterate: Signals the agent logic that processing is complete for the yielded event, allowing it to resume and generate the next event.
Conceptual Runner Loop:


# Simplified view of Runner's main loop logic
def run(new_query, ...) -> Generator[Event]:
    # 1. Append new_query to session event history (via SessionService)
    session_service.append_event(session, Event(author='user', content=new_query))

    # 2. Kick off event loop by calling the agent
    agent_event_generator = agent_to_run.run_async(context)

    async for event in agent_event_generator:
        # 3. Process the generated event and commit changes
        session_service.append_event(session, event) # Commits state/artifact deltas etc.
        # memory_service.update_memory(...) # If applicable
        # artifact_service might have already been called via context during agent run

        # 4. Yield event for upstream processing (e.g., UI rendering)
        yield event
        # Runner implicitly signals agent generator can continue after yielding
Execution Logic's Role (Agent, Tool, Callback)
Your code within agents, tools, and callbacks is responsible for the actual computation and decision-making. Its interaction with the loop involves:

Execute: Runs its logic based on the current InvocationContext, including the session state as it was when execution resumed.
Yield: When the logic needs to communicate (send a message, call a tool, report a state change), it constructs an Event containing the relevant content and actions, and then yields this event back to the Runner.
Pause: Crucially, execution of the agent logic pauses immediately after the yield statement. It waits for the Runner to complete step 3 (processing and committing).
Resume: Only after the Runner has processed the yielded event does the agent logic resume execution from the statement immediately following the yield.
See Updated State: Upon resumption, the agent logic can now reliably access the session state (ctx.session.state) reflecting the changes that were committed by the Runner from the previously yielded event.
Conceptual Execution Logic:


# Simplified view of logic inside Agent.run_async, callbacks, or tools

# ... previous code runs based on current state ...

# 1. Determine a change or output is needed, construct the event
# Example: Updating state
update_data = {'field_1': 'value_2'}
event_with_state_change = Event(
    author=self.name,
    actions=EventActions(state_delta=update_data),
    content=types.Content(parts=[types.Part(text="State updated.")])
    # ... other event fields ...
)

# 2. Yield the event to the Runner for processing & commit
yield event_with_state_change
# <<<<<<<<<<<< EXECUTION PAUSES HERE >>>>>>>>>>>>

# <<<<<<<<<<<< RUNNER PROCESSES & COMMITS THE EVENT >>>>>>>>>>>>

# 3. Resume execution ONLY after Runner is done processing the above event.
# Now, the state committed by the Runner is reliably reflected.
# Subsequent code can safely assume the change from the yielded event happened.
val = ctx.session.state['field_1']
# here `val` is guaranteed to be "value_2" (assuming Runner committed successfully)
print(f"Resumed execution. Value of field_1 is now: {val}")

# ... subsequent code continues ...
# Maybe yield another event later...
This cooperative yield/pause/resume cycle between the Runner and your Execution Logic, mediated by Event objects, forms the core of the ADK Runtime.

Key components of the Runtime
Several components work together within the ADK Runtime to execute an agent invocation. Understanding their roles clarifies how the event loop functions:

Runner
Role: The main entry point and orchestrator for a single user query (run_async).
Function: Manages the overall Event Loop, receives events yielded by the Execution Logic, coordinates with Services to process and commit event actions (state/artifact changes), and forwards processed events upstream (e.g., to the UI). It essentially drives the conversation turn by turn based on yielded events. (Defined in google.adk.runners.runner.py).
Execution Logic Components
Role: The parts containing your custom code and the core agent capabilities.
Components:
Agent (BaseAgent, LlmAgent, etc.): Your primary logic units that process information and decide on actions. They implement the _run_async_impl method which yields events.
Tools (BaseTool, FunctionTool, AgentTool, etc.): External functions or capabilities used by agents (often LlmAgent) to interact with the outside world or perform specific tasks. They execute and return results, which are then wrapped in events.
Callbacks (Functions): User-defined functions attached to agents (e.g., before_agent_callback, after_model_callback) that hook into specific points in the execution flow, potentially modifying behavior or state, whose effects are captured in events.
Function: Perform the actual thinking, calculation, or external interaction. They communicate their results or needs by yielding Event objects and pausing until the Runner processes them.
Event
Role: The message passed back and forth between the Runner and the Execution Logic.
Function: Represents an atomic occurrence (user input, agent text, tool call/result, state change request, control signal). It carries both the content of the occurrence and the intended side effects (actions like state_delta). (Defined in google.adk.events.event.py).
Services
Role: Backend components responsible for managing persistent or shared resources. Used primarily by the Runner during event processing.
Components:
SessionService (BaseSessionService, InMemorySessionService, etc.): Manages Session objects, including saving/loading them, applying state_delta to the session state, and appending events to the event history.
ArtifactService (BaseArtifactService, InMemoryArtifactService, GcsArtifactService, etc.): Manages the storage and retrieval of binary artifact data. Although save_artifact is called via context during execution logic, the artifact_delta in the event confirms the action for the Runner/SessionService.
MemoryService (BaseMemoryService, etc.): (Optional) Manages long-term semantic memory across sessions for a user.
Function: Provide the persistence layer. The Runner interacts with them to ensure changes signaled by event.actions are reliably stored before the Execution Logic resumes.
Session
Role: A data container holding the state and history for one specific conversation between a user and the application.
Function: Stores the current state dictionary, the list of all past events (event history), and references to associated artifacts. It's the primary record of the interaction, managed by the SessionService. (Defined in google.adk.sessions.session.py).
Invocation
Role: A conceptual term representing everything that happens in response to a single user query, from the moment the Runner receives it until the agent logic finishes yielding events for that query.
Function: An invocation might involve multiple agent runs (if using agent transfer or AgentTool), multiple LLM calls, tool executions, and callback executions, all tied together by a single invocation_id within the InvocationContext.
These players interact continuously through the Event Loop to process a user's request.

How It Works: A Simplified Invocation
Let's trace a simplified flow for a typical user query that involves an LLM agent calling a tool:

intro_components.png

Step-by-Step Breakdown
User Input: The User sends a query (e.g., "What's the capital of France?").
Runner Starts: Runner.run_async begins. It interacts with the SessionService to load the relevant Session and adds the user query as the first Event to the session history. An InvocationContext (ctx) is prepared.
Agent Execution: The Runner calls agent.run_async(ctx) on the designated root agent (e.g., an LlmAgent).
LLM Call (Example): The Agent_Llm determines it needs information, perhaps by calling a tool. It prepares a request for the LLM. Let's assume the LLM decides to call MyTool.
Yield FunctionCall Event: The Agent_Llm receives the FunctionCall response from the LLM, wraps it in an Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)])), and yields this event.
Agent Pauses: The Agent_Llm's execution pauses immediately after the yield.
Runner Processes: The Runner receives the FunctionCall event. It passes it to the SessionService to record it in the history. The Runner then yields the event upstream to the User (or application).
Agent Resumes: The Runner signals that the event is processed, and Agent_Llm resumes execution.
Tool Execution: The Agent_Llm's internal flow now proceeds to execute the requested MyTool. It calls tool.run_async(...).
Tool Returns Result: MyTool executes and returns its result (e.g., {'result': 'Paris'}).
Yield FunctionResponse Event: The agent (Agent_Llm) wraps the tool result into an Event containing a FunctionResponse part (e.g., Event(author='Agent_Llm', content=Content(role='user', parts=[Part(function_response=...)]))). This event might also contain actions if the tool modified state (state_delta) or saved artifacts (artifact_delta). The agent yields this event.
Agent Pauses: Agent_Llm pauses again.
Runner Processes: Runner receives the FunctionResponse event. It passes it to SessionService which applies any state_delta/artifact_delta and adds the event to history. Runner yields the event upstream.
Agent Resumes: Agent_Llm resumes, now knowing the tool result and any state changes are committed.
Final LLM Call (Example): Agent_Llm sends the tool result back to the LLM to generate a natural language response.
Yield Final Text Event: Agent_Llm receives the final text from the LLM, wraps it in an Event(author='Agent_Llm', content=Content(parts=[Part(text=...)])), and yields it.
Agent Pauses: Agent_Llm pauses.
Runner Processes: Runner receives the final text event, passes it to SessionService for history, and yields it upstream to the User. This is likely marked as the is_final_response().
Agent Resumes & Finishes: Agent_Llm resumes. Having completed its task for this invocation, its run_async generator finishes.
Runner Completes: The Runner sees the agent's generator is exhausted and finishes its loop for this invocation.
This yield/pause/process/resume cycle ensures that state changes are consistently applied and that the execution logic always operates on the most recently committed state after yielding an event.

Important Runtime Behaviors
Understanding a few key aspects of how the ADK Runtime handles state, streaming, and asynchronous operations is crucial for building predictable and efficient agents.

State Updates & Commitment Timing
The Rule: When your code (in an agent, tool, or callback) modifies the session state (e.g., context.state['my_key'] = 'new_value'), this change is initially recorded locally within the current InvocationContext. The change is only guaranteed to be persisted (saved by the SessionService) after the Event carrying the corresponding state_delta in its actions has been yield-ed by your code and subsequently processed by the Runner.

Implication: Code that runs after resuming from a yield can reliably assume that the state changes signaled in the yielded event have been committed.


# Inside agent logic (conceptual)

# 1. Modify state
ctx.session.state['status'] = 'processing'
event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))

# 2. Yield event with the delta
yield event1
# --- PAUSE --- Runner processes event1, SessionService commits 'status' = 'processing' ---

# 3. Resume execution
# Now it's safe to rely on the committed state
current_status = ctx.session.state['status'] # Guaranteed to be 'processing'
print(f"Status after resuming: {current_status}")
"Dirty Reads" of Session State
Definition: While commitment happens after the yield, code running later within the same invocation, but before the state-changing event is actually yielded and processed, can often see the local, uncommitted changes. This is sometimes called a "dirty read".
Example:

# Code in before_agent_callback
callback_context.state['field_1'] = 'value_1'
# State is locally set to 'value_1', but not yet committed by Runner

# ... agent runs ...

# Code in a tool called later *within the same invocation*
# Readable (dirty read), but 'value_1' isn't guaranteed persistent yet.
val = tool_context.state['field_1'] # 'val' will likely be 'value_1' here
print(f"Dirty read value in tool: {val}")

# Assume the event carrying the state_delta={'field_1': 'value_1'}
# is yielded *after* this tool runs and is processed by the Runner.
Implications:
Benefit: Allows different parts of your logic within a single complex step (e.g., multiple callbacks or tool calls before the next LLM turn) to coordinate using state without waiting for a full yield/commit cycle.
Caveat: Relying heavily on dirty reads for critical logic can be risky. If the invocation fails before the event carrying the state_delta is yielded and processed by the Runner, the uncommitted state change will be lost. For critical state transitions, ensure they are associated with an event that gets successfully processed.
Streaming vs. Non-Streaming Output (partial=True)
This primarily relates to how responses from the LLM are handled, especially when using streaming generation APIs.

Streaming: The LLM generates its response token-by-token or in small chunks.
The framework (often within BaseLlmFlow) yields multiple Event objects for a single conceptual response. Most of these events will have partial=True.
The Runner, upon receiving an event with partial=True, typically forwards it immediately upstream (for UI display) but skips processing its actions (like state_delta).
Eventually, the framework yields a final event for that response, marked as non-partial (partial=False or implicitly via turn_complete=True).
The Runner fully processes only this final event, committing any associated state_delta or artifact_delta.
Non-Streaming: The LLM generates the entire response at once. The framework yields a single event marked as non-partial, which the Runner processes fully.
Why it Matters: Ensures that state changes are applied atomically and only once based on the complete response from the LLM, while still allowing the UI to display text progressively as it's generated.
Async is Primary (run_async)
Core Design: The ADK Runtime is fundamentally built on Python's asyncio library to handle concurrent operations (like waiting for LLM responses or tool executions) efficiently without blocking.
Main Entry Point: Runner.run_async is the primary method for executing agent invocations. All core runnable components (Agents, specific flows) use async def methods internally.
Synchronous Convenience (run): A synchronous Runner.run method exists mainly for convenience (e.g., in simple scripts or testing environments). However, internally, Runner.run typically just calls Runner.run_async and manages the async event loop execution for you.
Developer Experience: You should generally design your application logic (e.g., web servers using ADK) using asyncio.
Sync Callbacks/Tools: The framework aims to handle both async def and regular def functions provided as tools or callbacks seamlessly. Long-running synchronous tools or callbacks, especially those performing blocking I/O, can potentially block the main asyncio event loop. The framework might use mechanisms like asyncio.to_thread to mitigate this by running such blocking synchronous code in a separate thread pool, preventing it from stalling other asynchronous tasks. CPU-bound synchronous code, however, will still block the thread it runs on.
Understanding these behaviors helps you write more robust ADK applications and debug issues related to state consistency, streaming updates, and asynchronous execution.

# Events
Events:
Events are the fundamental units of information flow within the Agent Development Kit (ADK). They represent every significant occurrence during an agent's interaction lifecycle, from initial user input to the final response and all the steps in between. Understanding events is crucial because they are the primary way components communicate, state is managed, and control flow is directed.

What Events Are and Why They Matter
An Event in ADK is an immutable record representing a specific point in the agent's execution. It captures user messages, agent replies, requests to use tools (function calls), tool results, state changes, control signals, and errors. Technically, it's an instance of the google.adk.events.Event class, which builds upon the basic LlmResponse structure by adding essential ADK-specific metadata and an actions payload.


# Conceptual Structure of an Event
# from google.adk.events import Event, EventActions
# from google.genai import types

# class Event(LlmResponse): # Simplified view
#     # --- LlmResponse fields ---
#     content: Optional[types.Content]
#     partial: Optional[bool]
#     # ... other response fields ...

#     # --- ADK specific additions ---
#     author: str          # 'user' or agent name
#     invocation_id: str   # ID for the whole interaction run
#     id: str              # Unique ID for this specific event
#     timestamp: float     # Creation time
#     actions: EventActions # Important for side-effects & control
#     branch: Optional[str] # Hierarchy path
#     # ...
Events are central to ADK's operation for several key reasons:

Communication: They serve as the standard message format between the user interface, the Runner, agents, the LLM, and tools. Everything flows as an Event.
Signaling State & Artifact Changes: Events carry instructions for state modifications via event.actions.state_delta and track artifact updates via event.actions.artifact_delta. The SessionService uses these signals to ensure persistence.
Control Flow: Specific fields like event.actions.transfer_to_agent or event.actions.escalate act as signals that direct the framework, determining which agent runs next or if a loop should terminate.
History & Observability: The sequence of events recorded in session.events provides a complete, chronological history of an interaction, invaluable for debugging, auditing, and understanding agent behavior step-by-step.
In essence, the entire process, from a user's query to the agent's final answer, is orchestrated through the generation, interpretation, and processing of Event objects.

Understanding and Using Events
As a developer, you'll primarily interact with the stream of events yielded by the Runner. Here's how to understand and extract information from them:

Identifying Event Origin and Type
Quickly determine what an event represents by checking:

Who sent it? (event.author)
'user': Indicates input directly from the end-user.
'AgentName': Indicates output or action from a specific agent (e.g., 'WeatherAgent', 'SummarizerAgent').
What's the main payload? (event.content and event.content.parts)
Text: If event.content.parts[0].text exists, it's likely a conversational message.
Tool Call Request: Check event.get_function_calls(). If not empty, the LLM is asking to execute one or more tools. Each item in the list has .name and .args.
Tool Result: Check event.get_function_responses(). If not empty, this event carries the result(s) from tool execution(s). Each item has .name and .response (the dictionary returned by the tool). Note: For history structuring, the role inside the content is often 'user', but the event author is typically the agent that requested the tool call.
Is it streaming output? (event.partial)
True: This is an incomplete chunk of text from the LLM; more will follow.
False or None: This part of the content is complete (though the overall turn might not be finished if turn_complete is also false).

# Pseudocode: Basic event identification
# async for event in runner.run_async(...):
#     print(f"Event from: {event.author}")
#
#     if event.content and event.content.parts:
#         if event.get_function_calls():
#             print("  Type: Tool Call Request")
#         elif event.get_function_responses():
#             print("  Type: Tool Result")
#         elif event.content.parts[0].text:
#             if event.partial:
#                 print("  Type: Streaming Text Chunk")
#             else:
#                 print("  Type: Complete Text Message")
#         else:
#             print("  Type: Other Content (e.g., code result)")
#     elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
#         print("  Type: State/Artifact Update")
#     else:
#         print("  Type: Control Signal or Other")
Extracting Key Information
Once you know the event type, access the relevant data:

Text Content: text = event.content.parts[0].text (Always check event.content and event.content.parts first).
Function Call Details:

calls = event.get_function_calls()
if calls:
    for call in calls:
        tool_name = call.name
        arguments = call.args # This is usually a dictionary
        print(f"  Tool: {tool_name}, Args: {arguments}")
        # Application might dispatch execution based on this
Function Response Details:

responses = event.get_function_responses()
if responses:
    for response in responses:
        tool_name = response.name
        result_dict = response.response # The dictionary returned by the tool
        print(f"  Tool Result: {tool_name} -> {result_dict}")
Identifiers:
event.id: Unique ID for this specific event instance.
event.invocation_id: ID for the entire user-request-to-final-response cycle this event belongs to. Useful for logging and tracing.
Detecting Actions and Side Effects
The event.actions object signals changes that occurred or should occur. Always check if event.actions exists before accessing its fields.

State Changes: delta = event.actions.state_delta gives you a dictionary of {key: value} pairs that were modified in the session state during the step that produced this event.

if event.actions and event.actions.state_delta:
    print(f"  State changes: {event.actions.state_delta}")
    # Update local UI or application state if necessary
Artifact Saves: artifact_changes = event.actions.artifact_delta gives you a dictionary of {filename: version} indicating which artifacts were saved and their new version number.

if event.actions and event.actions.artifact_delta:
    print(f"  Artifacts saved: {event.actions.artifact_delta}")
    # UI might refresh an artifact list
Control Flow Signals: Check boolean flags or string values:
event.actions.transfer_to_agent (string): Control should pass to the named agent.
event.actions.escalate (bool): A loop should terminate.
event.actions.skip_summarization (bool): A tool result should not be summarized by the LLM.

if event.actions:
    if event.actions.transfer_to_agent:
        print(f"  Signal: Transfer to {event.actions.transfer_to_agent}")
    if event.actions.escalate:
        print("  Signal: Escalate (terminate loop)")
    if event.actions.skip_summarization:
        print("  Signal: Skip summarization for tool result")
Determining if an Event is a "Final" Response
Use the built-in helper method event.is_final_response() to identify events suitable for display as the agent's complete output for a turn.

Purpose: Filters out intermediate steps (like tool calls, partial streaming text, internal state updates) from the final user-facing message(s).
When True?
The event contains a tool result (function_response) and skip_summarization is True.
The event contains a tool call (function_call) for a tool marked as is_long_running=True.
OR, all of the following are met:
No function calls (get_function_calls() is empty).
No function responses (get_function_responses() is empty).
Not a partial stream chunk (partial is not True).
Doesn't end with a code execution result that might need further processing/display.
Usage: Filter the event stream in your application logic.


# Pseudocode: Handling final responses in application
# full_response_text = ""
# async for event in runner.run_async(...):
#     # Accumulate streaming text if needed...
#     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
#         full_response_text += event.content.parts[0].text
#
#     # Check if it's a final, displayable event
#     if event.is_final_response():
#         print("\n--- Final Output Detected ---")
#         if event.content and event.content.parts and event.content.parts[0].text:
#              # If it's the final part of a stream, use accumulated text
#              final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
#              print(f"Display to user: {final_text.strip()}")
#              full_response_text = "" # Reset accumulator
#         elif event.actions.skip_summarization:
#              # Handle displaying the raw tool result if needed
#              response_data = event.get_function_responses()[0].response
#              print(f"Display raw tool result: {response_data}")
#         elif event.long_running_tool_ids:
#              print("Display message: Tool is running in background...")
#         else:
#              # Handle other types of final responses if applicable
#              print("Display: Final non-textual response or signal.")
By carefully examining these aspects of an event, you can build robust applications that react appropriately to the rich information flowing through the ADK system.

How Events Flow: Generation and Processing
Events are created at different points and processed systematically by the framework. Understanding this flow helps clarify how actions and history are managed.

Generation Sources:

User Input: The Runner typically wraps initial user messages or mid-conversation inputs into an Event with author='user'.
Agent Logic: Agents (BaseAgent, LlmAgent) explicitly yield Event(...) objects (setting author=self.name) to communicate responses or signal actions.
LLM Responses: The ADK model integration layer (e.g., google_llm.py) translates raw LLM output (text, function calls, errors) into Event objects, authored by the calling agent.
Tool Results: After a tool executes, the framework generates an Event containing the function_response. The author is typically the agent that requested the tool, while the role inside the content is set to 'user' for the LLM history.
Processing Flow:

Yield: An event is generated and yielded by its source.
Runner Receives: The main Runner executing the agent receives the event.
SessionService Processing (append_event): The Runner sends the event to the configured SessionService. This is a critical step:
Applies Deltas: The service merges event.actions.state_delta into session.state and updates internal records based on event.actions.artifact_delta. (Note: The actual artifact saving usually happened earlier when context.save_artifact was called).
Finalizes Metadata: Assigns a unique event.id if not present, may update event.timestamp.
Persists to History: Appends the processed event to the session.events list.
External Yield: The Runner yields the processed event outwards to the calling application (e.g., the code that invoked runner.run_async).
This flow ensures that state changes and history are consistently recorded alongside the communication content of each event.

Common Event Examples (Illustrative Patterns)
Here are concise examples of typical events you might see in the stream:

User Input:

{
  "author": "user",
  "invocation_id": "e-xyz...",
  "content": {"parts": [{"text": "Book a flight to London for next Tuesday"}]}
  // actions usually empty
}
Agent Final Text Response: (is_final_response() == True)

{
  "author": "TravelAgent",
  "invocation_id": "e-xyz...",
  "content": {"parts": [{"text": "Okay, I can help with that. Could you confirm the departure city?"}]},
  "partial": false,
  "turn_complete": true
  // actions might have state delta, etc.
}
Agent Streaming Text Response: (is_final_response() == False)

{
  "author": "SummaryAgent",
  "invocation_id": "e-abc...",
  "content": {"parts": [{"text": "The document discusses three main points:"}]},
  "partial": true,
  "turn_complete": false
}
// ... more partial=True events follow ...
Tool Call Request (by LLM): (is_final_response() == False)

{
  "author": "TravelAgent",
  "invocation_id": "e-xyz...",
  "content": {"parts": [{"function_call": {"name": "find_airports", "args": {"city": "London"}}}]}
  // actions usually empty
}
Tool Result Provided (to LLM): (is_final_response() depends on skip_summarization)

{
  "author": "TravelAgent", // Author is agent that requested the call
  "invocation_id": "e-xyz...",
  "content": {
    "role": "user", // Role for LLM history
    "parts": [{"function_response": {"name": "find_airports", "response": {"result": ["LHR", "LGW", "STN"]}}}]
  }
  // actions might have skip_summarization=True
}
State/Artifact Update Only: (is_final_response() == False)

{
  "author": "InternalUpdater",
  "invocation_id": "e-def...",
  "content": null,
  "actions": {
    "state_delta": {"user_status": "verified"},
    "artifact_delta": {"verification_doc.pdf": 2}
  }
}
Agent Transfer Signal: (is_final_response() == False)

{
  "author": "OrchestratorAgent",
  "invocation_id": "e-789...",
  "content": {"parts": [{"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "BillingAgent"}}}]},
  "actions": {"transfer_to_agent": "BillingAgent"} // Added by framework
}
Loop Escalation Signal: (is_final_response() == False)

{
  "author": "CheckerAgent",
  "invocation_id": "e-loop...",
  "content": {"parts": [{"text": "Maximum retries reached."}]}, // Optional content
  "actions": {"escalate": true}
}
Additional Context and Event Details
Beyond the core concepts, here are a few specific details about context and events that are important for certain use cases:

ToolContext.function_call_id (Linking Tool Actions):

When an LLM requests a tool (FunctionCall), that request has an ID. The ToolContext provided to your tool function includes this function_call_id.
Importance: This ID is crucial for linking actions like authentication (request_credential, get_auth_response) back to the specific tool request that initiated them, especially if multiple tools are called in one turn. The framework uses this ID internally.
How State/Artifact Changes are Recorded:

When you modify state (context.state['key'] = value) or save an artifact (context.save_artifact(...)) using CallbackContext or ToolContext, these changes aren't immediately written to persistent storage.
Instead, they populate the state_delta and artifact_delta fields within the EventActions object.
This EventActions object is attached to the next event generated after the change (e.g., the agent's response or a tool result event).
The SessionService.append_event method reads these deltas from the incoming event and applies them to the session's persistent state and artifact records. This ensures changes are tied chronologically to the event stream.
State Scope Prefixes (app:, user:, temp:):

When managing state via context.state, you can optionally use prefixes:
app:my_setting: Suggests state relevant to the entire application (requires a persistent SessionService).
user:user_preference: Suggests state relevant to the specific user across sessions (requires a persistent SessionService).
temp:intermediate_result or no prefix: Typically session-specific or temporary state for the current invocation.
The underlying SessionService determines how these prefixes are handled for persistence.
Error Events:

An Event can represent an error. Check the event.error_code and event.error_message fields (inherited from LlmResponse).
Errors might originate from the LLM (e.g., safety filters, resource limits) or potentially be packaged by the framework if a tool fails critically. Check tool FunctionResponse content for typical tool-specific errors.

// Example Error Event (conceptual)
{
  "author": "LLMAgent",
  "invocation_id": "e-err...",
  "content": null,
  "error_code": "SAFETY_FILTER_TRIGGERED",
  "error_message": "Response blocked due to safety settings.",
  "actions": {}
}
These details provide a more complete picture for advanced use cases involving tool authentication, state persistence scope, and error handling within the event stream.

Best Practices for Working with Events
To use events effectively in your ADK applications:

Clear Authorship: When building custom agents (BaseAgent), ensure yield Event(author=self.name, ...) to correctly attribute agent actions in the history. The framework generally handles authorship correctly for LLM/tool events.
Semantic Content & Actions: Use event.content for the core message/data (text, function call/response). Use event.actions specifically for signaling side effects (state/artifact deltas) or control flow (transfer, escalate, skip_summarization).
Idempotency Awareness: Understand that the SessionService is responsible for applying the state/artifact changes signaled in event.actions. While ADK services aim for consistency, consider potential downstream effects if your application logic re-processes events.
Use is_final_response(): Rely on this helper method in your application/UI layer to identify complete, user-facing text responses. Avoid manually replicating its logic.
Leverage History: The session.events list is your primary debugging tool. Examine the sequence of authors, content, and actions to trace execution and diagnose issues.
Use Metadata: Use invocation_id to correlate all events within a single user interaction. Use event.id to reference specific, unique occurrences.
Treating events as structured messages with clear purposes for their content and actions is key to building, debugging, and managing complex agent behaviors in ADK.
# Models

## Using Different Models with ADK

The Agent Development Kit (ADK) is designed for flexibility, allowing you to integrate various Large Language Models (LLMs) into your agents. While the setup for Google Gemini models is covered in the Setup Foundation Models guide, this page details how to leverage Gemini effectively and integrate other popular models, including those hosted externally or running locally.

ADK primarily uses two mechanisms for model integration:

1. **Direct String / Registry**: For models tightly integrated with Google Cloud (like Gemini models accessed via Google AI Studio or Vertex AI) or models hosted on Vertex AI endpoints. You typically provide the model name or endpoint resource string directly to the `LlmAgent`. ADK's internal registry resolves this string to the appropriate backend client, often utilizing the `google-genai` library.

2. **Wrapper Classes**: For broader compatibility, especially with models outside the Google ecosystem or those requiring specific client configurations (like models accessed via LiteLLM). You instantiate a specific wrapper class (e.g., `LiteLlm`) and pass this object as the `model` parameter to your `LlmAgent`.

## Using Google Gemini Models

This is the most direct way to use Google's flagship models within ADK.

### Integration Method:
Pass the model's identifier string directly to the `model` parameter of `LlmAgent` (or its alias, `Agent`).

### Backend Options & Setup:

The `google-genai` library, used internally by ADK for Gemini, can connect through either Google AI Studio or Vertex AI.

#### Google AI Studio

* **Use Case**: Ideal for development, prototyping, and personal projects.
* **Setup**: Typically requires an API key set as an environment variable:
  ```
  export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
  export GOOGLE_GENAI_USE_VERTEXAI=FALSE
  ```
* **Models**: Find all available models on the [Google AI for Developers site](https://ai.google.dev/).

#### Vertex AI

* **Use Case**: Recommended for production applications, leveraging Google Cloud infrastructure. Gemini on Vertex AI supports enterprise-grade features, security, and compliance controls.
* **Setup**:
  * Authenticate using Application Default Credentials (ADC):
    ```
    gcloud auth application-default login
    ```
  * Set your Google Cloud project and location:
    ```
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```
  * Enable Vertex AI:
    ```
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

# Evaluate

Why Evaluate Agents
In traditional software development, unit tests and integration tests provide confidence that code functions as expected and remains stable through changes. These tests provide a clear "pass/fail" signal, guiding further development. However, LLM agents introduce a level of variability that makes traditional testing approaches insufficient.

Due to the probabilistic nature of models, deterministic "pass/fail" assertions are often unsuitable for evaluating agent performance. Instead, we need qualitative evaluations of both the final output and the agent's trajectory - the sequence of steps taken to reach the solution. This involves assessing the quality of the agent's decisions, its reasoning process, and the final result.

This may seem like a lot of extra work to set up, but the investment of automating evaluations pays off quickly. If you intend to progress beyond prototype, this is a highly recommended best practice.

intro_components.png

Preparing for Agent Evaluations
Before automating agent evaluations, define clear objectives and success criteria:

Define Success: What constitutes a successful outcome for your agent?
Identify Critical Tasks: What are the essential tasks your agent must accomplish?
Choose Relevant Metrics: What metrics will you track to measure performance?
These considerations will guide the creation of evaluation scenarios and enable effective monitoring of agent behavior in real-world deployments.

What to Evaluate?
To bridge the gap between a proof-of-concept and a production-ready AI agent, a robust and automated evaluation framework is essential. Unlike evaluating generative models, where the focus is primarily on the final output, agent evaluation requires a deeper understanding of the decision-making process. Agent evaluation can be broken down into two components:

Evaluating Trajectory and Tool Use: Analyzing the steps an agent takes to reach a solution, including its choice of tools, strategies, and the efficiency of its approach.
Evaluating the Final Response: Assessing the quality, relevance, and correctness of the agent's final output.
The trajectory is just a list of steps the agent took before it returned to the user. We can compare that against the list of steps we expect the agent to have taken.

Evaluating trajectory and tool use
Before responding to a user, an agent typically performs a series of actions, which we refer to as a 'trajectory.' It might compare the user input with session history to disambiguate a term, or lookup a policy document, search a knowledge base or invoke an API to save a ticket. We call this a ‘trajectory’ of actions. Evaluating an agent's performance requires comparing its actual trajectory to an expected, or ideal, one. This comparison can reveal errors and inefficiencies in the agent's process. The expected trajectory represents the ground truth -- the list of steps we anticipate the agent should take.

For example:


// Trajectory evaluation will compare
expected_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
actual_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
Several ground-truth-based trajectory evaluations exist:

Exact match: Requires a perfect match to the ideal trajectory.
In-order match: Requires the correct actions in the correct order, allows for extra actions.
Any-order match: Requires the correct actions in any order, allows for extra actions.
Precision: Measures the relevance/correctness of predicted actions.
Recall: Measures how many essential actions are captured in the prediction.
Single-tool use: Checks for the inclusion of a specific action.
Choosing the right evaluation metric depends on the specific requirements and goals of your agent. For instance, in high-stakes scenarios, an exact match might be crucial, while in more flexible situations, an in-order or any-order match might suffice.

How Evaluation works with the ADK
The ADK offers two methods for evaluating agent performance against predefined datasets and evaluation criteria. While conceptually similar, they differ in the amount of data they can process, which typically dictates the appropriate use case for each.

First approach: Using a test file
This approach involves creating individual test files, each representing a single, simple agent-model interaction (a session). It's most effective during active agent development, serving as a form of unit testing. These tests are designed for rapid execution and should focus on simple session complexity. Each test file contains a single session, which may consist of multiple turns. A turn represents a single interaction between the user and the agent. Each turn includes

query: This is the user query.
expected_tool_use: The tool call(s) that we expect the agent to make in order to respond correctly to the user query.
expected_intermediate_agent_responses: This field contains the natural language responses produced by the agent as it progresses towards a final answer. These responses are typical in multi-agent systems where a root agent relies on child agents to accomplish a task. While generally not directly relevant to end-users, these intermediate responses are valuable for developers. They provide insight into the agent's reasoning path and help verify that it followed the correct steps to generate the final response.
reference: The expected final response from the model.
You can give the file any name for example evaluation.test.json.The framework only checks for the .test.json suffix, and the preceding part of the filename is not constrained. Here is a test file with a few examples:


[
  {
    "query": "hi",
    "expected_tool_use": [],
    "expected_intermediate_agent_responses": [],
    "reference": "Hello! What can I do for you?\n"
  },
  {
    "query": "roll a die for me",
    "expected_tool_use": [
      {
        "tool_name": "roll_die",
        "tool_input": {
          "sides": 6
        }
      }
    ],
    "expected_intermediate_agent_responses": [],
  },
  {
    "query": "what's the time now?",
    "expected_tool_use": [],
    "expected_intermediate_agent_responses": [],
    "reference": "I'm sorry, I cannot access real-time information, including the current time. My capabilities are limited to rolling dice and checking prime numbers.\n"
  }
]
Test files can be organized into folders. Optionally, a folder can also include a test_config.json file that specifies the evaluation criteria.

Second approach: Using An Evalset File
The evalset approach utilizes a dedicated dataset called an "evalset" for evaluating agent-model interactions. Similar to a test file, the evalset contains example interactions. However, an evalset can contain multiple, potentially lengthy sessions, making it ideal for simulating complex, multi-turn conversations. Due to its ability to represent complex sessions, the evalset is well-suited for integration tests. These tests are typically run less frequently than unit tests due to their more extensive nature.

An evalset file contains multiple "evals," each representing a distinct session. Each eval consists of one or more "turns," which include the user query, expected tool use, expected intermediate agent responses, and a reference response. These fields have the same meaning as they do in the test file approach. Each eval is identified by a unique name. Furthermore, each eval includes an associated initial session state.

Creating evalsets manually can be complex, therefore UI tools are provided to help capture relevant sessions and easily convert them into evals within your evalset. Learn more about using the web UI for evaluation below. Here is an example evalset containing two sessions.


[
  {
    "name": "roll_16_sided_dice_and_then_check_if_6151953_is_prime",
    "data": [
      {
        "query": "What can you do?",
        "expected_tool_use": [],
        "expected_intermediate_agent_responses": [],
        "reference": "I can roll dice of different sizes and check if a number is prime. I can also use multiple tools in parallel.\n"
      },
      {
        "query": "Roll a 16 sided dice for me",
        "expected_tool_use": [
          {
            "tool_name": "roll_die",
            "tool_input": {
              "sides": 16
            }
          }
        ],
        "expected_intermediate_agent_responses": [],
        "reference": "I rolled a 16 sided die and got 13.\n"
      },
      {
        "query": "Is 6151953  a prime number?",
        "expected_tool_use": [
          {
            "tool_name": "check_prime",
            "tool_input": {
              "nums": [
                6151953
              ]
            }
          }
        ],
        "expected_intermediate_agent_responses": [],
        "reference": "No, 6151953 is not a prime number.\n"
      }
    ],
    "initial_session": {
      "state": {},
      "app_name": "hello_world",
      "user_id": "user"
    }
  },
  {
    "name": "roll_17_sided_dice_twice",
    "data": [
      {
        "query": "What can you do?",
        "expected_tool_use": [],
        "expected_intermediate_agent_responses": [],
        "reference": "I can roll dice of different sizes and check if a number is prime. I can also use multiple tools in parallel.\n"
      },
      {
        "query": "Roll a 17 sided dice twice for me",
        "expected_tool_use": [
          {
            "tool_name": "roll_die",
            "tool_input": {
              "sides": 17
            }
          },
          {
            "tool_name": "roll_die",
            "tool_input": {
              "sides": 17
            }
          }
        ],
        "expected_intermediate_agent_responses": [],
        "reference": "I have rolled a 17 sided die twice. The first roll was 13 and the second roll was 4.\n"
      }
    ],
    "initial_session": {
      "state": {},
      "app_name": "hello_world",
      "user_id": "user"
    }
  }
]
Evaluation Criteria
The evaluation criteria define how the agent's performance is measured against the evalset. The following metrics are supported:

tool_trajectory_avg_score: This metric compares the agent's actual tool usage during the evaluation against the expected tool usage defined in the expected_tool_use field. Each matching tool usage step receives a score of 1, while a mismatch receives a score of 0. The final score is the average of these matches, representing the accuracy of the tool usage trajectory.
response_match_score: This metric compares the agent's final natural language response to the expected final response, stored in the reference field. We use the ROUGE metric to calculate the similarity between the two responses.
If no evaluation criteria are provided, the following default configuration is used:

tool_trajectory_avg_score: Defaults to 1.0, requiring a 100% match in the tool usage trajectory.
response_match_score: Defaults to 0.8, allowing for a small margin of error in the agent's natural language responses.
Here is an example of a test_config.json file specifying custom evaluation criteria:


{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  }
}
How to run Evaluation with the ADK
As a developer, you can evaluate your agents using the ADK in the following ways:

Web-based UI (adk web): Evaluate agents interactively through a web-based interface.
Programmatically (pytest): Integrate evaluation into your testing pipeline using pytest and test files.
Command Line Interface (adk eval): Run evaluations on an existing evaluation set file directly from the command line.
1. adk web - Run Evaluations via the Web UI
The web UI provides an interactive way to evaluate agents and generate evaluation datasets.

Steps to run evaluation via the web ui:

Start the web server by running: bash adk web samples_for_testing
In the web interface:
Select an agent (e.g., hello_world).
Interact with the agent to create a session that you want to save as a test case.
Click the “Eval tab” on the right side of the interface.
If you already have an existing eval set, select that or create a new one by clicking on "Create new eval set" button. Give your eval set a contextual name. Select the newly created evaluation set.
Click "Add current session" to save the current session as an eval in the eval set file. You will be asked to provide a name for this eval, again give it a contextual name.
Once created, the newly created eval will show up in the list of available evals in the eval set file. You can run all or select specific ones to run the eval.
The status of each eval will be shown in the UI.
2. pytest - Run Tests Programmatically
You can also use pytest to run test files as part of your integration tests.

Example Command

pytest tests/integration/
Example Test Code
Here is an example of a pytest test case that runs a single test file:


def test_with_single_test_file():
    """Test the agent's basic ability via a session file."""
    AgentEvaluator.evaluate(
        agent_module="tests.integration.fixture.home_automation_agent",
        eval_dataset="tests/integration/fixture/home_automation_agent/simple_test.test.json",
    )
This approach allows you to integrate agent evaluations into your CI/CD pipelines or larger test suites. If you want to specify the initial session state for your tests, you can do that by storing the session details in a file and passing that to AgentEvaluator.evaluate method.

Here is a sample session json file:


{
  "id": "test_id",
  "app_name": "trip_planner_agent",
  "user_id": "test_user",
  "state": {
    "origin": "San Francisco",
    "interests": "Moutains, Hikes",
    "range": "1000 miles",
    "cities": ""


  },
  "events": [],
  "last_update_time": 1741218714.258285
}
And the sample code will look like this:


def test_with_single_test_file():
    """Test the agent's basic ability via a session file."""
    AgentEvaluator.evaluate(
        agent_module="tests.integration.fixture.trip_planner_agent",
        eval_dataset="tests/integration/fixture/trip_planner_agent/simple_test.test.json",
        initial_session_file="tests/integration/fixture/trip_planner_agent/initial.session.json"
    )
3. adk eval - Run Evaluations via the cli
You can also run evaluation of an eval set file through the command line interface (CLI). This runs the same evaluation that runs on the UI, but it helps with automation, i.e. you can add this command as a part of your regular build generation and verification process.

Here is the command:


adk eval \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_FILE_PATH> \
    [--config_file_path=<PATH_TO_TEST_JSON_CONFIG_FILE>] \
    [--print_detailed_results]
For example:


adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
Here are the details for each command line argument:

AGENT_MODULE_FILE_PATH: The path to the init.py file that contains a module by the name "agent". "agent" module contains a root_agent.
EVAL_SET_FILE_PATH: The path to evaluations file(s). You can specify one or more eval set file paths. For each file, all evals will be run by default. If you want to run only specific evals from a eval set, first create a comma separated list of eval names and then add that as a suffix to the eval set file name, demarcated by a colon : .
For example: sample_eval_set_file.json:eval_1,eval_2,eval_3
This will only run eval_1, eval_2 and eval_3 from sample_eval_set_file.json
CONFIG_FILE_PATH: The path to the config file.
PRINT_DETAILED_RESULTS: Prints detailed results on the console.

# Context

Context
What are Context
In the Agent Development Kit (ADK), "context" refers to the crucial bundle of information available to your agent and its tools during specific operations. Think of it as the necessary background knowledge and resources needed to handle a current task or conversation turn effectively.

Agents often need more than just the latest user message to perform well. Context is essential because it enables:

Maintaining State: Remembering details across multiple steps in a conversation (e.g., user preferences, previous calculations, items in a shopping cart). This is primarily managed through session state.
Passing Data: Sharing information discovered or generated in one step (like an LLM call or a tool execution) with subsequent steps. Session state is key here too.
Accessing Services: Interacting with framework capabilities like:
Artifact Storage: Saving or loading files or data blobs (like PDFs, images, configuration files) associated with the session.
Memory: Searching for relevant information from past interactions or external knowledge sources connected to the user.
Authentication: Requesting and retrieving credentials needed by tools to access external APIs securely.
Identity and Tracking: Knowing which agent is currently running (agent.name) and uniquely identifying the current request-response cycle (invocation_id) for logging and debugging.
Tool-Specific Actions: Enabling specialized operations within tools, such as requesting authentication or searching memory, which require access to the current interaction's details.
The central piece holding all this information together for a single, complete user-request-to-final-response cycle (an invocation) is the InvocationContext. However, you typically won't create or manage this object directly. The ADK framework creates it when an invocation starts (e.g., via runner.run_async) and passes the relevant contextual information implicitly to your agent code, callbacks, and tools.


# Conceptual Pseudocode: How the framework provides context (Internal Logic)

# runner = Runner(agent=my_root_agent, session_service=..., artifact_service=...)
# user_message = types.Content(...)
# session = session_service.get_session(...) # Or create new

# --- Inside runner.run_async(...) ---
# 1. Framework creates the main context for this specific run
# invocation_context = InvocationContext(
#     invocation_id="unique-id-for-this-run",
#     session=session,
#     user_content=user_message,
#     agent=my_root_agent, # The starting agent
#     session_service=session_service,
#     artifact_service=artifact_service,
#     memory_service=memory_service,
#     # ... other necessary fields ...
# )

# 2. Framework calls the agent's run method, passing the context implicitly
#    (The agent's method signature will receive it, e.g., _run_async_impl(self, ctx: InvocationContext))
# await my_root_agent.run_async(invocation_context)
# --- End Internal Logic ---

# As a developer, you work with the context objects provided in method arguments.
The Different types of Context
While InvocationContext acts as the comprehensive internal container, ADK provides specialized context objects tailored to specific situations. This ensures you have the right tools and permissions for the task at hand without needing to handle the full complexity of the internal context everywhere. Here are the different "flavors" you'll encounter:

InvocationContext

Where Used: Received as the ctx argument directly within an agent's core implementation methods (_run_async_impl, _run_live_impl).
Purpose: Provides access to the entire state of the current invocation. This is the most comprehensive context object.
Key Contents: Direct access to session (including state and events), the current agent instance, invocation_id, initial user_content, references to configured services (artifact_service, memory_service, session_service), and fields related to live/streaming modes.
Use Case: Primarily used when the agent's core logic needs direct access to the overall session or services, though often state and artifact interactions are delegated to callbacks/tools which use their own contexts. Also used to control the invocation itself (e.g., setting ctx.end_invocation = True).

# Pseudocode: Agent implementation receiving InvocationContext
from google.adk.agents import BaseAgent, InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator

class MyAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Direct access example
        agent_name = ctx.agent.name
        session_id = ctx.session.id
        print(f"Agent {agent_name} running in session {session_id} for invocation {ctx.invocation_id}")
        # ... agent logic using ctx ...
        yield # ... event ...
ReadonlyContext

Where Used: Provided in scenarios where only read access to basic information is needed and mutation is disallowed (e.g., InstructionProvider functions). It's also the base class for other contexts.
Purpose: Offers a safe, read-only view of fundamental contextual details.
Key Contents: invocation_id, agent_name, and a read-only view of the current state.

# Pseudocode: Instruction provider receiving ReadonlyContext
from google.adk.agents import ReadonlyContext

def my_instruction_provider(context: ReadonlyContext) -> str:
    # Read-only access example
    user_tier = context.state.get("user_tier", "standard") # Can read state
    # context.state['new_key'] = 'value' # This would typically cause an error or be ineffective
    return f"Process the request for a {user_tier} user."
CallbackContext

Where Used: Passed as callback_context to agent lifecycle callbacks (before_agent_callback, after_agent_callback) and model interaction callbacks (before_model_callback, after_model_callback).
Purpose: Facilitates inspecting and modifying state, interacting with artifacts, and accessing invocation details specifically within callbacks.
Key Capabilities (Adds to ReadonlyContext):
Mutable state Property: Allows reading and writing to session state. Changes made here (callback_context.state['key'] = value) are tracked and associated with the event generated by the framework after the callback.
Artifact Methods: load_artifact(filename) and save_artifact(filename, part) methods for interacting with the configured artifact_service.
Direct user_content access.

# Pseudocode: Callback receiving CallbackContext
from google.adk.agents import CallbackContext
from google.adk.models import LlmRequest
from google.genai import types
from typing import Optional

def my_before_model_cb(callback_context: CallbackContext, request: LlmRequest) -> Optional[types.Content]:
    # Read/Write state example
    call_count = callback_context.state.get("model_calls", 0)
    callback_context.state["model_calls"] = call_count + 1 # Modify state

    # Optionally load an artifact
    # config_part = callback_context.load_artifact("model_config.json")
    print(f"Preparing model call #{call_count + 1} for invocation {callback_context.invocation_id}")
    return None # Allow model call to proceed
ToolContext

Where Used: Passed as tool_context to the functions backing FunctionTools and to tool execution callbacks (before_tool_callback, after_tool_callback).
Purpose: Provides everything CallbackContext does, plus specialized methods essential for tool execution, like handling authentication, searching memory, and listing artifacts.
Key Capabilities (Adds to CallbackContext):
Authentication Methods: request_credential(auth_config) to trigger an auth flow, and get_auth_response(auth_config) to retrieve credentials provided by the user/system.
Artifact Listing: list_artifacts() to discover available artifacts in the session.
Memory Search: search_memory(query) to query the configured memory_service.
function_call_id Property: Identifies the specific function call from the LLM that triggered this tool execution, crucial for linking authentication requests or responses back correctly.
actions Property: Direct access to the EventActions object for this step, allowing the tool to signal state changes, auth requests, etc.

# Pseudocode: Tool function receiving ToolContext
from google.adk.agents import ToolContext
from typing import Dict, Any

# Assume this function is wrapped by a FunctionTool
def search_external_api(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    api_key = tool_context.state.get("api_key")
    if not api_key:
        # Define required auth config
        # auth_config = AuthConfig(...)
        # tool_context.request_credential(auth_config) # Request credentials
        # Use the 'actions' property to signal the auth request has been made
        # tool_context.actions.requested_auth_configs[tool_context.function_call_id] = auth_config
        return {"status": "Auth Required"}

    # Use the API key...
    print(f"Tool executing for query '{query}' using API key. Invocation: {tool_context.invocation_id}")

    # Optionally search memory or list artifacts
    # relevant_docs = tool_context.search_memory(f"info related to {query}")
    # available_files = tool_context.list_artifacts()

    return {"result": f"Data for {query} fetched."}
Understanding these different context objects and when to use them is key to effectively managing state, accessing services, and controlling the flow of your ADK application. The next section will detail common tasks you can perform using these contexts.

Common Tasks Using Context
Now that you understand the different context objects, let's focus on how to use them for common tasks when building your agents and tools.

Accessing Information
You'll frequently need to read information stored within the context.

Reading Session State: Access data saved in previous steps or user/app-level settings. Use dictionary-like access on the state property.


# Pseudocode: In a Tool function
from google.adk.agents import ToolContext

def my_tool(tool_context: ToolContext, **kwargs):
    user_pref = tool_context.state.get("user_display_preference", "default_mode")
    api_endpoint = tool_context.state.get("app:api_endpoint") # Read app-level state

    if user_pref == "dark_mode":
        # ... apply dark mode logic ...
        pass
    print(f"Using API endpoint: {api_endpoint}")
    # ... rest of tool logic ...

# Pseudocode: In a Callback function
from google.adk.agents import CallbackContext

def my_callback(callback_context: CallbackContext, **kwargs):
    last_tool_result = callback_context.state.get("temp:last_api_result") # Read temporary state
    if last_tool_result:
        print(f"Found temporary result from last tool: {last_tool_result}")
    # ... callback logic ...
Getting Current Identifiers: Useful for logging or custom logic based on the current operation.


# Pseudocode: In any context (ToolContext shown)
from google.adk.agents import ToolContext

def log_tool_usage(tool_context: ToolContext, **kwargs):
    agent_name = tool_context.agent_name
    inv_id = tool_context.invocation_id
    func_call_id = getattr(tool_context, 'function_call_id', 'N/A') # Specific to ToolContext

    print(f"Log: Invocation={inv_id}, Agent={agent_name}, FunctionCallID={func_call_id} - Tool Executed.")
Accessing the Initial User Input: Refer back to the message that started the current invocation.


# Pseudocode: In a Callback
from google.adk.agents import CallbackContext

def check_initial_intent(callback_context: CallbackContext, **kwargs):
    initial_text = "N/A"
    if callback_context.user_content and callback_context.user_content.parts:
        initial_text = callback_context.user_content.parts[0].text or "Non-text input"

    print(f"This invocation started with user input: '{initial_text}'")

# Pseudocode: In an Agent's _run_async_impl
# async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
#     if ctx.user_content and ctx.user_content.parts:
#         initial_text = ctx.user_content.parts[0].text
#         print(f"Agent logic remembering initial query: {initial_text}")
#     ...
Managing Session State
State is crucial for memory and data flow. When you modify state using CallbackContext or ToolContext, the changes are automatically tracked and persisted by the framework.

How it Works: Writing to callback_context.state['my_key'] = my_value or tool_context.state['my_key'] = my_value adds this change to the EventActions.state_delta associated with the current step's event. The SessionService then applies these deltas when persisting the event.
Passing Data Between Tools:


# Pseudocode: Tool 1 - Fetches user ID
from google.adk.agents import ToolContext
import uuid

def get_user_profile(tool_context: ToolContext) -> dict:
    user_id = str(uuid.uuid4()) # Simulate fetching ID
    # Save the ID to state for the next tool
    tool_context.state["temp:current_user_id"] = user_id
    return {"profile_status": "ID generated"}

# Pseudocode: Tool 2 - Uses user ID from state
def get_user_orders(tool_context: ToolContext) -> dict:
    user_id = tool_context.state.get("temp:current_user_id")
    if not user_id:
        return {"error": "User ID not found in state"}

    print(f"Fetching orders for user ID: {user_id}")
    # ... logic to fetch orders using user_id ...
    return {"orders": ["order123", "order456"]}
Updating User Preferences:


# Pseudocode: Tool or Callback identifies a preference
from google.adk.agents import ToolContext # Or CallbackContext

def set_user_preference(tool_context: ToolContext, preference: str, value: str) -> dict:
    # Use 'user:' prefix for user-level state (if using a persistent SessionService)
    state_key = f"user:{preference}"
    tool_context.state[state_key] = value
    print(f"Set user preference '{preference}' to '{value}'")
    return {"status": "Preference updated"}
State Prefixes: While basic state is session-specific, prefixes like app: and user: can be used with persistent SessionService implementations (like DatabaseSessionService or VertexAiSessionService) to indicate broader scope (app-wide or user-wide across sessions). temp: can denote data only relevant within the current invocation.

Working with Artifacts
Use artifacts to handle files or large data blobs associated with the session. Common use case: processing uploaded documents.

Document Summarizer Example Flow:

Ingest Reference (e.g., in a Setup Tool or Callback): Save the path or URI of the document, not the entire content, as an artifact.


# Pseudocode: In a callback or initial tool
from google.adk.agents import CallbackContext # Or ToolContext
from google.genai import types

def save_document_reference(context: CallbackContext, file_path: str) -> None:
    # Assume file_path is something like "gs://my-bucket/docs/report.pdf" or "/local/path/to/report.pdf"
    try:
        # Create a Part containing the path/URI text
        artifact_part = types.Part(text=file_path)
        version = context.save_artifact("document_to_summarize.txt", artifact_part)
        print(f"Saved document reference '{file_path}' as artifact version {version}")
        # Store the filename in state if needed by other tools
        context.state["temp:doc_artifact_name"] = "document_to_summarize.txt"
    except ValueError as e:
        print(f"Error saving artifact: {e}") # E.g., Artifact service not configured
    except Exception as e:
        print(f"Unexpected error saving artifact reference: {e}")

# Example usage:
# save_document_reference(callback_context, "gs://my-bucket/docs/report.pdf")
Summarizer Tool: Load the artifact to get the path/URI, read the actual document content using appropriate libraries, summarize, and return the result.


# Pseudocode: In the Summarizer tool function
from google.adk.agents import ToolContext
from google.genai import types
# Assume libraries like google.cloud.storage or built-in open are available
# Assume a 'summarize_text' function exists
# from my_summarizer_lib import summarize_text

def summarize_document_tool(tool_context: ToolContext) -> dict:
    artifact_name = tool_context.state.get("temp:doc_artifact_name")
    if not artifact_name:
        return {"error": "Document artifact name not found in state."}

    try:
        # 1. Load the artifact part containing the path/URI
        artifact_part = tool_context.load_artifact(artifact_name)
        if not artifact_part or not artifact_part.text:
            return {"error": f"Could not load artifact or artifact has no text path: {artifact_name}"}

        file_path = artifact_part.text
        print(f"Loaded document reference: {file_path}")

        # 2. Read the actual document content (outside ADK context)
        document_content = ""
        if file_path.startswith("gs://"):
            # Example: Use GCS client library to download/read
            # from google.cloud import storage
            # client = storage.Client()
            # blob = storage.Blob.from_string(file_path, client=client)
            # document_content = blob.download_as_text() # Or bytes depending on format
            pass # Replace with actual GCS reading logic
        elif file_path.startswith("/"):
             # Example: Use local file system
             with open(file_path, 'r', encoding='utf-8') as f:
                 document_content = f.read()
        else:
            return {"error": f"Unsupported file path scheme: {file_path}"}

        # 3. Summarize the content
        if not document_content:
             return {"error": "Failed to read document content."}

        # summary = summarize_text(document_content) # Call your summarization logic
        summary = f"Summary of content from {file_path}" # Placeholder

        return {"summary": summary}

    except ValueError as e:
         return {"error": f"Artifact service error: {e}"}
    except FileNotFoundError:
         return {"error": f"Local file not found: {file_path}"}
    # except Exception as e: # Catch specific exceptions for GCS etc.
    #      return {"error": f"Error reading document {file_path}: {e}"}
Listing Artifacts: Discover what files are available.


# Pseudocode: In a tool function
from google.adk.agents import ToolContext

def check_available_docs(tool_context: ToolContext) -> dict:
    try:
        artifact_keys = tool_context.list_artifacts()
        print(f"Available artifacts: {artifact_keys}")
        return {"available_docs": artifact_keys}
    except ValueError as e:
        return {"error": f"Artifact service error: {e}"}
Handling Tool Authentication
Securely manage API keys or other credentials needed by tools.


# Pseudocode: Tool requiring auth
from google.adk.agents import ToolContext
from google.adk.auth import AuthConfig # Assume appropriate AuthConfig is defined

# Define your required auth configuration (e.g., OAuth, API Key)
MY_API_AUTH_CONFIG = AuthConfig(...)
AUTH_STATE_KEY = "user:my_api_credential" # Key to store retrieved credential

def call_secure_api(tool_context: ToolContext, request_data: str) -> dict:
    # 1. Check if credential already exists in state
    credential = tool_context.state.get(AUTH_STATE_KEY)

    if not credential:
        # 2. If not, request it
        print("Credential not found, requesting...")
        try:
            tool_context.request_credential(MY_API_AUTH_CONFIG)
            # The framework handles yielding the event. The tool execution stops here for this turn.
            return {"status": "Authentication required. Please provide credentials."}
        except ValueError as e:
            return {"error": f"Auth error: {e}"} # e.g., function_call_id missing
        except Exception as e:
            return {"error": f"Failed to request credential: {e}"}

    # 3. If credential exists (might be from a previous turn after request)
    #    or if this is a subsequent call after auth flow completed externally
    try:
        # Optionally, re-validate/retrieve if needed, or use directly
        # This might retrieve the credential if the external flow just completed
        auth_credential_obj = tool_context.get_auth_response(MY_API_AUTH_CONFIG)
        api_key = auth_credential_obj.api_key # Or access_token, etc.

        # Store it back in state for future calls within the session
        tool_context.state[AUTH_STATE_KEY] = auth_credential_obj.model_dump() # Persist retrieved credential

        print(f"Using retrieved credential to call API with data: {request_data}")
        # ... Make the actual API call using api_key ...
        api_result = f"API result for {request_data}"

        return {"result": api_result}
    except Exception as e:
        # Handle errors retrieving/using the credential
        print(f"Error using credential: {e}")
        # Maybe clear the state key if credential is invalid?
        # tool_context.state[AUTH_STATE_KEY] = None
        return {"error": "Failed to use credential"}
Remember: request_credential pauses the tool and signals the need for authentication. The user/system provides credentials, and on a subsequent call, get_auth_response (or checking state again) allows the tool to proceed. The tool_context.function_call_id is used implicitly by the framework to link the request and response.
Leveraging Memory
Access relevant information from the past or external sources.


# Pseudocode: Tool using memory search
from google.adk.agents import ToolContext

def find_related_info(tool_context: ToolContext, topic: str) -> dict:
    try:
        search_results = tool_context.search_memory(f"Information about {topic}")
        if search_results.results:
            print(f"Found {len(search_results.results)} memory results for '{topic}'")
            # Process search_results.results (which are SearchMemoryResponseEntry)
            top_result_text = search_results.results[0].text
            return {"memory_snippet": top_result_text}
        else:
            return {"message": "No relevant memories found."}
    except ValueError as e:
        return {"error": f"Memory service error: {e}"} # e.g., Service not configured
    except Exception as e:
        return {"error": f"Unexpected error searching memory: {e}"}
Advanced: Direct InvocationContext Usage
While most interactions happen via CallbackContext or ToolContext, sometimes the agent's core logic (_run_async_impl/_run_live_impl) needs direct access.


# Pseudocode: Inside agent's _run_async_impl
from google.adk.agents import InvocationContext, BaseAgent
from google.adk.events import Event
from typing import AsyncGenerator

class MyControllingAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Example: Check if a specific service is available
        if not ctx.memory_service:
            print("Memory service is not available for this invocation.")
            # Potentially change agent behavior

        # Example: Early termination based on some condition
        if ctx.session.state.get("critical_error_flag"):
            print("Critical error detected, ending invocation.")
            ctx.end_invocation = True # Signal framework to stop processing
            yield Event(author=self.name, invocation_id=ctx.invocation_id, content="Stopping due to critical error.")
            return # Stop this agent's execution

        # ... Normal agent processing ...
        yield # ... event ...
Setting ctx.end_invocation = True is a way to gracefully stop the entire request-response cycle from within the agent or its callbacks/tools (via their respective context objects which also have access to modify the underlying InvocationContext's flag).

Key Takeaways & Best Practices
Use the Right Context: Always use the most specific context object provided (ToolContext in tools/tool-callbacks, CallbackContext in agent/model-callbacks, ReadonlyContext where applicable). Use the full InvocationContext (ctx) directly in _run_async_impl / _run_live_impl only when necessary.
State for Data Flow: context.state is the primary way to share data, remember preferences, and manage conversational memory within an invocation. Use prefixes (app:, user:, temp:) thoughtfully when using persistent storage.
Artifacts for Files: Use context.save_artifact and context.load_artifact for managing file references (like paths or URIs) or larger data blobs. Store references, load content on demand.
Tracked Changes: Modifications to state or artifacts made via context methods are automatically linked to the current step's EventActions and handled by the SessionService.
Start Simple: Focus on state and basic artifact usage first. Explore authentication, memory, and advanced InvocationContext fields (like those for live streaming) as your needs become more complex.
By understanding and effectively using these context objects, you can build more sophisticated, stateful, and capable agents with ADK.

# API Reference

Submodules
google.adk.agents module
Agent
BaseAgent
BaseAgent.after_agent_callback
BaseAgent.before_agent_callback
BaseAgent.description
BaseAgent.name
BaseAgent.parent_agent
BaseAgent.sub_agents
BaseAgent.find_agent()
BaseAgent.find_sub_agent()
BaseAgent.model_post_init()
BaseAgent.run_async()
BaseAgent.run_live()
BaseAgent.root_agent
LlmAgent
LlmAgent.after_model_callback
LlmAgent.after_tool_callback
LlmAgent.before_model_callback
LlmAgent.before_tool_callback
LlmAgent.code_executor
LlmAgent.disallow_transfer_to_parent
LlmAgent.disallow_transfer_to_peers
LlmAgent.examples
LlmAgent.generate_content_config
LlmAgent.global_instruction
LlmAgent.include_contents
LlmAgent.input_schema
LlmAgent.instruction
LlmAgent.model
LlmAgent.output_key
LlmAgent.output_schema
LlmAgent.planner
LlmAgent.tools
LlmAgent.canonical_global_instruction()
LlmAgent.canonical_instruction()
LlmAgent.canonical_model
LlmAgent.canonical_tools
LoopAgent
LoopAgent.max_iterations
ParallelAgent
SequentialAgent
google.adk.artifacts module
BaseArtifactService
BaseArtifactService.delete_artifact()
BaseArtifactService.list_artifact_keys()
BaseArtifactService.list_versions()
BaseArtifactService.load_artifact()
BaseArtifactService.save_artifact()
GcsArtifactService
GcsArtifactService.delete_artifact()
GcsArtifactService.list_artifact_keys()
GcsArtifactService.list_versions()
GcsArtifactService.load_artifact()
GcsArtifactService.save_artifact()
InMemoryArtifactService
InMemoryArtifactService.artifacts
InMemoryArtifactService.delete_artifact()
InMemoryArtifactService.list_artifact_keys()
InMemoryArtifactService.list_versions()
InMemoryArtifactService.load_artifact()
InMemoryArtifactService.save_artifact()
google.adk.code_executors module
BaseCodeExecutor
BaseCodeExecutor.optimize_data_file
BaseCodeExecutor.stateful
BaseCodeExecutor.error_retry_attempts
BaseCodeExecutor.code_block_delimiters
BaseCodeExecutor.execution_result_delimiters
BaseCodeExecutor.code_block_delimiters
BaseCodeExecutor.error_retry_attempts
BaseCodeExecutor.execution_result_delimiters
BaseCodeExecutor.optimize_data_file
BaseCodeExecutor.stateful
BaseCodeExecutor.execute_code()
CodeExecutorContext
CodeExecutorContext.add_input_files()
CodeExecutorContext.add_processed_file_names()
CodeExecutorContext.clear_input_files()
CodeExecutorContext.get_error_count()
CodeExecutorContext.get_execution_id()
CodeExecutorContext.get_input_files()
CodeExecutorContext.get_processed_file_names()
CodeExecutorContext.get_state_delta()
CodeExecutorContext.increment_error_count()
CodeExecutorContext.reset_error_count()
CodeExecutorContext.set_execution_id()
CodeExecutorContext.update_code_execution_result()
ContainerCodeExecutor
ContainerCodeExecutor.base_url
ContainerCodeExecutor.image
ContainerCodeExecutor.docker_path
ContainerCodeExecutor.base_url
ContainerCodeExecutor.docker_path
ContainerCodeExecutor.image
ContainerCodeExecutor.optimize_data_file
ContainerCodeExecutor.stateful
ContainerCodeExecutor.execute_code()
ContainerCodeExecutor.model_post_init()
UnsafeLocalCodeExecutor
UnsafeLocalCodeExecutor.optimize_data_file
UnsafeLocalCodeExecutor.stateful
UnsafeLocalCodeExecutor.execute_code()
VertexAiCodeExecutor
VertexAiCodeExecutor.resource_name
VertexAiCodeExecutor.resource_name
VertexAiCodeExecutor.execute_code()
VertexAiCodeExecutor.model_post_init()
google.adk.evaluation module
AgentEvaluator
AgentEvaluator.evaluate()
AgentEvaluator.find_config_for_test_file()
google.adk.events module
Event
Event.invocation_id
Event.author
Event.actions
Event.long_running_tool_ids
Event.branch
Event.id
Event.timestamp
Event.is_final_response
Event.get_function_calls
Event.actions
Event.author
Event.branch
Event.id
Event.invocation_id
Event.long_running_tool_ids
Event.timestamp
Event.get_function_calls()
Event.get_function_responses()
Event.has_trailing_code_exeuction_result()
Event.is_final_response()
Event.model_post_init()
Event.new_id()
EventActions
EventActions.artifact_delta
EventActions.escalate
EventActions.requested_auth_configs
EventActions.skip_summarization
EventActions.state_delta
EventActions.transfer_to_agent
google.adk.examples module
BaseExampleProvider
BaseExampleProvider.get_examples()
Example
Example.input
Example.output
Example.input
Example.output
VertexAiExampleStore
VertexAiExampleStore.get_examples()
google.adk.memory module
BaseMemoryService
BaseMemoryService.add_session_to_memory()
BaseMemoryService.search_memory()
InMemoryMemoryService
InMemoryMemoryService.add_session_to_memory()
InMemoryMemoryService.search_memory()
InMemoryMemoryService.session_events
VertexAiRagMemoryService
VertexAiRagMemoryService.add_session_to_memory()
VertexAiRagMemoryService.search_memory()
google.adk.models module
BaseLlm
BaseLlm.model
BaseLlm.model_config
BaseLlm.model
BaseLlm.connect()
BaseLlm.generate_content_async()
BaseLlm.supported_models()
Gemini
Gemini.model
Gemini.model
Gemini.connect()
Gemini.generate_content_async()
Gemini.supported_models()
Gemini.api_client
LLMRegistry
LLMRegistry.new_llm()
LLMRegistry.register()
LLMRegistry.resolve()
google.adk.planners module
BasePlanner
BasePlanner.build_planning_instruction()
BasePlanner.process_planning_response()
BuiltInPlanner
BuiltInPlanner.thinking_config
BuiltInPlanner.apply_thinking_config()
BuiltInPlanner.build_planning_instruction()
BuiltInPlanner.process_planning_response()
BuiltInPlanner.thinking_config
PlanReActPlanner
PlanReActPlanner.build_planning_instruction()
PlanReActPlanner.process_planning_response()
google.adk.runners module
InMemoryRunner
InMemoryRunner.agent
InMemoryRunner.app_name
Runner
Runner.app_name
Runner.agent
Runner.artifact_service
Runner.session_service
Runner.memory_service
Runner.agent
Runner.app_name
Runner.artifact_service
Runner.close_session()
Runner.memory_service
Runner.run()
Runner.run_async()
Runner.run_live()
Runner.session_service
google.adk.sessions module
BaseSessionService
BaseSessionService.append_event()
BaseSessionService.close_session()
BaseSessionService.create_session()
BaseSessionService.delete_session()
BaseSessionService.get_session()
BaseSessionService.list_events()
BaseSessionService.list_sessions()
DatabaseSessionService
DatabaseSessionService.append_event()
DatabaseSessionService.create_session()
DatabaseSessionService.delete_session()
DatabaseSessionService.get_session()
DatabaseSessionService.list_events()
DatabaseSessionService.list_sessions()
InMemorySessionService
InMemorySessionService.append_event()
InMemorySessionService.create_session()
InMemorySessionService.delete_session()
InMemorySessionService.get_session()
InMemorySessionService.list_events()
InMemorySessionService.list_sessions()
Session
Session.id
Session.app_name
Session.user_id
Session.state
Session.events
Session.last_update_time
Session.app_name
Session.events
Session.id
Session.last_update_time
Session.state
Session.user_id
State
State.APP_PREFIX
State.TEMP_PREFIX
State.USER_PREFIX
State.get()
State.has_delta()
State.to_dict()
State.update()
VertexAiSessionService
VertexAiSessionService.append_event()
VertexAiSessionService.create_session()
VertexAiSessionService.delete_session()
VertexAiSessionService.get_session()
VertexAiSessionService.list_events()
VertexAiSessionService.list_sessions()
google.adk.tools module
APIHubToolset
APIHubToolset.get_tool()
APIHubToolset.get_tools()
AuthToolArguments
AuthToolArguments.auth_config
AuthToolArguments.function_call_id
BaseTool
BaseTool.description
BaseTool.is_long_running
BaseTool.name
BaseTool.process_llm_request()
BaseTool.run_async()
ExampleTool
ExampleTool.examples
ExampleTool.process_llm_request()
FunctionTool
FunctionTool.func
FunctionTool.run_async()
LongRunningFunctionTool
LongRunningFunctionTool.is_long_running
ToolContext
ToolContext.invocation_context
ToolContext.function_call_id
ToolContext.event_actions
ToolContext.actions
ToolContext.get_auth_response()
ToolContext.list_artifacts()
ToolContext.request_credential()
ToolContext.search_memory()
VertexAiSearchTool
VertexAiSearchTool.data_store_id
VertexAiSearchTool.search_engine_id
VertexAiSearchTool.process_llm_request()
exit_loop()
transfer_to_agent()

