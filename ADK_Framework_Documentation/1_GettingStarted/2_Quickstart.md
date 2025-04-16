# Quickstart

This quickstart guides you through setting up a basic agent with multiple tools and running it locally either in the terminal or in the interactive, browser-based dev UI.

## Prerequisites

- Python 3.9+
- A local IDE (VS Code, PyCharm, etc.) with terminal access
- API key from [Google AI Studio](https://ai.google.dev/) (or Vertex AI credentials)

## 1. Create Agent Project

### Project Structure

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

### __init__.py

Create an `__init__.py` file:

```bash
echo "from . import agent" > multi_tool_agent/__init__.py
```

Your `__init__.py` should contain:

```python
from . import agent
```

### agent.py

Create an `agent.py` file with the following code:

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

### .env

Create a `.env` file with your API credentials:

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_ACTUAL_API_KEY_HERE
```

Replace `GOOGLE_API_KEY` with your actual API key.

## 2. Running Your Agent

### Command Line Interface

To run your agent from the command line:

```bash
python -m google.adk.cli run --agent multi_tool_agent.agent.root_agent
```

### Development Server (Web UI)

You can also run your agent with a browser-based UI. Add this to the bottom of your `agent.py` file:

```python
from google.adk.server import run_local_server

if __name__ == "__main__":
    run_local_server(root_agent)
```

Then run:

```bash
python -m multi_tool_agent.agent
```

This will start a local server (typically at http://localhost:8080) where you can interact with your agent through a web interface.

## 3. Testing Your Agent

Try these sample queries:

- "What's the weather in New York?"
- "What time is it in New York?"
- "What's the weather and time in New York?"

Your agent should respond with the appropriate information using the tools you provided.

## Next Steps

- Try the [Streaming Quickstart](./3_QuickstartStreaming.md) to enable word-by-word streaming responses
- Follow the [Tutorial](./4_Tutorial.md) to build a more sophisticated multi-agent system
- Learn more about [Agents](../2_CoreConcepts/1_Agents.md) and [Tools](../2_CoreConcepts/2_Tools.md)
