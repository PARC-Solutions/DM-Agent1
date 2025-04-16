#!/usr/bin/env python3
"""
Medical Billing Denial Agent - Main Application Entry Point

This script initializes and runs the Medical Billing Denial Agent system,
which helps healthcare providers analyze and resolve medical billing denials.
"""

import os
import logging
import sys
import time

from agent.core.coordinator import DenialAssistantAgent
from agent.core.session_manager import SessionManager
from config.environment import load_environment, validate_environment, check_google_cloud_setup

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, logging_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_cli_interface(agent):
    """
    Run a simple command-line interface for testing the agent.
    
    Args:
        agent: The DenialAssistantAgent to interact with
    """
    session_id = None
    print("\nMedical Billing Denial Agent CLI")
    print("--------------------------------")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\n> ")
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            # Process the query
            start_time = time.time()
            result = agent.process_query(user_input, session_id)
            end_time = time.time()
            
            # Update session ID if first interaction
            session_id = result["session_id"]
            
            # Print the response
            print("\n{}".format(result['response']))
            
            # Display processing metrics
            processing_time = end_time - start_time
            print("\n[Processed in {:.2f}s | Session: {}...]".format(processing_time, session_id[:8]))
            
        except KeyboardInterrupt:
            print("\nSession terminated by user.")
            break
        except Exception as e:
            logger.error("Error processing query: {}".format(e))
            print("\nAn error occurred: {}".format(e))


def main():
    """Initialize and run the Medical Billing Denial Agent system"""
    logger.info("Starting Medical Billing Denial Agent system")
    
    # Load and validate environment
    try:
        load_environment()
        validate_environment()
    except ValueError as e:
        logger.error("Environment validation failed: {}".format(e))
        logger.error("Please set all required environment variables in .env file")
        sys.exit(1)
    
    # Check Google Cloud setup
    if not check_google_cloud_setup():
        logger.warning("Google Cloud setup incomplete; some features may not work correctly")
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Initialize main coordinator agent
    denial_assistant = DenialAssistantAgent(session_manager=session_manager)
    
    # Print welcome message
    print("\nMedical Billing Denial Agent")
    print("\nNOTE: This is running in development mode with a simplified agent implementation.")
    print("      In a production environment, this would use the Google ADK with real LLM integration.")
    
    # Run CLI interface for testing
    run_cli_interface(denial_assistant)


if __name__ == "__main__":
    main()
