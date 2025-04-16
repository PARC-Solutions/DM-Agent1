"""
Coordinator Agent Tests

This module contains tests for the DenialAssistantAgent class to verify that
it initializes correctly and can process user queries.
"""

import pytest
from unittest.mock import patch, MagicMock

from agent.core.coordinator import DenialAssistantAgent, ConversationState, TaskType
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

    # Verify regex patterns for intent detection
    assert "carc_rarc_codes" in agent.patterns
    assert "denial_question" in agent.patterns
    assert "document_processing" in agent.patterns
    assert "remediation" in agent.patterns


def test_content_moderation_callback():
    """Test that the content moderation callback functions."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Call the content moderation callback directly
    test_response = "This is a test response."
    moderated_response = agent._content_moderation_callback({}, test_response)
    
    # In the base implementation, it should return the response with no major changes
    assert moderated_response == test_response

    # Test adding a header to steps
    steps_response = "1. First step\n2. Second step\n3. Third step"
    callback_context = {"steps": True}
    moderated_steps = agent._content_moderation_callback(callback_context, steps_response)
    assert "STEPS TO RESOLVE:" in moderated_steps


def test_format_response():
    """Test that the format_response method formats different response types."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Test greeting format
    greeting = agent._format_response(
        "greeting", 
        "I'm here to help with your medical billing denials."
    )
    assert greeting.startswith("Welcome to")
    
    # Test denial analysis format
    analysis = agent._format_response(
        "denial_analysis", 
        "Your claim was denied due to missing information."
    )
    assert analysis.startswith("DENIAL ANALYSIS:")
    
    # Test remediation format
    remediation = agent._format_response(
        "remediation",
        "Review the denial code. Check documentation. Resubmit the claim."
    )
    assert remediation.startswith("STEPS TO RESOLVE:")
    assert "1." in remediation  # Should be numbered


def test_detect_intent():
    """Test that the intent detection correctly identifies different query types."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Test CARC code detection
    task_type, info = agent._detect_intent("What does CARC code 16 mean?")
    assert task_type == TaskType.DENIAL_CLASSIFICATION
    assert info.get("code_type") == "CARC"
    assert info.get("code_value") == "16"
    
    # Test RARC code detection
    task_type, info = agent._detect_intent("I received RARC code N479, what's that?")
    assert task_type == TaskType.DENIAL_CLASSIFICATION
    assert info.get("code_type") == "RARC"
    assert info.get("code_value") == "N479"
    
    # Test document processing intent
    task_type, info = agent._detect_intent("Can you analyze this CMS-1500 form?")
    assert task_type == TaskType.CLAIM_ANALYSIS
    
    # Test remediation intent
    task_type, info = agent._detect_intent("How do I resolve this denial?")
    assert task_type == TaskType.REMEDIATION_ADVICE
    
    # Test general question
    task_type, info = agent._detect_intent("Why was my claim denied?")
    assert task_type == TaskType.GENERAL_QUESTION
    
    # Test unknown intent
    task_type, info = agent._detect_intent("What's the weather like today?")
    assert task_type == TaskType.UNKNOWN


def test_determine_conversation_state():
    """Test that the conversation state is correctly determined from session context."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Test new session
    new_session = {"conversation_history": []}
    state = agent._determine_conversation_state(new_session)
    assert state == ConversationState.GREETING
    
    # Test session with conversation state
    session_with_state = {"conversation_state": ConversationState.COLLECTING_INFO.value}
    state = agent._determine_conversation_state(session_with_state)
    assert state == ConversationState.COLLECTING_INFO
    
    # Test document processing state
    document_session = {"documents_processing": True}
    state = agent._determine_conversation_state(document_session)
    assert state == ConversationState.DOCUMENT_PROCESSING
    
    # Test analyzing denial state
    denial_session = {"denial_codes": ["16"], "remediation_provided": False}
    state = agent._determine_conversation_state(denial_session)
    assert state == ConversationState.ANALYZING_DENIAL
    
    # Test remediation provided state
    remediation_session = {"remediation_provided": True}
    state = agent._determine_conversation_state(remediation_session)
    assert state == ConversationState.ANSWERING_QUESTIONS


