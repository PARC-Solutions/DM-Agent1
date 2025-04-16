# Tutorial: Building a Multi-Agent System

This tutorial walks you through building a more sophisticated application that demonstrates how to compose multiple specialized agents to work together.

## Prerequisites

Before starting this tutorial, ensure:
- You have completed the basic [Quickstart](./2_Quickstart.md)
- You have a Python 3.9+ environment with ADK installed
- You understand the basic concept of agents and tools

## Overview: Building a Customer Support System

In this tutorial, we'll build a customer support system with two specialized agents:
1. **Router Agent**: Determines the type of customer inquiry
2. **Support Agent**: Handles specific customer support queries

This architecture demonstrates a multi-agent approach where each agent has a specialized role, and they work together to provide a comprehensive solution.

## 1. Project Setup

Create a project directory:

```bash
mkdir support_system
cd support_system
```

Create the necessary files:

```bash
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

## 2. Create the Router Agent

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

## 3. Create the Support Agent

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

## 4. Combine Agents in Main Application

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

## 5. Run the Multi-Agent System

Execute your support system:

```bash
python -m support_system.main
```

You can now interact with your customer support system via the terminal or browser interface (typically at http://localhost:8080).

## 6. Testing the System

Try the following test inquiries:

1. "How much does the PremiumPhone Pro cost?"
2. "What are the features of the BasicPhone X1?"
3. "My phone's battery is draining too quickly, can you help?"
4. "What are your store hours?"

## What You've Learned

In this tutorial, you've built a multi-agent system where:
- The router agent analyzes and classifies customer inquiries
- The support agent provides detailed responses based on a knowledge base
- A sequential workflow connects these specialized agents

This architecture demonstrates key ADK concepts:
- Specialized agents with defined roles
- Tool usage for accessing external data
- Workflow agents for orchestration
- Multi-stage processing of user requests

## Next Steps

- Learn more about [Agent types](../2_CoreConcepts/1_Agents.md) to understand other orchestration patterns
- Explore [Tools](../2_CoreConcepts/2_Tools.md) to enhance your agents' capabilities
- Add [Sessions and Memory](../2_CoreConcepts/3_Sessions_and_Memory.md) to track conversation history
- Implement [Evaluation](../5_Advanced/4_Evaluation.md) to measure and improve agent performance
