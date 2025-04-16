# Agents

## Agents Overview

In the Agent Development Kit (ADK), an **Agent** is a self-contained execution unit designed to act autonomously to achieve specific goals. Agents can perform tasks, interact with users, utilize external tools, and coordinate with other agents.

The foundation for all agents in ADK is the `BaseAgent` class. It serves as the fundamental blueprint. To create functional agents, you typically extend `BaseAgent` in one of three main ways, catering to different needs – from intelligent reasoning to structured process control.

## Core Agent Categories

ADK provides distinct agent categories to build sophisticated applications:

### 1. LLM Agents (`LLMAgent`, `Agent`)

LLM Agents utilize Large Language Models (LLMs) as their core engine to:
- Understand natural language
- Reason and plan
- Generate responses 
- Dynamically decide how to proceed or which tools to use

They are ideal for flexible, language-centric tasks where the agent needs to determine the best action based on user input.

```python
from google.adk.agents import Agent

# Creating a simple LLM Agent
my_agent = Agent(
    name="simple_agent",
    model="gemini-2.0-flash",  # The LLM model to use
    description="A helpful assistant that answers questions.",
    instruction="Always be concise and direct in your responses."
)
```

### 2. Workflow Agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`)

Workflow Agents control the execution flow of other agents in predefined, deterministic patterns without using an LLM for the flow control itself:

- **SequentialAgent**: Runs agents one after another, passing the output of each to the next
- **ParallelAgent**: Runs multiple agents simultaneously and combines their results
- **LoopAgent**: Repeatedly executes an agent until a condition is met

```python
from google.adk.agents import SequentialAgent, Agent

# Create individual agents
agent1 = Agent(name="data_collector", model="gemini-2.0-flash", description="Collects user data")
agent2 = Agent(name="data_analyzer", model="gemini-2.0-flash", description="Analyzes collected data")

# Create a sequential workflow
workflow = SequentialAgent(
    name="data_processing_workflow",
    description="Collects and analyzes user data",
    agents=[agent1, agent2]  # These will run in sequence
)
```

### 3. Custom Agents (Direct `BaseAgent` extensions)

Created by extending `BaseAgent` directly, these agents allow you to implement unique operational logic, specific control flows, or specialized integrations not covered by the standard types.

```python
from google.adk.agents import BaseAgent

class MyCustomAgent(BaseAgent):
    """A custom agent with specialized behavior."""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        # Custom initialization
    
    def run(self, new_message, **kwargs):
        # Custom execution logic
        return self._create_response("This is a custom response")
```

## Agents Working Together: Multi-Agent Systems

While each agent type serves a distinct purpose, the true power often comes from combining multiple agents to form sophisticated AI applications:

- **LLM Agents** handle intelligent, language-based task execution
- **Workflow Agents** manage the overall process flow using standard patterns
- **Custom Agents** provide specialized capabilities for unique integrations

Here's a typical multi-agent system architecture:

```
                    ┌───────────────────┐
                    │   Main Workflow   │
                    │  (SequentialAgent)│
                    └─────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
   ┌──────────▼──────────┐       ┌────────────▼────────────┐
   │   Router Agent      │       │   Specialist Agents     │
   │     (LLMAgent)      │───────▶      (LLMAgents)        │
   └─────────────────────┘       └─────────────────────────┘
```

## Agent Configuration Options

When creating agents, you have various configuration options:

### Basic Configuration

```python
agent = Agent(
    name="my_agent",                    # Required: Unique identifier
    model="gemini-2.0-flash",           # Required for LLM agents: Model to use
    description="A helpful assistant",  # Optional: Short description
    instruction="Be concise and helpful" # Optional: Detailed instructions
)
```

### Advanced Configuration

```python
agent = Agent(
    name="advanced_agent",
    model="gemini-2.0-flash",
    description="An advanced agent with many features",
    instruction="Detailed instructions here...",
    tools=[tool1, tool2],                # Optional: Tools for the agent to use
    enable_streaming=True,               # Optional: Enable streaming responses
    temperature=0.2,                     # Optional: Control randomness (0.0-1.0)
    session_service=my_session_service,  # Optional: Custom session service
    memory_service=my_memory_service,    # Optional: Custom memory service
    before_model_callback=my_callback    # Optional: Add callback functions
)
```

## Best Practices for Agent Design

1. **Specialized Responsibilities**: Design agents with clear, focused responsibilities rather than creating monolithic agents that do everything.

2. **Clear Instructions**: Provide detailed instructions to guide your LLM agents' behavior; be specific about the tone, format, and approach you want.

3. **Appropriate Tools**: Equip agents with the right tools they need for their specific tasks.

4. **Thoughtful Orchestration**: Use workflow agents to coordinate complex processes among specialized agents.

5. **Validation and Guardrails**: Implement callbacks for input validation and output verification to ensure safe, reliable behavior.
