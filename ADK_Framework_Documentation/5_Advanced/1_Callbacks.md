# Callbacks

## Introduction: What are Callbacks and Why Use Them?

Callbacks are a cornerstone feature of ADK, providing a powerful mechanism to hook into an agent's execution process. They allow you to observe, customize, and even control the agent's behavior at specific, predefined points without modifying the core ADK framework code.

In essence, callbacks are standard Python functions that you define and associate with an agent when you create it. The ADK framework automatically calls your functions at key stages in the agent's lifecycle, such as:

* Before or after the agent's main processing logic runs
* Before sending a request to, or after receiving a response from, the Large Language Model (LLM)
* Before executing a tool (like a Python function or another agent) or after it finishes

## Benefits of Using Callbacks

Callbacks unlock significant flexibility and enable advanced agent capabilities:

* **Observe & Debug**: Log detailed information at critical steps for monitoring and troubleshooting
* **Customize & Control**: Modify data flowing through the agent (like LLM requests or tool results) or even bypass certain steps entirely
* **Implement Guardrails**: Enforce safety rules, validate inputs/outputs, or prevent disallowed operations
* **Manage State**: Read or dynamically update the agent's session state during execution

## How to Use Callbacks

### Registering Callbacks

You register callbacks by passing your defined Python functions as arguments to the agent's constructor (`__init__`) when you create an instance of `Agent` or `LlmAgent`:

```python
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional

# Define your callback function
def my_before_model_logic(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    print(f"Callback running before model call for agent: {callback_context.agent_name}")
    # ... your custom logic here ...
    return None # Allow the model call to proceed

# Register it during Agent creation
my_agent = Agent(
    name="MyCallbackAgent",
    model="gemini-2.0-flash",
    instruction="Be helpful.",
    # Other agent parameters...
    before_model_callback=my_before_model_logic # Pass the function here
)
```

### Available Callback Types

ADK provides several callback hooks that execute at different points in the agent's lifecycle:

#### Model Callbacks

**Before Model Callback**: Executes before the LLM is called.

```python
def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Args:
        callback_context: Contains information about the current context
        llm_request: The request about to be sent to the LLM
        
    Returns:
        Optional[LlmResponse]: If None, the normal LLM call proceeds. 
                               If a response is returned, it's used instead of calling the LLM.
    """
    # You can modify the request before it's sent to the model
    llm_request.prompt = f"{llm_request.prompt}\n\nRemember to be concise and factual."
    
    # Or you can log information for debugging
    print(f"About to call LLM with prompt: {llm_request.prompt[:100]}...")
    
    # Return None to proceed with the modified request
    return None
```

**After Model Callback**: Executes after receiving a response from the LLM.

```python
def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse:
    """
    Args:
        callback_context: Contains information about the current context
        llm_response: The response received from the LLM
        
    Returns:
        LlmResponse: The potentially modified response
    """
    # You can modify the response from the model
    if "inappropriate content" in llm_response.text.lower():
        llm_response.text = "I apologize, but I cannot provide that information."
    
    # Or log the response for debugging
    print(f"Received response from LLM: {llm_response.text[:100]}...")
    
    return llm_response
```

#### Tool Callbacks

**Before Tool Callback**: Executes before a tool is called.

```python
def before_tool_callback(
    callback_context: CallbackContext, tool_name: str, tool_args: dict
) -> Optional[dict]:
    """
    Args:
        callback_context: Contains information about the current context
        tool_name: Name of the tool about to be called
        tool_args: Arguments to be passed to the tool
        
    Returns:
        Optional[dict]: If None, the normal tool call proceeds.
                       If a dict is returned, it's used as the tool's result.
    """
    # Log tool usage
    print(f"About to call tool: {tool_name} with args: {tool_args}")
    
    # You can validate tool arguments
    if tool_name == "search_web" and "query" in tool_args:
        if len(tool_args["query"]) < 3:
            return {
                "status": "error", 
                "message": "Search query must be at least 3 characters long"
            }
    
    # Return None to proceed with the tool call
    return None
```

**After Tool Callback**: Executes after a tool has been called.

```python
def after_tool_callback(
    callback_context: CallbackContext, tool_name: str, tool_args: dict, tool_result: dict
) -> dict:
    """
    Args:
        callback_context: Contains information about the current context
        tool_name: Name of the tool that was called
        tool_args: Arguments that were passed to the tool
        tool_result: The result returned by the tool
        
    Returns:
        dict: The potentially modified tool result
    """
    # Log the tool result
    print(f"Tool {tool_name} returned: {tool_result}")
    
    # You can modify the tool result
    if tool_name == "get_weather" and tool_result["status"] == "success":
        # Add a disclaimer
        tool_result["disclaimer"] = "Weather information is approximate."
    
    return tool_result
```

#### Agent Lifecycle Callbacks

**Before Request Callback**: Executes at the beginning of agent processing.

