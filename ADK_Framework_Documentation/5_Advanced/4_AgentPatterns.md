# Advanced Agent Patterns

## Introduction

While a single agent can address many use cases, more complex applications often benefit from advanced agent patterns that combine multiple agents into sophisticated systems. This document explores these patterns, explaining how to compose agents together to solve complex problems, implement multi-step workflows, and create specialized agent systems.

ADK provides built-in support for many of these patterns through the `MultiAgent` class and its implementations. These patterns allow agents to collaborate, specialize, and build upon each other's strengths.

## Sequential Agents

The sequential pattern chains multiple agents together in a predefined order, with each agent building on the work of the previous one. This pattern is ideal for multi-step processes where each step has distinct requirements.

### Use Cases

- Multi-stage content creation (e.g., outline → draft → edit → polish)
- Data processing pipelines (e.g., extract → transform → analyze)
- Progressive refinement of responses
- Step-by-step problem solving

### Implementation

```python
from google.adk.agents import Agent, SequentialAgent

# Step 1: Create specialized agents for each stage
research_agent = Agent(
    name="researcher",
    model="gemini-2.0-pro",
    instruction="""
    You are a research specialist. Your job is to gather key facts about a topic.
    Provide only verified information with sources when possible.
    Focus on breadth rather than depth, gathering a wide range of relevant facts.
    """
)

outline_agent = Agent(
    name="outliner",
    model="gemini-2.0-pro",
    instruction="""
    You are an outline specialist. Based on research provided, create a structured outline.
    Organize information logically with clear sections and subsections.
    Ensure comprehensive coverage of the topic with a coherent flow.
    """
)

draft_agent = Agent(
    name="writer",
    model="gemini-2.0-pro",
    instruction="""
    You are a content writer. Based on the outline provided, write a full draft.
    Elaborate on each point with clear explanations and examples.
    Maintain a consistent tone and ensure content flows naturally between sections.
    """
)

editor_agent = Agent(
    name="editor",
    model="gemini-2.0-pro",
    instruction="""
    You are an editor. Improve the draft provided while preserving its content and structure.
    Fix grammatical errors, improve clarity, and enhance readability.
    Ensure consistent style and tone throughout the document.
    """
)

# Step 2: Create a sequential agent pipeline
content_creation_pipeline = SequentialAgent(
    name="content_creation_system",
    agents=[research_agent, outline_agent, draft_agent, editor_agent],
    description="A multi-stage system for creating high-quality content"
)

# Step 3: Run the pipeline
response = content_creation_pipeline.run("Create content about renewable energy technologies")
```

### Customizing the Pipeline

You can customize how information flows through the pipeline:

```python
from google.adk.agents import SequentialAgent

# Create a pipeline with custom prompts between stages
custom_pipeline = SequentialAgent(
    name="custom_pipeline",
    agents=[agent1, agent2, agent3],
    description="A customized sequential pipeline",
    
    # Define inter-stage prompts
    inter_agent_prompts=[
        "Based on the previous research, create a detailed plan.",
        "Using the plan above, implement a complete solution."
    ]
)
```

## Router Agents

The router pattern uses a central agent to analyze requests and route them to specialized agents based on the request's nature. This allows for specialization while maintaining a unified interface.

### Use Cases

- Multi-domain virtual assistants
- Complex systems with specialized components
- Customer service applications
- Knowledge bases with distinct subject areas

### Implementation

