"""
Multi-Agent System Example

This example demonstrates how to create a multi-agent system with a coordinator
that delegates tasks to specialized sub-agents.

To run this example:
1. Make sure you have the ADK installed: pip install google-adk
2. Set up your API keys as environment variables:
   - GOOGLE_API_KEY: Your Google API key with access to the Gemini API
3. Run this file: python multi_agent_system.py
"""

import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools import tool

# Load environment variables from .env file (if present)
load_dotenv()

# Define a simple tool for the math agent
@tool
def calculate_expression(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.
    
    Args:
        expression: A mathematical expression as a string (e.g., "2 + 2 * 3")
        
    Returns:
        The result of the calculation.
    """
    try:
        # Using eval is generally not safe for production, but for simple demo purposes
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

def main():
    """
    Creates and runs a multi-agent system with a coordinator and specialized agents.
    """
    # Create specialized agents
    
    # A greeter agent that handles introductions and farewells
    greeter_agent = LlmAgent(
        name="greeter",
        model="gemini-2.0-flash",
        description="I handle greetings and farewells for users.",
        instruction="""
        You are a friendly greeter agent. Your job is to:
        1. Welcome users in a warm, professional manner
        2. Say goodbye when users are leaving
        3. Only respond to messages that are greetings, introductions, or farewells
        4. For any other queries, inform the coordinator that this isn't your specialty
        """
    )
    
    # A math agent for calculations
    math_agent = LlmAgent(
        name="math_specialist",
        model="gemini-2.0-flash",
        description="I specialize in mathematical calculations.",
        instruction="""
        You are a math specialist agent. Your job is to:
        1. Answer questions about mathematics
        2. Perform calculations using the calculate_expression tool
        3. Only respond to messages related to mathematics
        4. For any other queries, inform the coordinator that this isn't your specialty
        """,
        tools=[calculate_expression]
    )
    
    # A general knowledge agent
    knowledge_agent = LlmAgent(
        name="knowledge_specialist",
        model="gemini-2.0-flash",
        description="I provide general knowledge information.",
        instruction="""
        You are a knowledge specialist agent. Your job is to:
        1. Answer general knowledge questions about history, science, geography, etc.
        2. Provide factual information based on your training data
        3. Only respond to messages seeking factual information
        4. For any other queries, inform the coordinator that this isn't your specialty
        """
    )
    
    # Create a coordinator agent that delegates to sub-agents
    coordinator = LlmAgent(
        name="coordinator",
        model="gemini-2.0-flash",
        description="I coordinate between different specialized agents.",
        instruction="""
        You are a coordinator agent responsible for routing user queries to the right
        specialized agent. Your job is to:
        
        1. Analyze each user query and determine which sub-agent is best equipped to handle it
        2. For greetings and farewells, use the greeter agent
        3. For mathematical questions and calculations, use the math specialist
        4. For general knowledge questions, use the knowledge specialist
        5. If multiple agents might be relevant, choose the most appropriate one
        6. Always provide a brief introduction when handing off to a specialist agent
        """,
        sub_agents=[
            greeter_agent,
            math_agent,
            knowledge_agent
        ]
    )

    # Print welcome message
    print("Multi-Agent System is ready! Ask any question or type 'exit' to quit.")
    
    # Start conversation loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Assistant: Goodbye!")
            break
            
        # Process the user query and get the response
        response = coordinator.run(user_input)
        
        # Display the response
        print(f"\nAssistant: {response.text}")

if __name__ == "__main__":
    main()
