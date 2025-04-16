"""
Session Manager Tests

This module contains tests for the SessionManager class to verify that
it correctly handles session creation, retrieval, and updates.
"""

import time
import json
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
    assert "conversation_state" in session
    assert session["conversation_state"] == "greeting"
    assert "remediation_provided" in session
    assert session["remediation_provided"] is False
    assert "documents_processing" in session
    assert session["documents_processing"] is False


def test_session_creation_with_initial_context(session_manager):
    """Test that sessions can be created with initial context."""
    initial_context = {
        "conversation_state": "collecting_info",
        "claim_details": {"claim_id": "12345", "provider": "ABC Health"},
        "denial_codes": ["16", "A6"]
    }
    
    session_id = session_manager.create_session(initial_context)
    
    # Verify that the session exists with initial context
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session["conversation_state"] == "collecting_info"
    assert session["claim_details"]["claim_id"] == "12345"
    assert session["claim_details"]["provider"] == "ABC Health"
    assert "16" in session["denial_codes"]
    assert "A6" in session["denial_codes"]


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


def test_add_conversation_turn_with_metadata(session_manager):
    """Test that conversation turns can be added with metadata."""
    session_id = session_manager.create_session()
    
    # Add a conversation turn with metadata
    user_input = "What does CARC code 16 mean?"
    agent_response = "CARC code 16 indicates 'Claim/service lacks information or has submission/billing error(s).'"
    metadata = {
        "task_type": "denial_classification",
        "intent": "code_explanation",
        "confidence": 0.95
    }
    
    result = session_manager.add_conversation_turn(session_id, user_input, agent_response, metadata)
    assert result is True
    
    # Verify that the conversation history was updated with metadata
    session = session_manager.get_session(session_id)
    assert len(session["conversation_history"]) == 1
    assert session["conversation_history"][0]["user_input"] == user_input
    assert session["conversation_history"][0]["agent_response"] == agent_response
    assert "metadata" in session["conversation_history"][0]
    assert session["conversation_history"][0]["metadata"]["task_type"] == "denial_classification"
    assert session["conversation_history"][0]["metadata"]["intent"] == "code_explanation"
    assert session["conversation_history"][0]["metadata"]["confidence"] == 0.95


def test_history_truncation(session_manager):
    """Test that conversation history is truncated when it exceeds maximum length."""
    # Override max_history_length to a smaller value for testing
    session_manager.max_history_length = 3
    
    session_id = session_manager.create_session()
    
    # Add more turns than max_history_length
    for i in range(5):
        session_manager.add_conversation_turn(
            session_id,
            f"Question {i+1}",
            f"Answer {i+1}"
        )
    
    # Verify that history was truncated
    session = session_manager.get_session(session_id)
    assert len(session["conversation_history"]) == 3
    
    # Verify that we kept the first turn and the most recent turns
    assert session["conversation_history"][0]["user_input"] == "Question 1"
    assert session["conversation_history"][1]["user_input"] == "Question 4"
    assert session["conversation_history"][2]["user_input"] == "Question 5"


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


def test_add_document_reference(session_manager):
    """Test that document references can be added to a session."""
    session_id = session_manager.create_session()
    
    # Add a document reference
    document_id = "doc-123456"
    document_type = "cms1500"
    document_metadata = {
        "filename": "claim_form.pdf",
        "size": 1024,
        "content_type": "application/pdf",
        "page_count": 2
    }
    
    result = session_manager.add_document_reference(
        session_id,
        document_id,
        document_type,
        document_metadata
    )
    assert result is True
    
    # Verify that the document reference was added
    session = session_manager.get_session(session_id)
    assert len(session["documents"]) == 1
    assert session["documents"][0]["document_id"] == document_id
    assert session["documents"][0]["document_type"] == document_type
    assert session["documents"][0]["metadata"]["filename"] == "claim_form.pdf"
    assert "added_timestamp" in session["documents"][0]


def test_get_document_references(session_manager):
    """Test that document references can be retrieved."""
    session_id = session_manager.create_session()
    
    # Add document references of different types
    session_manager.add_document_reference(
        session_id,
        "doc-1",
        "cms1500",
        {"filename": "claim1.pdf"}
    )
    
    session_manager.add_document_reference(
        session_id,
        "doc-2",
        "eob",
        {"filename": "eob1.pdf"}
    )
    
    session_manager.add_document_reference(
        session_id,
        "doc-3",
        "cms1500",
        {"filename": "claim2.pdf"}
    )
    
    # Get all documents
    documents = session_manager.get_document_references(session_id)
    assert len(documents) == 3
    
    # Get documents by type
    cms_documents = session_manager.get_document_references(session_id, "cms1500")
    assert len(cms_documents) == 2
    assert cms_documents[0]["document_type"] == "cms1500"
    assert cms_documents[1]["document_type"] == "cms1500"
    
    eob_documents = session_manager.get_document_references(session_id, "eob")
    assert len(eob_documents) == 1
    assert eob_documents[0]["document_type"] == "eob"


