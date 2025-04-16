"""
Coordinator Agent Tests

This module contains tests for the DenialAssistantAgent class to verify that
it initializes correctly and can process user queries.
"""

import pytest
from unittest.mock import patch, MagicMock

from agent.core.coordinator import DenialAssistantAgent
from agent.core.session_manager import SessionManager


def test_coordinator_agent_initialization():
    """Test that the coordinator agent initializes correctly."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Verify agent attributes
    assert agent.session_manager is session_manager
    assert agent.name == "medical_billing_denial_assistant"
    assert agent.description is not None and "denial" in agent.description.lower()
    
    # Verify sub-agents are set to None initially (will be implemented in Epic 5)
    assert agent.denial_classifier is None
    assert agent.claims_analyzer is None
    assert agent.remediation_advisor is None


def test_content_moderation_callback():
    """Test that the content moderation callback functions."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Call the content moderation callback directly
    test_response = "This is a test response."
    moderated_response = agent._content_moderation_callback({}, test_response)
    
    # In the placeholder implementation, it should return the original response unchanged
    assert moderated_response == test_response


def test_generate_text():
    """Test that the generate_text method produces appropriate responses."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Test with different types of queries
    carc_response = agent.generate_text("What are CARC codes?")
    assert "CARC" in carc_response
    assert "Claim Adjustment Reason Codes" in carc_response
    
    steps_response = agent.generate_text("How to resolve a denial?")
    assert "steps" in steps_response.lower() or "resolve" in steps_response.lower()
    
    general_response = agent.generate_text("Hello")
    assert len(general_response) > 0  # Should provide some kind of response


def test_process_query_new_session(session_manager):
    """Test that the agent can process a query with a new session."""
    # Create agent and process query
    agent = DenialAssistantAgent(session_manager)
    result = agent.process_query("What does CARC code 16 mean?")
    
    # Verify result structure
    assert "session_id" in result
    assert "response" in result
    assert len(result["response"]) > 0
    
    # Verify a session was created
    session = session_manager.get_session(result["session_id"])
    assert session is not None
    
    # Verify conversation was added to history
    assert len(session["conversation_history"]) == 1
    assert session["conversation_history"][0]["user_input"] == "What does CARC code 16 mean?"
    assert "CARC" in session["conversation_history"][0]["agent_response"]


def test_process_query_existing_session(session_manager, sample_session):
    """Test that the agent can process a query with an existing session."""
    # Create agent and process query with existing session
    agent = DenialAssistantAgent(session_manager)
    result = agent.process_query("How do I fix this issue?", sample_session)
    
    # Verify result structure
    assert "session_id" in result
    assert result["session_id"] == sample_session
    assert "response" in result
    assert len(result["response"]) > 0
    
    # Verify conversation was added to history
    session = session_manager.get_session(sample_session)
    assert len(session["conversation_history"]) == 2  # One from sample data + one new
    assert session["conversation_history"][1]["user_input"] == "How do I fix this issue?"
    assert len(session["conversation_history"][1]["agent_response"]) > 0


def test_process_query_expired_session(session_manager):
    """Test that the agent handles expired sessions correctly."""
    # Create agent
    agent = DenialAssistantAgent(session_manager)
    
    # Use a nonexistent session ID
    result = agent.process_query("Another question", "nonexistent-session-id")
    
    # Verify a new session was created
    assert "session_id" in result
    assert result["session_id"] != "nonexistent-session-id"
    assert "response" in result
    
    # Verify conversation was added to the new session
    new_session = session_manager.get_session(result["session_id"])
    assert new_session is not None
    assert len(new_session["conversation_history"]) == 1