```python
from google.adk.agents import Agent, RouterAgent

# Step 1: Create specialized agents for different domains
tech_support_agent = Agent(
    name="tech_support",
    model="gemini-2.0-pro",
    instruction="""
    You are a technical support specialist. Provide accurate troubleshooting assistance
    for technical problems with computers, devices, and software.
    """
)

billing_agent = Agent(
    name="billing_support",
    model="gemini-2.0-pro",
    instruction="""
    You are a billing support specialist. Help with questions about invoices,
    payments, subscription plans, and billing cycles.
    """
)

product_info_agent = Agent(
    name="product_info",
    model="gemini-2.0-pro",
    instruction="""
    You are a product information specialist. Provide detailed information about
    our products, their features, specifications, and compatibility.
    """
)

# Step 2: Define routing rules and create the router agent
customer_support_system = RouterAgent(
    name="customer_support",
    model="gemini-2.0-flash",  # A faster model is fine for routing decisions
    description="Customer support system that routes queries to specialized agents",
    
    # Define the agents to route between
    agents={
        "tech_support": tech_support_agent,
        "billing": billing_agent,
        "product_info": product_info_agent
    },
    
    # Define routing instructions
    router_instruction="""
    You are a customer support coordinator. Your job is to determine the nature of 
    the customer's query and route it to the appropriate specialized agent.
    
    For technical problems, errors, or "how to" questions, route to "tech_support".
    For questions about payments, subscriptions, or invoices, route to "billing".
    For questions about product features or specifications, route to "product_info".
    
    Select EXACTLY ONE agent and briefly explain why you chose it.
    """
)

# Step 3: Process a customer query
response = customer_support_system.run("I'm having trouble connecting my new monitor to my laptop")
```

### Advanced Routing with Sub-routers

For complex systems, you can create hierarchical routing structures:

```python
# Create sub-routers for different departments
tech_department = RouterAgent(
    name="tech_department",
    model="gemini-2.0-flash",
    agents={
        "hardware": hardware_agent,
        "software": software_agent,
        "networking": networking_agent
    }
)

sales_department = RouterAgent(
    name="sales_department",
    model="gemini-2.0-flash",
    agents={
        "residential": residential_sales_agent,
        "business": business_sales_agent,
        "enterprise": enterprise_sales_agent
    }
)

# Create a main router that routes to sub-routers
company_system = RouterAgent(
    name="company_system",
    model="gemini-2.0-flash",
    agents={
        "tech_support": tech_department,
        "sales": sales_department,
        "general": general_info_agent
    }
)
```

## Competing Agents

The competing pattern involves multiple agents generating responses independently, then selecting the best response through an evaluator agent. This pattern can produce higher quality results, especially for subjective or creative tasks.

### Use Cases

- Creative writing and content generation
- Problem-solving with multiple approaches
- Generating and selecting the best ideas
- Subjective tasks with multiple valid outcomes

### Implementation

```python
from google.adk.agents import Agent, CompetingAgent

# Step 1: Create multiple agents with different approaches
creative_agent = Agent(
    name="creative",
    model="gemini-2.0-pro",
    instruction="""
    You are a creative copywriter. Write engaging, imaginative content that
    captures attention with vivid language and unique perspectives.
    Be bold, innovative, and think outside the box.
    """
)

formal_agent = Agent(
    name="formal",
    model="gemini-2.0-pro",
    instruction="""
    You are a formal copywriter. Write professional, clear, and authoritative content.
    Use precise language, maintain a consistent tone, and present information
    in a structured, logical manner. Be concise and avoid unnecessary embellishment.
    """
)

conversational_agent = Agent(
    name="conversational",
    model="gemini-2.0-pro",
    instruction="""
    You are a conversational copywriter. Write in a friendly, approachable style
    that feels like a natural conversation. Use everyday language, occasional humor,
    and direct address to build rapport with the reader.
    """
)

# Step 2: Create a competing agent system with evaluator criteria
copywriting_system = CompetingAgent(
    name="copywriting_system",
    model="gemini-2.0-pro",  # The model used for evaluation
    description="A system that generates and selects the best copywriting approach",
    
    # The agents competing to provide responses
    agents=[creative_agent, formal_agent, conversational_agent],
    
    # Criteria for evaluating the responses
    evaluator_instruction="""
    You are a senior copywriting director. Evaluate the provided copywriting samples
    based on the following criteria:
    
    1. Effectiveness: How well it communicates the key message
    2. Engagement: How likely it is to capture and maintain reader interest
    3. Appropriateness: How well it matches the likely audience and purpose
    4. Uniqueness: How it stands out from typical content on this topic
    
    Select the BEST response for the given prompt. Consider the context and
    what would be most effective for the specific request.
    Explain your reasoning briefly before announcing your selection.
    """
)

# Step 3: Generate and select the best copywriting approach
response = copywriting_system.run("Write a product description for our new eco-friendly water bottle")
```