def test_update_document_reference(session_manager):
    """Test that document references can be updated."""
    session_id = session_manager.create_session()
    
    # Add a document reference
    document_id = "doc-123456"
    session_manager.add_document_reference(
        session_id,
        document_id,
        "cms1500",
        {"filename": "claim_form.pdf", "status": "pending"}
    )
    
    # Update the same document with new metadata
    session_manager.add_document_reference(
        session_id,
        document_id,
        "cms1500",
        {"filename": "claim_form.pdf", "status": "processed"}
    )
    
    # Verify that the document was updated, not duplicated
    session = session_manager.get_session(session_id)
    assert len(session["documents"]) == 1
    assert session["documents"][0]["metadata"]["status"] == "processed"


def test_remove_document_reference(session_manager):
    """Test that document references can be removed."""
    session_id = session_manager.create_session()
    
    # Add document references
    session_manager.add_document_reference(
        session_id,
        "doc-1",
        "cms1500",
        {"filename": "claim1.pdf"}
    )
    
    session_manager.add_document_reference(
        session_id,
        "doc-2",
        "eob",
        {"filename": "eob1.pdf"}
    )
    
    # Verify documents were added
    session = session_manager.get_session(session_id)
    assert len(session["documents"]) == 2
    
    # Remove one document
    result = session_manager.remove_document_reference(session_id, "doc-1")
    assert result is True
    
    # Verify document was removed
    session = session_manager.get_session(session_id)
    assert len(session["documents"]) == 1
    assert session["documents"][0]["document_id"] == "doc-2"


def test_get_conversation_history(session_manager):
    """Test that conversation history can be retrieved."""
    session_id = session_manager.create_session()
    
    # Add conversation turns
    for i in range(5):
        session_manager.add_conversation_turn(
            session_id,
            f"Question {i+1}",
            f"Answer {i+1}"
        )
    
    # Get all history
    history = session_manager.get_conversation_history(session_id)
    assert len(history) == 5
    
    # Get limited history
    limited_history = session_manager.get_conversation_history(session_id, max_turns=3)
    assert len(limited_history) == 3
    assert limited_history[0]["user_input"] == "Question 1"  # First turn
    assert limited_history[1]["user_input"] == "Question 4"  # Second-to-last turn
    assert limited_history[2]["user_input"] == "Question 5"  # Last turn


def test_export_import_session(session_manager):
    """Test that sessions can be exported and imported."""
    # Create a session with data
    original_session_id = session_manager.create_session()
    session_manager.update_session(original_session_id, {
        "conversation_state": "analyzing_denial",
        "claim_details": {"claim_id": "12345"},
        "denial_codes": ["16"]
    })
    session_manager.add_conversation_turn(
        original_session_id,
        "What's the problem with my claim?",
        "Your claim was denied due to missing information."
    )
    
    # Export the session
    exported_data = session_manager.export_session(original_session_id)
    assert exported_data is not None
    
    # Verify the exported data contains session information
    exported_json = json.loads(exported_data)
    assert exported_json["session_id"] == original_session_id
    assert exported_json["conversation_state"] == "analyzing_denial"
    assert exported_json["claim_details"]["claim_id"] == "12345"
    assert len(exported_json["conversation_history"]) == 1
    
    # Import the session with a new ID
    imported_session_id = session_manager.import_session(exported_data)
    assert imported_session_id is not None
    assert imported_session_id == original_session_id  # Should maintain the same ID
    
    # Verify the imported session has the same data
    imported_session = session_manager.get_session(imported_session_id)
    assert imported_session["conversation_state"] == "analyzing_denial"
    assert imported_session["claim_details"]["claim_id"] == "12345"
    assert len(imported_session["conversation_history"]) == 1


def test_cleanup_expired_sessions(session_manager):
    """Test that expired sessions are cleaned up."""
    # Override session_ttl to a very small value for testing
    original_ttl = session_manager.session_ttl
    session_manager.session_ttl = 0.1  # 100 milliseconds
    
    # Create a few sessions
    session_ids = []
    for _ in range(3):
        session_ids.append(session_manager.create_session())
    
    # Wait for the sessions to expire
    time.sleep(0.2)
    
    # Clean up expired sessions
    count = session_manager.cleanup_expired_sessions()
    
    # Verify all sessions were cleaned up
    assert count == 3
    for session_id in session_ids:
        assert session_manager.get_session(session_id) is None
    
    # Restore original TTL
    session_manager.session_ttl = original_ttl
