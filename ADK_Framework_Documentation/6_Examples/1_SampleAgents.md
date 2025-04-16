# Sample Agents

The ADK repository includes several sample agents that demonstrate different capabilities and use cases. Exploring these examples is a great way to understand how to build your own agents with specific features.

## Basic Samples

### Echo Agent

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

### Weather Agent

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

## Advanced Samples

### Multimodal Agent

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

### RAG (Retrieval-Augmented Generation) Agent

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

## How to Run the Samples

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

## Learning from Samples

When exploring these samples, pay attention to:

1. **Agent Configuration**: How different parameters affect agent behavior
2. **Tool Integration**: How tools are defined and used by agents
3. **Prompt Engineering**: How instructions shape the agent's responses
4. **Error Handling**: How the samples handle edge cases and errors

The sample code is designed to be readable and educational, serving as a reference for your own agent development.
