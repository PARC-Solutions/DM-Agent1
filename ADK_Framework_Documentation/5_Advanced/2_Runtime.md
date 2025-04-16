# Runtime

## What is Runtime?

The ADK Runtime is the underlying engine that powers your agent application during user interactions. It's the system that takes your defined agents, tools, and callbacks and orchestrates their execution in response to user input, managing the flow of information, state changes, and interactions with external services like LLMs or storage.

Think of the Runtime as the "engine" of your agentic application. You define the parts (agents, tools), and the Runtime handles how they connect and run together to fulfill a user's request.

## Core Concept: The Event Loop

At its heart, the ADK Runtime operates on an Event Loop. This loop facilitates a back-and-forth communication between the `Runner` component and your defined "Execution Logic" (which includes your Agents, the LLM calls they make, Callbacks, and Tools).

### In Simple Terms

1. The `Runner` receives a user query and asks the main `Agent` to start processing.
2. The `Agent` (and its associated logic) runs until it has something to report (like a response, a request to use a tool, or a state change) – it then `yields` an `Event`.
3. The `Runner` receives this `Event`, processes any associated actions (like saving state changes via `Services`), and forwards the event onwards (e.g., to the user interface).
4. Only `after` the `Runner` has processed the event does the `Agent`'s logic `resume` from where it paused, now potentially seeing the effects of the changes committed by the Runner.
5. This cycle repeats until the agent has no more events to yield for the current user query.

## The Event Loop: Inner Workings

The Event Loop is the core operational pattern defining the interaction between the `Runner` and your custom code (Agents, Tools, Callbacks). It establishes a clear division of responsibilities:

### Runner's Role (Orchestrator)

The `Runner` acts as the central coordinator for a single user invocation. Its responsibilities in the loop are:

1. **Initiation**: Receives the end user's query (`new_message`) and typically appends it to the session history via the `SessionService`.
2. **Kick-off**: Starts the event generation process by calling the main agent's execution method (e.g., `agent_to_run.run_async(...)`).
3. **Receive & Process**: Waits for the agent logic to `yield` an `Event`. Upon receiving an event, the Runner promptly processes it. This involves:
   * Using configured `Services` (`SessionService`, `ArtifactService`, `MemoryService`) to commit changes indicated in `event.actions` (like `state_delta`, `artifact_delta`).
   * Forwarding relevant information to external systems (like user interfaces or API clients).

### Agent's Role (Logic Provider)

Your `Agent` code (and the tools and callbacks it uses) serves as the "brains" of the operation:

1. **Generate Events**: Performs its logic, making decisions, and `yields` `Events` whenever it needs to report something or cause a state change.
2. **Wait for Processing**: After yielding an event, the agent's execution is paused until the Runner processes the event.
3. **Resume with Updated State**: When execution resumes, any state changes that the Runner committed during event processing are now visible to the agent.

### Event Flow Diagram

```
┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
│   User      │                 │   Runner    │                 │ Agent Logic │
│             │                 │             │                 │             │
└─────┬───────┘                 └─────┬───────┘                 └─────┬───────┘
      │                               │                               │
      │  1. Send Message              │                               │
      │ ───────────────────────────► │                               │
      │                               │  2. Start Agent Processing    │
      │                               │ ───────────────────────────► │
      │                               │                               │
      │                               │                               │  3. Process
      │                               │                               │     and Yield
      │                               │  4. Event (e.g., LLM Request) │     Event
      │                               │ ◄─────────────────────────── │
      │                               │                               │
      │                               │  5. Process Event             │
      │                               │     (e.g., call LLM)          │
      │                               │                               │
      │                               │  6. Resume Processing         │
      │                               │     with Event Result         │
      │                               │ ───────────────────────────► │
      │                               │                               │
      │                               │                               │  7. Process
      │                               │                               │     and Yield
      │                               │  8. Event (e.g., Final        │     Event
      │                               │     Response)                 │
      │                               │ ◄─────────────────────────── │
      │                               │                               │
      │  9. Deliver Response          │                               │
      │ ◄─────────────────────────── │                               │
      │                               │                               │
┌─────┴───────┐                 ┌─────┴───────┐                 ┌─────┴───────┐
│   User      │                 │   Runner    │                 │ Agent Logic │
│             │                 │             │                 │             │
└─────────────┘                 └─────────────┘                 └─────────────┘
```

