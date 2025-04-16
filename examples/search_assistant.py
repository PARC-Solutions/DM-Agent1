"""
Search Assistant Example

This example demonstrates how to create a simple agent that can search the web
using Google Search.

To run this example:
1. Make sure you have the ADK installed: pip install google-adk
2. Set up your API keys as environment variables:
   - GOOGLE_API_KEY: Your Google API key with access to the Gemini API
   - GOOGLE_SEARCH_API_KEY: Your Google Search API key
   - GOOGLE_SEARCH_ENGINE_ID: Your Google Custom Search Engine ID
3. Run this file: python search_assistant.py
"""

import os
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import google_search

# Load environment variables from .env file (if present)
load_dotenv()

def main():
    """
    Creates and runs a simple search assistant agent.
    """
    # Create the agent
    search_assistant = Agent(
        name="search_assistant",
        model="gemini-2.0-flash",  # Or your preferred Gemini model
        instruction="You are a helpful assistant. Answer user questions using Google Search when needed.",
        description="An assistant that can search the web.",
        tools=[google_search]  # Use the built-in Google Search tool
    )

    # Print welcome message
    print("Search Assistant is ready! Ask any question or type 'exit' to quit.")
    
    # Start conversation loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Search Assistant: Goodbye!")
            break
            
        # Process the user query and get the response
        response = search_assistant.run(user_input)
        
        # Display the response
        print(f"\nSearch Assistant: {response.text}")

if __name__ == "__main__":
    main()