```python
def before_request_callback(
    callback_context: CallbackContext, user_message: str
) -> Optional[LlmResponse]:
    """
    Args:
        callback_context: Contains information about the current context
        user_message: The message from the user
        
    Returns:
        Optional[LlmResponse]: If None, normal agent processing proceeds.
                               If a response is returned, it's used instead of normal processing.
    """
    # Check for prohibited topics or keywords
    prohibited_keywords = ["hack", "illegal", "bypass security"]
    if any(keyword in user_message.lower() for keyword in prohibited_keywords):
        return LlmResponse(text="I cannot assist with illegal activities.")
    
    # Update session state
    session = callback_context.session
    if session:
        session.state["last_message_time"] = time.time()
        session.state["message_count"] = session.state.get("message_count", 0) + 1
    
    # Return None to proceed with normal processing
    return None
```

**Before Response Callback**: Executes before the final response is returned to the user.

```python
def before_response_callback(
    callback_context: CallbackContext, response: LlmResponse
) -> LlmResponse:
    """
    Args:
        callback_context: Contains information about the current context
        response: The response about to be returned to the user
        
    Returns:
        LlmResponse: The potentially modified response
    """
    # Add a footer to all responses
    response.text = f"{response.text}\n\n[Response generated by MyAgent v1.0]"
    
    # Log the final response
    print(f"Final response: {response.text}")
    
    return response
```

## The Callback Context

The `CallbackContext` object provides important information about the current execution context. It includes:

```python
class CallbackContext:
    # The agent's name
    agent_name: str
    
    # The user's message that initiated this execution
    user_message: str
    
    # The current session (if a session service is configured)
    session: Optional[Session]
    
    # The execution path so far (tool calls, etc.)
    trajectory: List[TrajectoryEvent]
    
    # Custom data that can be used to pass information between callbacks
    custom_data: Dict[str, Any]
```

You can use `callback_context` to access information about the current state and to pass information between different callbacks.

## Practical Examples

### Example 1: Content Moderation

This example implements content moderation using callbacks:

```python
def content_moderation_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse:
    """Filter out inappropriate content from responses."""
    # Simple keyword-based filtering
    inappropriate_keywords = ["hate", "violence", "illegal"]
    
    # Check if any inappropriate keywords are in the response
    if any(keyword in llm_response.text.lower() for keyword in inappropriate_keywords):
        return LlmResponse(
            text="I apologize, but I cannot provide that information as it may contain inappropriate content."
        )
    
    return llm_response

# Create an agent with the moderation callback
moderated_agent = Agent(
    name="moderated_agent",
    model="gemini-2.0-flash",
    instruction="Be helpful but avoid inappropriate content.",
    after_model_callback=content_moderation_callback
)
```

### Example 2: Adding Contextual Information

This example adds contextual information (like the current time) to the agent's prompt:

```python
import datetime

def add_context_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Add current time to the context."""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Append current time to the prompt
    llm_request.prompt = f"{llm_request.prompt}\n\nCurrent time: {current_time}"
    
    return None

# Create an agent with the context-adding callback
contextual_agent = Agent(
    name="contextual_agent",
    model="gemini-2.0-flash",
    instruction="Be helpful and time-aware.",
    before_model_callback=add_context_callback
)
```

### Example 3: Performance Monitoring

This example measures and logs performance metrics:

```python
import time

def performance_start_callback(
    callback_context: CallbackContext, user_message: str
) -> Optional[LlmResponse]:
    """Record the start time of processing."""
    # Store the start time in custom_data
    callback_context.custom_data["start_time"] = time.time()
    return None

def performance_end_callback(
    callback_context: CallbackContext, response: LlmResponse
) -> LlmResponse:
    """Calculate and log processing time."""
    start_time = callback_context.custom_data.get("start_time")
    if start_time:
        processing_time = time.time() - start_time
        print(f"Request processed in {processing_time:.2f} seconds")
        
        # You could also store this in a database or monitoring system
    
    return response

# Create an agent with performance monitoring callbacks
monitored_agent = Agent(
    name="monitored_agent",
    model="gemini-2.0-flash",
    instruction="Be helpful.",
    before_request_callback=performance_start_callback,
    before_response_callback=performance_end_callback
)
```

### Example 4: Tool Usage Control

This example controls and validates tool usage:

```python
def tool_control_callback(
    callback_context: CallbackContext, tool_name: str, tool_args: dict
) -> Optional[dict]:
    """Control which tools can be used based on rules."""
    
    # Get the user's role from session state
    session = callback_context.session
    user_role = session.state.get("user_role", "basic") if session else "basic"
    
    # Define tool permissions
    restricted_tools = {
        "basic": ["get_public_info", "search_documentation"],
        "premium": ["get_public_info", "search_documentation", "get_analytics"],
        "admin": ["get_public_info", "search_documentation", "get_analytics", "update_settings"]
    }
    
    # Check if the user is allowed to use this tool
    allowed_tools = restricted_tools.get(user_role, [])
    if tool_name not in allowed_tools:
        return {
            "status": "error",
            "message": f"You do not have permission to use the '{tool_name}' tool."
        }
    
    # For certain tools, add additional validation
    if tool_name == "get_analytics" and "date_range" in tool_args:
        # Validate date range format
        try:
            start_date, end_date = tool_args["date_range"].split(":")
            # Additional validation logic could go here
        except:
            return {
                "status": "error",
                "message": "Invalid date range format. Use 'start_date:end_date'."
            }
    
    # Allow the tool call to proceed
    return None

# Create an agent with tool control
controlled_agent = Agent(
    name="controlled_agent",
    model="gemini-2.0-flash",
    instruction="Use tools according to user permissions.",
    tools=[get_public_info, search_documentation, get_analytics, update_settings],
    before_tool_callback=tool_control_callback
)
```