## Events in ADK

Events are the communication mechanism between your agent logic and the runner. They signal state changes, requests, and responses. Key event types include:

### 1. ModelRequest Event

Generated when the agent needs to query the LLM.

```python
from google.adk.runtime.events import ModelRequestEvent

# Inside an agent's logic
model_request = LlmRequest(prompt="What's the weather in New York?")
yield ModelRequestEvent(model_request=model_request)
# Execution pauses here until the Runner processes the event and resumes the agent
# When resumed, the agent now has access to the LLM's response
```

### 2. AgentResponse Event

Generated when the agent has a response to send to the user.

```python
from google.adk.runtime.events import AgentResponseEvent

# Inside an agent's logic
yield AgentResponseEvent(response="The weather in New York is sunny today.")
# The Runner will deliver this response to the user
```

### 3. ToolCall Event

Generated when the agent needs to invoke a tool.

```python
from google.adk.runtime.events import ToolCallEvent

# Inside an agent's logic
tool_args = {"city": "New York"}
yield ToolCallEvent(tool_name="get_weather", tool_args=tool_args)
# Execution pauses here until the Runner processes the event (calls the tool) and resumes the agent
# When resumed, the agent now has access to the tool's result
```

### 4. State Change Event

Generated when the agent wants to update session state.

```python
from google.adk.runtime.events import StateChangeEvent

# Inside an agent's logic
state_delta = {"last_city": "New York"}
yield StateChangeEvent(state_delta=state_delta)
# The Runner will commit this state change
```

## Advanced Runtime Usage

### 1. Custom Runners

You can create custom runners for specialized deployment scenarios:

```python
from google.adk.runtime import Runner
from google.adk.sessions import InMemorySessionService

class CustomRunner(Runner):
    """Custom runner with specialized behavior."""
    
    def __init__(self, agent, **kwargs):
        super().__init__(agent, session_service=InMemorySessionService(), **kwargs)
        self.metrics = {}  # Custom metrics tracking
    
    async def process_event(self, event):
        # Track metrics before processing
        event_type = type(event).__name__
        self.metrics[event_type] = self.metrics.get(event_type, 0) + 1
        
        # Call the parent implementation to actually process the event
        await super().process_event(event)
        
        # Additional custom logic after processing
        if hasattr(event, 'response') and event.response:
            print(f"Response length: {len(event.response)}")
```

### 2. Custom Event Handlers

You can add custom event handlers for specialized event processing:

```python
from google.adk.runtime import Runner

class MonitoringRunner(Runner):
    """Runner with custom event handlers for monitoring."""
    
    async def handle_tool_call_event(self, event):
        # Track tool usage metrics before calling the parent handler
        print(f"Tool called: {event.tool_name}")
        start_time = time.time()
        
        # Call the parent implementation to actually process the event
        result = await super().handle_tool_call_event(event)
        
        # Record metrics after tool execution
        duration = time.time() - start_time
        print(f"Tool {event.tool_name} completed in {duration:.2f}s")
        
        return result
```

### 3. Custom Events

You can define custom events for specialized scenarios:

```python
from google.adk.runtime.events import Event

class MetricsEvent(Event):
    """Custom event for recording metrics."""
    
    def __init__(self, metric_name, metric_value):
        super().__init__()
        self.metric_name = metric_name
        self.metric_value = metric_value

# Then add a handler in your custom runner
class MetricsRunner(Runner):
    """Runner that handles custom metrics events."""
    
    async def handle_metrics_event(self, event):
        # Process the metrics event
        print(f"Metric recorded: {event.metric_name} = {event.metric_value}")
        
        # You might send this to a monitoring system, database, etc.
        if hasattr(self, 'metrics'):
            self.metrics[event.metric_name] = event.metric_value
        
        # Custom events should return an empty list if they don't generate
        # any new events themselves
        return []
```

## Runtime Configuration

The Runtime can be configured through various options:

### 1. Services Configuration