### Customizing the Evaluation

You can customize how responses are evaluated and selected:

```python
from google.adk.agents import CompetingAgent

# Create a competing system with custom evaluation
specialized_competing_system = CompetingAgent(
    name="specialized_competing_system",
    model="gemini-2.0-pro",
    agents=[agent1, agent2, agent3, agent4],
    
    # Define a specific evaluation framework
    evaluator_instruction="""
    Evaluate the responses using this scoring rubric:
    - Accuracy (0-10 points): Correctness of information
    - Completeness (0-10 points): Coverage of all relevant aspects
    - Clarity (0-10 points): Clear explanation and readability
    - Practicality (0-10 points): Usefulness in real-world application
    
    Calculate a total score for each response.
    Select the response with the highest score.
    If there's a tie, prefer the response that scored higher on Accuracy.
    """
)
```

## Composite Agent Patterns

For more complex applications, you can combine these patterns to create sophisticated agent systems.

### Example: Multi-stage Analysis System

Combining sequential and router patterns:

```python
from google.adk.agents import Agent, SequentialAgent, RouterAgent

# Create specialized data analysis agents
financial_analyzer = Agent(name="financial_analyzer", model="gemini-2.0-pro")
social_trend_analyzer = Agent(name="social_trend_analyzer", model="gemini-2.0-pro")
technical_analyzer = Agent(name="technical_analyzer", model="gemini-2.0-pro")

# Create a router for analysis type
analysis_router = RouterAgent(
    name="analysis_router",
    model="gemini-2.0-flash",
    agents={
        "financial": financial_analyzer,
        "social": social_trend_analyzer,
        "technical": technical_analyzer
    }
)

# Create agents for the sequential steps
data_processor = Agent(name="data_processor", model="gemini-2.0-pro")
insight_generator = Agent(name="insight_generator", model="gemini-2.0-pro")
report_creator = Agent(name="report_creator", model="gemini-2.0-pro")

# Combine them into a multi-stage analysis system
analysis_system = SequentialAgent(
    name="advanced_analysis_system",
    agents=[
        data_processor,  # First process the data
        analysis_router, # Then route to appropriate specialized analyzer
        insight_generator, # Then generate insights
        report_creator  # Finally create a report
    ]
)
```

### Example: Competing Workflows

Combining competing and sequential patterns:

```python
from google.adk.agents import Agent, SequentialAgent, CompetingAgent

# Create two different workflows for content creation
workflow1 = SequentialAgent(
    name="standard_workflow",
    agents=[research_agent1, outline_agent1, writing_agent1]
)

workflow2 = SequentialAgent(
    name="alternative_workflow",
    agents=[research_agent2, writing_agent2, editing_agent2]
)

# Create a competing agent to select the best result
content_system = CompetingAgent(
    name="content_creation_system",
    model="gemini-2.0-pro",
    agents=[workflow1, workflow2],
    evaluator_instruction="Select the better content based on quality, engagement, and accuracy."
)
```

## Agent Teams

Agent Teams represent a flexible collaboration pattern where multiple agents work together under the coordination of a team manager agent. Unlike more rigid patterns like sequential or router agents, Agent Teams enable more dynamic collaboration.

### Use Cases

- Complex problem-solving requiring diverse expertise
- Projects needing iterative refinement and collaboration
- Simulating group discussions or multiple perspectives
- Tasks benefiting from parallel processing and integration

### Implementation