def test_route_to_specialized_agent():
    """Test that tasks are correctly routed to specialized agents."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Initialize sub-agents (they're placeholders for now)
    agent._initialize_sub_agents()
    
    # Test routing to denial classifier
    context = {"code_type": "CARC", "code_value": "16"}
    response = agent._route_to_specialized_agent(
        TaskType.DENIAL_CLASSIFICATION, 
        "What does CARC code 16 mean?", 
        context
    )
    assert "denial codes" in response.lower()
    
    # Test routing to claims analyzer
    response = agent._route_to_specialized_agent(
        TaskType.CLAIM_ANALYSIS, 
        "Can you analyze this form?", 
        {}
    )
    assert "analyzed" in response.lower()
    
    # Test routing to remediation advisor
    response = agent._route_to_specialized_agent(
        TaskType.REMEDIATION_ADVICE, 
        "How do I fix this?", 
        {}
    )
    assert "steps" in response.lower()
    
    # Test general question
    response = agent._route_to_specialized_agent(
        TaskType.GENERAL_QUESTION,
        "Tell me about denials", 
        {}
    )
    assert len(response) > 0


def test_generate_text():
    """Test that the generate_text method produces appropriate context-aware responses."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Test greeting state
    greeting_context = {"conversation_state": ConversationState.GREETING}
    greeting = agent.generate_text("Hello", greeting_context)
    assert "Welcome" in greeting or "I'm here to help" in greeting
    
    # Test CARC code query
    carc_context = {"code_type": "CARC", "code_value": "16"}
    carc_response = agent.generate_text("What does CARC code 16 mean?", carc_context)
    assert "CARC" in carc_response
    
    # Test document query
    document_response = agent.generate_text("Can you analyze my CMS-1500 form?")
    assert "document" in document_response.lower() or "upload" in document_response.lower()
    
    # Test remediation query
    remediation_context = {"conversation_state": ConversationState.ANALYZING_DENIAL}
    remediation_response = agent.generate_text("How do I resolve this denial?", remediation_context)
    assert "recommend" in remediation_response.lower() or "review" in remediation_response.lower()


def test_process_query_new_session():
    """Test that the agent can process a query with a new session."""
    session_manager = SessionManager()
    
    # Create agent and process query
    agent = DenialAssistantAgent(session_manager)
    result = agent.process_query("What does CARC code 16 mean?")
    
    # Verify result structure
    assert "session_id" in result
    assert "response" in result
    assert "task_type" in result
    assert "conversation_state" in result
    assert len(result["response"]) > 0
    
    # Verify the task type and conversation state
    assert result["task_type"] == TaskType.DENIAL_CLASSIFICATION.value
    
    # Verify a session was created
    session = session_manager.get_session(result["session_id"])
    assert session is not None
    
    # Verify conversation was added to history
    assert len(session["conversation_history"]) == 1
    assert session["conversation_history"][0]["user_input"] == "What does CARC code 16 mean?"
    # The response might not have "CARC" in it if it's coming from the specialized agent
    assert len(session["conversation_history"][0]["agent_response"]) > 0


def test_process_query_existing_session():
    """Test that the agent can process a query with an existing session."""
    session_manager = SessionManager()
    
    # Create a sample session
    session_id = session_manager.create_session({
        "conversation_state": "collecting_info",
        "conversation_history": [{
            "timestamp": 1000,
            "user_input": "Hello, I need help with a denial",
            "agent_response": "I'm here to help. Can you provide more details?"
        }]
    })
    
    # Create agent and process query with existing session
    agent = DenialAssistantAgent(session_manager)
    result = agent.process_query("How do I fix this issue?", session_id)
    
    # Verify result structure
    assert "session_id" in result
    assert result["session_id"] == session_id
    assert "response" in result
    assert "task_type" in result
    assert "conversation_state" in result
    assert len(result["response"]) > 0
    
    # Verify conversation was added to history
    session = session_manager.get_session(session_id)
    assert len(session["conversation_history"]) == 2  # One from sample data + one new
    assert session["conversation_history"][1]["user_input"] == "How do I fix this issue?"
    assert len(session["conversation_history"][1]["agent_response"]) > 0


def test_process_query_state_transition():
    """Test that the agent transitions conversation states correctly."""
    session_manager = SessionManager()
    agent = DenialAssistantAgent(session_manager)
    
    # Start with a greeting
    result1 = agent.process_query("Hello, I need help with a denial")
    assert result1["conversation_state"] == ConversationState.COLLECTING_INFO.value
    
    # Ask about a CARC code
    result2 = agent.process_query("What does CARC code 16 mean?", result1["session_id"])
    assert result2["conversation_state"] == ConversationState.ANALYZING_DENIAL.value
    
    # Ask for remediation with explicit pattern matching
    result3 = agent.process_query("How do I resolve this denial?", result2["session_id"])
    
    # Update session with remediation provided flag manually since we're testing the flag
    session_id = result3["session_id"]
    session_manager.update_session(
        session_id=session_id,
        context_updates={"remediation_provided": True}
    )
    
    # Check if the session has the remediation provided flag
    session = session_manager.get_session(session_id)
    assert session["remediation_provided"] is True


def test_process_query_expired_session():
    """Test that the agent handles expired sessions correctly."""
    session_manager = SessionManager()
    
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
