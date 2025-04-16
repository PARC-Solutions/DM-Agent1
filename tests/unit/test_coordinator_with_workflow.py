"""
Tests for the coordinator agent with the sequential workflow.

This module contains tests for the coordinator agent that uses the sequential
workflow system for managing denial resolution conversations.
"""

import pytest
from unittest.mock import MagicMock, patch, ANY
import json

from agent.core.coordinator import DenialAssistantAgent, ConversationState, TaskType
from agent.core.session_manager import SessionManager
from agent.core.workflow import WorkflowState, WorkflowDefinition
from agent.core.sequential_agent import SequentialDenialAgent
from agent.security.content_moderation import ContentModerator


class TestDenialAssistantAgentWithWorkflow:
    """Tests for the DenialAssistantAgent with workflow integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mocks
        self.session_manager = MagicMock(spec=SessionManager)
        self.sequential_agent = MagicMock(spec=SequentialDenialAgent)
        self.content_moderator = MagicMock(spec=ContentModerator)
        
        # Mock the session manager's methods
        self.session_manager.create_session.return_value = "test_session_id"
        self.session_manager.get_session.return_value = {
            "session_id": "test_session_id",
            "conversation_history": []
        }
        
        # Mock the sequential agent's process method
        self.sequential_agent.process.return_value = {
            "response": "This is a test response",
            "workflow_state": WorkflowState.COLLECTING_INFO.value
        }
        
        # Mock the visualize_conversation_flow method
        self.sequential_agent.visualize_conversation_flow.return_value = {
            "current_state": WorkflowState.COLLECTING_INFO.value,
            "conversation_states": [],
            "possible_next_states": []
        }
        
        # Mock the content moderator
        self.content_moderator.moderate_response.return_value = {
            "original_response": "This is a test response",
            "moderated_response": "This is a moderated test response",
            "moderation_details": {}
        }
        
        # Create the agent
        self.agent = DenialAssistantAgent(
            session_manager=self.session_manager,
            sequential_agent=self.sequential_agent,
            content_moderator=self.content_moderator
        )
        
        # Override the specialized agent initialization
        self.agent._initialize_specialized_agents = MagicMock()
    
    def test_initialization(self):
        """Test initialization of the agent."""
        assert self.agent.session_manager == self.session_manager
        assert self.agent.sequential_agent == self.sequential_agent
        assert self.agent.content_moderator == self.content_moderator
        
        # Specialized agents should be initialized
        self.agent._initialize_specialized_agents.assert_called_once()
    
    def test_process_query_new_session(self):
        """Test processing a query with a new session."""
        # Process a query
        result = self.agent.process_query("Hello, I need help with a denial", None)
        
        # Should create a new session
        self.session_manager.create_session.assert_called_once()
        
        # Should process through the sequential agent
        self.sequential_agent.process.assert_called_once()
        query_arg = self.sequential_agent.process.call_args[0][0]
        assert query_arg == "Hello, I need help with a denial"
        
        # Should moderate the response
        self.content_moderator.moderate_response.assert_called_once()
        
        # Should update the session with conversation turn
        self.session_manager.update_session.assert_called()
        
        # Should return a properly structured result
        assert "session_id" in result
        assert "response" in result
        assert "conversation_state" in result
        assert "workflow_state" in result
        assert "processing_time" in result
    
    def test_process_query_existing_session(self):
        """Test processing a query with an existing session."""
        # Set up an existing session
        existing_session = {
            "session_id": "existing_session_id",
            "conversation_history": [
                {"user_input": "Previous message", "agent_response": "Previous response"}
            ],
            "workflow_state": WorkflowState.GREETING.value
        }
        self.session_manager.get_session.return_value = existing_session
        
        # Process a query
        result = self.agent.process_query(
            "I have a claim with CARC code 16", 
            "existing_session_id"
        )
        
        # Should not create a new session
        assert self.session_manager.create_session.call_count == 0
        
        # Should get the existing session
        self.session_manager.get_session.assert_called_with("existing_session_id")
        
        # Should process through the sequential agent
        self.sequential_agent.process.assert_called_once()
        
        # Should return the existing session ID
        assert result["session_id"] == "existing_session_id"
    
    def test_reset_session_workflow(self):
        """Test resetting a session workflow."""
        # Mock the reset_workflow method
        self.sequential_agent.reset_workflow.return_value = {
            "workflow_state": WorkflowState.GREETING.value
        }
        
        # Reset a session workflow
        result = self.agent.reset_session_workflow("test_session_id")
        
        # Should call reset_workflow
        self.sequential_agent.reset_workflow.assert_called_once()
        
        # Should update the session
        self.session_manager.update_session.assert_called_with(
            session_id="test_session_id",
            context_updates={"workflow_state": WorkflowState.GREETING.value}
        )
        
        # Should return success
        assert result["success"] is True
        assert result["session_id"] == "test_session_id"
        assert result["workflow_state"] == WorkflowState.GREETING.value
    
    def test_visualize_session_workflow(self):
        """Test visualizing a session workflow."""
        # Visualize a session workflow
        result = self.agent.visualize_session_workflow("test_session_id")
        
        # Should call visualize_conversation_flow
        self.sequential_agent.visualize_conversation_flow.assert_called_once()
        
        # Should return visualization data
        assert result["success"] is True
        assert result["session_id"] == "test_session_id"
        assert "visualization" in result
    
    @patch('agent.core.coordinator.logger')
    def test_moderate_response(self, mock_logger):
        """Test response moderation."""
        # Set up test data
        response = "This is a test response with patient information"
        context = {
            "workflow_state": WorkflowState.COLLECTING_INFO.value,
            "task_type": TaskType.GENERAL_QUESTION.value
        }
        
        # Mock moderation result
        moderation_result = {
            "original_response": response,
            "moderated_response": "This is a moderated response",
            "moderation_details": {
                "phi_detected": True,
                "disclaimers_added": True
            }
        }
        self.content_moderator.moderate_response.return_value = moderation_result
        
        # Call the method
        result = self.agent._moderate_response(response, context)
        
        # Should call content_moderator.moderate_response
        self.content_moderator.moderate_response.assert_called_once()
        
        # Should log moderation actions
        mock_logger.info.assert_called_once()
        
        # Should return moderated response
        assert result == "This is a moderated response"
    
    def test_detect_intent_carc_code(self):
        """Test detecting intent with CARC code."""
        # Test with CARC code
        query = "I have a denial with CARC code 16"
        task_type, extracted_info = self.agent._detect_intent(query)
        
        assert task_type == TaskType.DENIAL_CLASSIFICATION
        assert extracted_info["code_type"] == "CARC"
        assert extracted_info["code_value"] == "16"
        assert extracted_info["carc_code"] == "16"
    
    def test_detect_intent_rarc_code(self):
        """Test detecting intent with RARC code."""
        # Test with RARC code
        query = "I have a denial with RARC code M54"
        task_type, extracted_info = self.agent._detect_intent(query)
        
        assert task_type == TaskType.DENIAL_CLASSIFICATION
        assert extracted_info["code_type"] == "RARC"
        assert extracted_info["code_value"] == "M54"
        assert extracted_info["rarc_code"] == "M54"
    
    def test_detect_intent_document(self):
        """Test detecting document processing intent."""
        # Test with document processing intent
        query = "I want to upload a CMS-1500 form"
        task_type, extracted_info = self.agent._detect_intent(query)
        
        assert task_type == TaskType.CLAIM_ANALYSIS
    
    def test_detect_intent_remediation(self):
        """Test detecting remediation intent."""
        # Test with remediation intent
        query = "How do I fix this denial?"
        task_type, extracted_info = self.agent._detect_intent(query)
        
        assert task_type == TaskType.REMEDIATION_ADVICE
    
    def test_map_workflow_to_conversation_state(self):
        """Test mapping workflow states to conversation states."""
        # Test mapping various workflow states
        assert self.agent._map_workflow_to_conversation_state(
            WorkflowState.GREETING.value) == ConversationState.GREETING.value
            
        assert self.agent._map_workflow_to_conversation_state(
            WorkflowState.COLLECTING_INFO.value) == ConversationState.COLLECTING_INFO.value
            
        assert self.agent._map_workflow_to_conversation_state(
            WorkflowState.ANALYZING_DENIAL_CODES.value) == ConversationState.ANALYZING_DENIAL.value
            
        assert self.agent._map_workflow_to_conversation_state(
            WorkflowState.GENERATING_REMEDIATION.value) == ConversationState.PROVIDING_REMEDIATION.value
            
        # Test with unknown workflow state - should default to COLLECTING_INFO
        assert self.agent._map_workflow_to_conversation_state(
            "unknown_state") == ConversationState.COLLECTING_INFO.value
    
    def test_handle_denial_classification(self):
        """Test handling denial classification."""
        # Create a mock classifier
        self.agent.denial_classifier = MagicMock()
        self.agent.denial_classifier.classify_denial.return_value = {
            "denial_type": "authorization_issue",
            "explanation": "This denial is due to missing authorization.",
            "severity": "high"
        }
        
        # Create a context with CARC code
        context = {
            "carc_code": "50",
            "rarc_code": "M62"
        }
        
        # Call the handler
        result = self.agent._handle_denial_classification(context)
        
        # Should call classify_denial
        self.agent.denial_classifier.classify_denial.assert_called_with(
            carc_code="50",
            rarc_code="M62",
            group_code=None
        )
        
        # Should return a response with formatted analysis
        assert "response" in result
        assert "DENIAL ANALYSIS:" in result["response"]
        assert "authorization_issue" in result["response"]
        assert "missing authorization" in result["response"]
        
        # Should return denial details
        assert result["denial_type"] == "authorization_issue"
        assert result["denial_explanation"] == "This denial is due to missing authorization."
        assert result["denial_severity"] == "high"
    
    def test_handle_claim_analysis(self):
        """Test handling claim analysis."""
        # Create a mock analyzer
        self.agent.claims_analyzer = MagicMock()
        self.agent.claims_analyzer.analyze_cms1500.return_value = {
            "summary": "Analysis of CMS-1500 form",
            "issues": ["Missing modifier", "Diagnosis code mismatch"],
            "carc_code": "16"
        }
        
        # Create a context with document references
        context = {
            "documents": [
                {"document_type": "cms1500", "path": "test.pdf"}
            ]
        }
        
        # Call the handler
        result = self.agent._handle_claim_analysis(context)
        
        # Should call analyze_cms1500
        self.agent.claims_analyzer.analyze_cms1500.assert_called_once()
        
        # Should return a response with formatted analysis
        assert "response" in result
        assert "CMS-1500 ANALYSIS:" in result["response"]
        assert "Analysis of CMS-1500 form" in result["response"]
        assert "Missing modifier" in result["response"]
        
        # Should extract and update CARC code
        assert context["carc_code"] == "16"
        
        # Should return analysis details
        assert result["analysis_result"]["summary"] == "Analysis of CMS-1500 form"
        assert len(result["identified_issues"]) == 2
    
    def test_handle_remediation_advice(self):
        """Test handling remediation advice."""
        # Create mock agents
        self.agent.denial_classifier = MagicMock()
        self.agent.remediation_advisor = MagicMock()
        
        # Configure classifier mock
        self.agent.denial_classifier.classify_denial.return_value = {
            "denial_type": "authorization_issue"
        }
        
        # Configure advisor mock
        self.agent.remediation_advisor.get_remediation_steps.return_value = {
            "steps": [
                "Contact the insurer to verify authorization requirements",
                "Submit authorization request with clinical documentation"
            ],
            "documentation_requirements": ["Patient demographics", "Clinical notes"],
            "references": ["Payer policy ABC123"]
        }
        
        # Create context with CARC code but no denial type
        context = {
            "carc_code": "50"
        }
        
        # Call the handler
        result = self.agent._handle_remediation_advice(context)
        
        # Should call classify_denial since we have CARC but no denial type
        self.agent.denial_classifier.classify_denial.assert_called_with(
            carc_code="50",
            rarc_code=None
        )
        
        # Should call get_remediation_steps with the classified denial type
        self.agent.remediation_advisor.get_remediation_steps.assert_called_with(
            denial_type="authorization_issue",
            carc_code="50",
            rarc_code=None,
            claim_details={}
        )
        
        # Should return a response with formatted steps
        assert "response" in result
        assert "STEPS TO RESOLVE:" in result["response"]
        assert "Contact the insurer" in result["response"]
        assert "Submit authorization request" in result["response"]
        assert "REQUIRED DOCUMENTATION:" in result["response"]
        assert "REFERENCES:" in result["response"]
        
        # Should return remediation details
        assert len(result["remediation_steps"]) == 2
        assert len(result["documentation_requirements"]) == 2
        assert len(result["references"]) == 1
        assert result["remediation_provided"] is True