```python
from google.adk.agents import Agent, AgentTeam

# Step 1: Create specialized team members
researcher = Agent(
    name="researcher",
    model="gemini-2.0-pro",
    instruction="You research facts and data relevant to the topic."
)

idea_generator = Agent(
    name="idea_generator",
    model="gemini-2.0-pro",
    instruction="You generate creative ideas and solutions."
)

critic = Agent(
    name="critic",
    model="gemini-2.0-pro",
    instruction="You analyze proposals critically, identifying potential issues."
)

implementer = Agent(
    name="implementer",
    model="gemini-2.0-pro",
    instruction="You create practical implementation plans."
)

# Step 2: Create the team with manager
problem_solving_team = AgentTeam(
    name="problem_solving_team",
    model="gemini-2.0-pro",  # Model for the team manager
    description="A collaborative team that solves complex problems",
    
    # Team members
    agents=[researcher, idea_generator, critic, implementer],
    
    # Team manager instructions
    manager_instruction="""
    You are the coordinator of a problem-solving team with these specialists:
    - Researcher: Gathers relevant facts and data
    - Idea Generator: Creates innovative solutions
    - Critic: Identifies potential issues and weaknesses
    - Implementer: Develops practical implementation plans
    
    Your job is to:
    1. Break down the problem and assign initial tasks to appropriate team members
    2. Integrate their input and identify areas needing further exploration
    3. Facilitate additional rounds of collaboration as needed
    4. Synthesize a final comprehensive solution
    
    Ensure all team members contribute where their expertise is valuable.
    """
)

# Step 3: Solve a complex problem
response = problem_solving_team.run(
    "How can a mid-sized city reduce traffic congestion while improving accessibility?"
)
```

### Customizing Team Dynamics

You can customize team collaboration parameters:

```python
from google.adk.agents import AgentTeam

# Create a team with custom collaboration settings
custom_team = AgentTeam(
    name="custom_team",
    model="gemini-2.0-pro",
    agents=[agent1, agent2, agent3, agent4],
    
    # Control collaboration rounds
    max_collaboration_rounds=3,  # Limit to 3 rounds of collaboration
    
    # Custom manager instructions
    manager_instruction="""
    Coordinate the team as follows:
    - First round: Assign each specialist to analyze a different aspect of the problem
    - Second round: Have specialists respond to each other's analyses
    - Third round: Focus on creating an integrated solution
    
    When team members disagree, highlight the disagreement and have them
    directly address each other's points before proceeding.
    """,
    
    # Define how assignments are given to team members
    assignment_strategy="parallel"  # All members work simultaneously on each round
)
```

## Reflective Agents

Reflective agents incorporate self-evaluation and iterative improvement. These agents first generate a response, then critically evaluate that response, and finally refine the response based on their evaluation.

### Use Cases

- Complex reasoning tasks requiring high accuracy
- Content requiring careful review and refinement
- Learning systems that improve through iteration
- Applications where avoiding errors is critical

### Implementation

```python
from google.adk.agents import Agent, ReflectiveAgent

# Create a reflective agent
reflective_agent = ReflectiveAgent(
    name="reflective_reasoner",
    model="gemini-2.0-pro",
    description="An agent that thinks carefully and refines its reasoning",
    
    # Initial instruction for generating the first draft
    initial_instruction="""
    You are an expert problem solver. Break down complex problems step by step,
    carefully considering all relevant factors. Show your reasoning clearly.
    """,
    
    # Instruction for the reflection/evaluation phase
    reflection_instruction="""
    Critically evaluate your previous response. Consider:
    - Are there errors in reasoning or calculations?
    - Did you make any unjustified assumptions?
    - Are there important factors or perspectives you didn't consider?
    - Is the explanation clear and complete?
    
    Identify specific improvements needed, if any.
    """,
    
    # Instruction for the refinement phase
    refinement_instruction="""
    Based on your reflection, create an improved response that addresses
    the issues identified. Maintain the strengths of the original while
    fixing weaknesses. Make your reasoning explicit and comprehensive.
    """
)

# Use the reflective agent to solve a problem
response = reflective_agent.run(
    "Design a system to optimize package delivery in a dense urban area"
)
```

### Custom Reflection Patterns

You can customize the reflection process:

