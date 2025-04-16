"""
Session Manager Tests

This module contains tests for the SessionManager class to verify that
it correctly handles session creation, retrieval, and updates.
"""

import time
import pytest
from typing import Dict, Any

from agent.core.session_manager import SessionManager


def test_session_creation(session_manager):
    """Test that sessions can be created with unique IDs."""
    session_id = session_manager.create_session()
    
    # Verify that we get a string ID
    assert isinstance(session_id, str)
    assert len(session_id) > 0
    
    # Verify that the session exists
    session = session_manager.get_session(session_id)
    assert session is not None
    
    # Verify that the session has the required fields
    assert "created_at" in session
    assert "last_active" in session
    assert "conversation_history" in session
    assert isinstance(session["conversation_history"], list)


def test_session_update(session_manager):
    """Test that session data can be updated correctly."""
    session_id = session_manager.create_session()
    
    # Update session with new data
    update_data = {
        "test_key": "test_value",
        "nested_data": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    
    result = session_manager.update_session(session_id, update_data)
    assert result is True
    
    # Verify that the session was updated
    session = session_manager.get_session(session_id)
    assert "test_key" in session
    assert session["test_key"] == "test_value"
    assert "nested_data" in session
    assert session["nested_data"]["key1"] == "value1"
    assert session["nested_data"]["key2"] == "value2"
    
    # Verify that the original data is still there
    assert "created_at" in session
    assert "last_active" in session
    assert "conversation_history" in session


def test_add_conversation_turn(session_manager):
    """Test that conversation turns can be added to the session history."""
    session_id = session_manager.create_session()
    
    # Add a conversation turn
    user_input = "What does CARC code 16 mean?"
    agent_response = "CARC code 16 indicates 'Claim/service lacks information or has submission/billing error(s).'"
    
    result = session_manager.add_conversation_turn(session_id, user_input, agent_response)
    assert result is True
    
    # Verify that the conversation history was updated
    session = session_manager.get_session(session_id)
    assert len(session["conversation_history"]) == 1
    assert session["conversation_history"][0]["user_input"] == user_input
    assert session["conversation_history"][0]["agent_response"] == agent_response
    assert "timestamp" in session["conversation_history"][0]


def test_get_nonexistent_session(session_manager):
    """Test that getting a nonexistent session returns None."""
    session = session_manager.get_session("nonexistent-session-id")
    assert session is None


def test_update_nonexistent_session(session_manager):
    """Test that updating a nonexistent session returns False."""
    result = session_manager.update_session("nonexistent-session-id", {"test_key": "test_value"})
    assert result is False


def test_delete_session(session_manager):
    """Test that sessions can be deleted."""
    session_id = session_manager.create_session()
    
    # Verify that the session exists
    session = session_manager.get_session(session_id)
    assert session is not None
    
    # Delete the session
    result = session_manager.delete_session(session_id)
    assert result is True
    
    # Verify that the session no longer exists
    session = session_manager.get_session(session_id)
    assert session is None


def test_last_active_updated(session_manager):
    """Test that last_active timestamp is updated when the session is accessed."""
    session_id = session_manager.create_session()
    
    # Get initial last_active time
    session = session_manager.get_session(session_id)
    initial_last_active = session["last_active"]
    
    # Wait a short time to ensure timestamp would change
    time.sleep(0.1)
    
    # Access the session again
    session = session_manager.get_session(session_id)
    
    # Verify that last_active was updated
    assert session["last_active"] > initial_last_active