## Advanced Callback Patterns

### Callback Chaining

You can build complex behavior by chaining multiple callbacks together. In this case, each callback should focus on a single responsibility:

```python
# First callback: Add context
def add_context(context, llm_request):
    # Add current time, user info, etc.
    llm_request.prompt += "\n\nAdditional context: ..."
    return None

# Second callback: Apply safety filters
def apply_safety_filters(context, llm_request):
    # Check for safety concerns
    # ...
    return None

# Third callback: Log the request
def log_request(context, llm_request):
    # Log the request for auditing
    print(f"Request from user {context.session.user_id}: {llm_request.prompt[:100]}...")
    return None

# Combine callbacks using a helper function
def combined_callback(context, llm_request):
    # Run each callback in sequence
    for callback in [add_context, apply_safety_filters, log_request]:
        result = callback(context, llm_request)
        if result is not None:
            return result  # Early return if any callback returns a value
    return None

# Create agent with the combined callback
agent = Agent(
    name="advanced_agent",
    model="gemini-2.0-flash",
    before_model_callback=combined_callback
)
```

### Stateful Callbacks

You can create callbacks with their own state by using classes:

```python
class RateLimitingCallback:
    def __init__(self, requests_per_minute=10):
        self.requests_per_minute = requests_per_minute
        self.request_times = {}  # Maps session_id to list of request timestamps
    
    def before_request(self, callback_context, user_message):
        """Implement rate limiting per session."""
        current_time = time.time()
        session_id = callback_context.session.id if callback_context.session else "default"
        
        # Initialize or update request times for this session
        if session_id not in self.request_times:
            self.request_times[session_id] = []
        
        # Clean up old request times (older than 1 minute)
        self.request_times[session_id] = [
            t for t in self.request_times[session_id]
            if current_time - t < 60
        ]
        
        # Check if rate limit exceeded
        if len(self.request_times[session_id]) >= self.requests_per_minute:
            return LlmResponse(
                text="Rate limit exceeded. Please try again later."
            )
        
        # Record this request
        self.request_times[session_id].append(current_time)
        return None

# Create the callback instance
rate_limiter = RateLimitingCallback(requests_per_minute=5)

# Create agent with the stateful callback
agent = Agent(
    name="rate_limited_agent",
    model="gemini-2.0-flash",
    before_request_callback=rate_limiter.before_request
)
```

## Best Practices for Callbacks

1. **Single Responsibility**: Each callback should focus on a single aspect of behavior modification.

2. **Error Handling**: Implement proper error handling in callbacks to prevent crashes.

3. **Performance Awareness**: Keep callbacks efficient, as they execute during the agent's processing pipeline.

4. **Immutability**: When possible, create new objects rather than modifying existing ones.

5. **Testing**: Test callbacks independently to ensure they behave as expected.

6. **Documentation**: Document what each callback does and its expected behavior.

7. **Logging**: Include appropriate logging in callbacks for debugging and monitoring.

## Debugging Callbacks

When callbacks aren't working as expected, use these debugging techniques:

1. **Print Statements**: Add print statements to see when callbacks are being called and what data they're receiving.

```python
def debug_callback(callback_context, llm_request):
    print(f"Callback triggered for agent: {callback_context.agent_name}")
    print(f"User message: {callback_context.user_message}")
    print(f"LLM prompt: {llm_request.prompt[:100]}...")
    return None
```

2. **Inspect the Callback Context**: Examine the callback context to understand the current state.

```python
def inspect_context(callback_context, llm_request):
    print("Session state:", callback_context.session.state if callback_context.session else "No session")
    print("Trajectory:", [event.tool_name for event in callback_context.trajectory if hasattr(event, 'tool_name')])
    return None
```

3. **Use Try/Except**: Wrap callback logic in try/except blocks to catch and log errors.

```python
def safe_callback(callback_context, llm_request):
    try:
        # Your callback logic here
        return None
    except Exception as e:
        print(f"Callback error: {e}")
        import traceback
        traceback.print_exc()
        return None  # Continue normal processing despite the error
```

## Conclusion

Callbacks provide a powerful mechanism for extending and customizing agent behavior without modifying the core ADK code. By strategically inserting callback functions at key points in the agent's execution flow, you can implement features like content moderation, performance monitoring, custom integrations, and more.

As your agents become more sophisticated, callbacks will become an essential tool for implementing advanced behaviors while maintaining a clean, modular codebase.