```python
from google.adk.runtime import Runner
from google.adk.agents import Agent
from google.adk.sessions import FileSessionService
from google.adk.artifacts import GcsArtifactService
from google.adk.memory import VectorMemoryService

# Create services
session_service = FileSessionService(directory="sessions")
artifact_service = GcsArtifactService(bucket_name="my-artifacts")
memory_service = VectorMemoryService(collection_name="agent-memory")

# Create an agent
agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    instruction="Be helpful.",
    # These services can also be passed directly to the agent
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service
)

# Create a runner with the services
runner = Runner(
    agent=agent,
    session_service=session_service,  # Same as passed to agent, or could be different
    artifact_service=artifact_service,
    memory_service=memory_service
)

# Run the agent
response = runner.run("Hello, agent!", session_id="user-123")
```

### 2. Execution Options

```python
from google.adk.runtime import Runner

# Create a runner with custom execution options
runner = Runner(
    agent=my_agent,
    timeout=30,  # Maximum time in seconds for the agent to run
    max_iterations=50,  # Maximum number of event loop iterations
    execution_mode="async"  # "async" or "sync"
)
```

## Using the Runner Directly

Most of the time, you'll use the agent's `run()` method, which internally uses a Runner. But you can also use a Runner directly for more control:

```python
from google.adk.runtime import Runner

# Create a runner
runner = Runner(agent=my_agent)

# Run synchronously
response = runner.run("Hello, agent!", session_id="user-123")

# Or run asynchronously
import asyncio

async def run_agent_async():
    response = await runner.run_async("Hello, agent!", session_id="user-123")
    return response

asyncio.run(run_agent_async())
```

## Debugging the Runtime

When troubleshooting runtime issues, consider these techniques:

### 1. Event Logging

```python
from google.adk.runtime import Runner
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("adk.runtime")

# Create a runner that will log events
runner = Runner(agent=my_agent)

# Run the agent - detailed events will be logged
response = runner.run("Hello, agent!")
```

### 2. Event Inspection with Callbacks

```python
from google.adk.agents import Agent

def inspect_model_requests(callback_context, llm_request):
    """Callback to inspect model requests before they're sent."""
    print(f"Model Request Event: {llm_request.prompt[:100]}...")
    return None

def inspect_tool_calls(callback_context, tool_name, tool_args):
    """Callback to inspect tool calls before they're made."""
    print(f"Tool Call Event: {tool_name}({tool_args})")
    return None

# Create an agent with debugging callbacks
debug_agent = Agent(
    name="debug_agent",
    model="gemini-2.0-flash",
    before_model_callback=inspect_model_requests,
    before_tool_callback=inspect_tool_calls
)
```

### 3. Custom Event Tracer

```python
class EventTracer(Runner):
    """Runner that traces all events for debugging."""
    
    def __init__(self, agent, **kwargs):
        super().__init__(agent, **kwargs)
        self.event_trace = []
    
    async def process_event(self, event):
        # Record the event before processing
        event_type = type(event).__name__
        event_info = {"type": event_type, "timestamp": time.time()}
        
        # Add event-specific data
        if hasattr(event, 'tool_name'):
            event_info["tool_name"] = event.tool_name
        if hasattr(event, 'response'):
            event_info["response_preview"] = str(event.response)[:50]
        
        self.event_trace.append(event_info)
        
        # Process the event normally
        return await super().process_event(event)
    
    def get_trace(self):
        """Return the event trace for analysis."""
        return self.event_trace
```

## Best Practices

1. **Event Efficiency**: Keep event generation efficient - only yield events when necessary.

2. **Service Separation**: Maintain clean separation between your agent logic and services.

3. **Error Handling**: Implement proper error handling in your agent code and custom runners.

4. **State Management**: Be mindful of state changes and their timing within the event loop.

5. **Testing**: Test your agents with different runner configurations to ensure proper behavior.

## Conclusion

Understanding the ADK Runtime and its event-based architecture gives you deeper insight into how your agents execute. This knowledge allows you to:

- Create more sophisticated agent behaviors
- Implement custom runners for specialized deployment scenarios
- Debug complex agent interactions
- Optimize performance by understanding the execution flow

While you don't need to interact with the Runtime directly for most use cases, this knowledge becomes valuable as your agent applications grow in complexity.
