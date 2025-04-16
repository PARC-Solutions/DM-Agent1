"""
Agent System Integration Tests

This module contains integration tests to verify that the entire agent system
is functioning correctly as an integrated whole.
"""

import os
import pytest
from unittest.mock import patch

from agent.core.coordinator import DenialAssistantAgent
from agent.core.session_manager import SessionManager


@patch.object(DenialAssistantAgent, 'generate_text')
def test_end_to_end_query_flow(mock_generate_text):
    """Test the end-to-end flow of processing a user query through the agent system."""
    # Set up mock response
    mock_generate_text.return_value = "CARC code 16 indicates 'Claim/service lacks information or has submission/billing error(s).'"
    
    # Create core components
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Process a query
    query = "What does CARC code 16 mean?"
    result = agent.process_query(query)
    
    # Verify response
    assert "session_id" in result
    assert "response" in result
    assert "Claim/service lacks information" in result["response"]
    
    # Verify session was created and conversation was stored
    session_id = result["session_id"]
    session = session_manager.get_session(session_id)
    
    assert session is not None
    assert "conversation_history" in session
    assert len(session["conversation_history"]) > 0
    assert session["conversation_history"][0]["user_input"] == query
    assert "Claim/service lacks information" in session["conversation_history"][0]["agent_response"]


@patch.object(DenialAssistantAgent, 'generate_text')
def test_multi_turn_conversation(mock_generate_text):
    """Test a multi-turn conversation with the agent system."""
    # Set up mock responses for multiple turns
    mock_responses = [
        "CARC code 16 indicates 'Claim/service lacks information or has submission/billing error(s).'",
        "To resolve this issue, you'll need to add the missing information to the claim and resubmit it."
    ]
    mock_generate_text.side_effect = mock_responses
    
    # Create core components
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # First turn
    query1 = "What does CARC code 16 mean?"
    result1 = agent.process_query(query1)
    session_id = result1["session_id"]
    
    # Second turn, using the same session
    query2 = "How do I resolve this issue?"
    result2 = agent.process_query(query2, session_id)
    
    # Verify responses for both turns
    assert "Claim/service lacks information" in result1["response"]
    assert "add the missing information" in result2["response"]
    
    # Verify conversation history has both turns
    session = session_manager.get_session(session_id)
    assert len(session["conversation_history"]) == 2
    assert session["conversation_history"][0]["user_input"] == query1
    assert session["conversation_history"][1]["user_input"] == query2