```python
from google.adk.agents import ReflectiveAgent

# Create a reflective agent with multiple reflection cycles
deep_reflective_agent = ReflectiveAgent(
    name="deep_reflective_agent",
    model="gemini-2.0-pro",
    
    # Enable multiple reflection cycles
    reflection_cycles=2,  # Will go through reflection and refinement twice
    
    # Include specific self-checking mechanisms
    reflection_instruction="""
    First, check your factual accuracy by asking:
    - Are all stated facts verifiable?
    - Are there any contradictions?
    - Have I made any unsupported claims?
    
    Then, evaluate your reasoning by asking:
    - Does each conclusion follow logically from the premises?
    - Have I considered alternative explanations?
    - Are there any fallacies in my reasoning?
    
    Be specific about any issues found.
    """
)
```

## Hybrid Patterns and Custom Implementations

For especially complex applications, you might need to create custom agent patterns beyond the built-in implementations. ADK provides the flexibility to do this by subclassing `MultiAgent` or creating custom integrations.

### Implementing Custom Patterns

```python
from google.adk.agents import MultiAgent, Agent

class AdaptiveAgent(MultiAgent):
    """Custom agent pattern that adapts based on response confidence."""
    
    def __init__(self, simple_agent, complex_agent, **kwargs):
        super().__init__(**kwargs)
        self.simple_agent = simple_agent
        self.complex_agent = complex_agent
        self.confidence_threshold = 0.7
    
    async def run_async(self, user_message, session_id=None):
        # First try with the simpler, faster model
        simple_response = await self.simple_agent.run_async(user_message, session_id)
        
        # Check confidence (this would be an actual implementation that
        # extracts confidence information from the response)
        confidence = self._extract_confidence(simple_response)
        
        # If confidence is high enough, return this response
        if confidence >= self.confidence_threshold:
            return simple_response
        
        # Otherwise, use the more complex agent
        return await self.complex_agent.run_async(user_message, session_id)
    
    def _extract_confidence(self, response):
        # Implementation would extract a confidence score from the response
        # This is a placeholder
        return 0.5  # For this example, always use the complex agent

# Create the component agents
simple_agent = Agent(name="simple", model="gemini-2.0-flash")
complex_agent = Agent(name="complex", model="gemini-2.0-pro")

# Create the adaptive agent
adaptive_system = AdaptiveAgent(
    name="adaptive_system",
    simple_agent=simple_agent,
    complex_agent=complex_agent,
    description="System that adapts based on response confidence"
)
```

## Best Practices

### Choosing the Right Pattern

Consider these factors when selecting an agent pattern:

1. **Task Complexity**: More complex tasks often benefit from sequential or team patterns.
2. **Specialization Needs**: If different aspects require different expertise, consider router or team patterns.
3. **Quality vs. Speed**: Competing and reflective patterns prioritize quality but take longer.
4. **Decision Characteristics**: If steps are clear and linear, sequential works well; if branching decisions are needed, router patterns are better.

### Performance Considerations

Multi-agent patterns can increase latency and costs. Consider these optimizations:

1. **Model Selection**: Use faster/smaller models for routing or initial processing steps.
2. **Caching**: Implement caching for common requests or sub-components.
3. **Asynchronous Processing**: Use asynchronous calls when appropriate.
4. **Limit Depth**: Excessive nesting of patterns can lead to diminishing returns.

### Design Principles

1. **Clear Instructions**: Each agent should have clear, specific instructions.
2. **Appropriate Specialization**: Ensure agents have meaningfully different capabilities or knowledge.
3. **Thoughtful Information Flow**: Consider what information needs to be passed between agents.
4. **Maintainability**: More complex systems are harder to debug and maintain.

## Conclusion

Advanced agent patterns allow you to build sophisticated AI systems by composing specialized agents together. By selecting the appropriate pattern for your use case and carefully designing each component, you can create systems that handle complex tasks effectively.

These patterns enable:
- Breaking down complex problems into manageable parts
- Leveraging specialized capabilities for different aspects of a task
- Implementing multi-step workflows with clear progression
- Comparing different approaches to select the best results
- Creating collaborative systems that leverage diverse expertise

As agent technology matures, these patterns will become increasingly important for building effective, maintainable, and powerful AI applications.
