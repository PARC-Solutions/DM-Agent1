# Sessions and Memory

## Introduction to Conversational Context

Meaningful, multi-turn conversations require agents to understand context. Just like humans, they need to recall what's been said and done to maintain continuity and avoid repetition. The Agent Development Kit (ADK) provides structured ways to manage this context through `Session`, `State`, and `Memory`.

### Core Concepts

Think of interacting with your agent as having distinct conversation threads, potentially drawing upon long-term knowledge:

#### 1. Session: The Current Conversation Thread

A `Session` represents a single, ongoing interaction between a user and your agent system. It contains:

- The conversation history (previous messages exchanged)
- Temporary data (`State`) relevant only during this conversation
- Metadata about the conversation (timestamps, session ID, etc.)

Sessions are self-contained and typically don't share information between different user interactions unless explicitly configured to do so.

#### 2. State (`session.state`): Data Within the Current Conversation

`State` is data stored within a specific `Session`. It's used to manage information relevant only to the current, active conversation thread, such as:

- Items in a shopping cart during this chat
- User preferences mentioned in this session
- Variables needed for multi-step processes
- Temporary calculations or intermediate results

State data is tied to the session's lifecycle and is not automatically preserved across different sessions.

#### 3. Memory: Searchable, Cross-Session Information

`Memory` represents a store of information that might span multiple past sessions or include external data sources. It acts as a knowledge base the agent can search to recall information or context beyond the immediate conversation.

Examples of what might be stored in Memory:
- User preferences that persist across multiple conversations
- Knowledge snippets extracted from previous interactions
- External documents or information repositories
- Frequently asked questions and their answers

## Managing Context: Services

ADK provides services to manage these concepts:

### 1. SessionService: Managing Conversation Threads

The `SessionService` is responsible for:
- Creating new sessions
- Retrieving existing sessions
- Updating session history and state
- Storing and loading sessions from persistent storage

```python
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService

# Create a session service
session_service = InMemorySessionService()

# Create an agent with the session service
agent = Agent(
    name="stateful_agent",
    model="gemini-2.0-flash",
    description="An agent that remembers conversation context",
    session_service=session_service
)

# Interact with the agent
response1 = agent.run("My name is Alice.")
# The agent will remember this information in the same session
response2 = agent.run("What's my name?")  # Will respond with "Alice"
```

### 2. MemoryService: Managing the Long-Term Knowledge Store

The `MemoryService` handles:
- Ingesting information into the long-term store
- Searching stored knowledge based on queries
- Managing persistence of memory across sessions

```python
from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService

# Create a memory service
memory_service = InMemoryMemoryService()

# Create an agent with the memory service
agent = Agent(
    name="memory_agent",
    model="gemini-2.0-flash",
    description="An agent that can store and retrieve information in long-term memory",
    memory_service=memory_service
)

# Store information in memory
memory_service.add_memory("Alice prefers vegetarian food.")

# Later, potentially in a different session, the agent can retrieve this info
response = agent.run("What food does Alice prefer?")
# The agent will search memory and find the information about Alice's preferences
```

## Implementation Options

ADK offers different implementations for both `SessionService` and `MemoryService`, allowing you to choose the storage backend that best fits your application's needs:

### Session Service Implementations

1. **InMemorySessionService**:
   - Stores sessions in memory only
   - Perfect for development and testing
   - Sessions are lost when the application restarts
   
2. **FileSessionService**:
   - Persists sessions to the file system
   - Good for simple applications
   - Supports persistence across application restarts

3. **Database-backed implementations**:
   - Store sessions in databases like PostgreSQL, MongoDB, etc.
   - Suitable for production applications
   - Provides scalability and durability

### Memory Service Implementations

1. **InMemoryMemoryService**:
   - Stores memory items in RAM
   - Perfect for development and testing
   - Memory is lost when the application restarts
   
2. **VectorMemoryService**:
   - Uses vector embeddings for semantic search
   - Enables finding related information based on meaning
   - Can connect to various vector databases

## Working with Sessions and State

Here's how to work with sessions and state in your agent applications:

### Managing Session State

```python
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService

# Create a session service
session_service = InMemorySessionService()

# Define a callback to update session state
def before_response_callback(callback_context, response):
    # Access the current session
    session = callback_context.session
    
    # Read from session state
    user_name = session.state.get("user_name", "unknown user")
    
    # Update session state if the user provided their name
    if "my name is" in callback_context.user_message.lower():
        # Extract the name (simplified example)
        name_parts = callback_context.user_message.lower().split("my name is")
        if len(name_parts) > 1:
            name = name_parts[1].strip()
            session.state["user_name"] = name
    
    return None  # Continue normal processing

# Create an agent with the session service and callback
agent = Agent(
    name="stateful_agent",
    model="gemini-2.0-flash",
    description="An agent that remembers user information",
    session_service=session_service,
    before_response_callback=before_response_callback
)
```

### Working with Session IDs

For multi-user applications, you'll need to handle multiple concurrent sessions:

```python
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService

# Create a session service
session_service = InMemorySessionService()

# Create an agent with the session service
agent = Agent(
    name="multi_user_agent",
    model="gemini-2.0-flash",
    description="An agent that serves multiple users",
    session_service=session_service
)

# Function to handle a user interaction
def handle_user_interaction(user_id, message):
    # Generate a session ID (could be based on user ID or other factors)
    session_id = f"session_{user_id}"
    
    # Run the agent with the specific session ID
    response = agent.run(message, session_id=session_id)
    return response

# Example usage
response1 = handle_user_interaction("user1", "My name is Alice")
response2 = handle_user_interaction("user2", "My name is Bob")
response3 = handle_user_interaction("user1", "What's my name?")  # Will remember "Alice"
```

## Best Practices

1. **Choose the Right Storage**:
   - Use in-memory implementations for development and testing
   - Use persistent implementations for production applications

2. **Structure State Data**:
   - Organize state data with clear naming conventions
   - Don't overuse state; only store what's necessary

3. **Session Management**:
   - Create session IDs based on user identity or conversation context
   - Consider session timeouts and cleanup strategies

4. **Memory Usage**:
   - Be selective about what information goes into long-term memory
   - Consider privacy implications when storing user data

5. **Monitoring and Debugging**:
   - Add logging to track session and memory operations
   - Include observability to understand how state affects agent behavior

## Advanced Topics

For more sophisticated applications, consider:

1. **Custom Session Services**:
   - Implement your own `SessionService` to integrate with specific databases or storage systems
   - Add encryption or additional metadata to sessions

2. **Advanced Memory Patterns**:
   - Implement memory prioritization based on relevance or recency
   - Combine with RAG (Retrieval-Augmented Generation) for more powerful knowledge access

3. **Multi-Agent State Sharing**:
   - Configure how state is shared between agents in workflow configurations
   - Use sessions to coordinate complex multi-agent interactions

By effectively leveraging Sessions and Memory, your agents can provide personalized, context-aware experiences that feel much more natural and intelligent to users.
