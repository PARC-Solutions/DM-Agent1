# Quickstart (Streaming)

This quickstart builds on the standard quickstart, showing you how to implement streaming responses from your agent, which provides a more engaging and interactive user experience.

## Prerequisites

- Completion of the [standard quickstart](./2_Quickstart.md)
- Python 3.9+
- API key from [Google AI Studio](https://ai.google.dev/) (or Vertex AI credentials)

## 1. Set up Environment & Create Project Structure

Start by setting up a new project directory:

```bash
mkdir streaming_agent
cd streaming_agent
```

Create the necessary files:

```bash
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

## 2. Implement the Streaming Agent

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

## 3. Run the Streaming Agent

Execute your streaming agent with:

```bash
python -m streaming_agent.agent
```

This will start a local server, typically at http://localhost:8080, where you can interact with your streaming agent through a web interface.

## 4. Observe the Streaming Behavior

When interacting with your agent, you'll notice:

- Responses appear incrementally, word by word, providing a more conversational feel
- The streaming happens automatically when `enable_streaming=True` is set
- The client interface (terminal or browser) shows responses as they're generated

## Benefits of Streaming

Streaming capabilities provide several advantages:

- **Improved User Experience**: Users don't have to wait for the entire response to be generated before seeing any output.
- **More Natural Interaction**: Word-by-word appearance mimics human conversation patterns.
- **Faster Perceived Response Time**: Even though the total generation time is similar, users perceive the interaction as faster because they see partial results immediately.
- **Better for Long Responses**: Especially valuable when the agent generates longer, detailed explanations.

## 5. Adding Streaming to the Multi-Tool Agent

To enable streaming on the multi-tool agent from the previous quickstart, simply add the `enable_streaming=True` parameter:

```python
root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
    enable_streaming=True  # Enable streaming responses
)
```

## Next Steps

- Follow the [Tutorial](./4_Tutorial.md) to build a more sophisticated multi-agent system
- Learn more about [Agents](../2_CoreConcepts/1_Agents.md) and [Tools](../2_CoreConcepts/2_Tools.md)
- Explore [Callbacks](../5_Advanced/1_Callbacks.md) for more advanced control over agent execution
