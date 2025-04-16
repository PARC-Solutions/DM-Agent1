"""
Tests for the Sequential Agent implementation.

This module contains tests for the Sequential Agent pattern used to manage
workflow-based conversations in the Medical Billing Denial Agent.
"""

import pytest
from unittest.mock import MagicMock, patch, ANY
import time

from agent.core.sequential_agent import SequentialDenialAgent
from agent.core.workflow import WorkflowState, WorkflowDefinition, Transition
from agent.core.context_manager import ContextManager
from agent.core.message import MessageBus


class TestSequentialDenialAgent:
    """Tests for the SequentialDenialAgent class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a simple workflow for testing
        self.workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        
        # Add some transitions
        self.workflow.add_transition(
            WorkflowState.GREETING,
            Transition(
                target_state=WorkflowState.COLLECTING_INFO,
                condition=lambda ctx: True,  # Always valid
                actions=[lambda ctx: {"action_result": "executed"}],
                description="Test transition"
            )
        )
        
        self.workflow.add_transition(
            WorkflowState.COLLECTING_INFO,
            Transition(
                target_state=WorkflowState.DOCUMENT_UPLOAD,
                condition=lambda ctx: "upload" in ctx.get("last_query", "").lower(),
                description="Upload transition"
            )
        )
        
        # Create mock components
        self.context_manager = MagicMock(spec=ContextManager)
        self.context_manager.extract_agent_specific_context.return_value = {}
        
        self.message_bus = MagicMock(spec=MessageBus)
        
        # Create the sequential agent
        self.agent = SequentialDenialAgent(
            workflow_definition=self.workflow,
            context_manager=self.context_manager,
            message_bus_instance=self.message_bus
        )
    
    def test_initialization(self):
        """Test initialization of sequential agent."""
        assert self.agent.workflow_definition == self.workflow
        assert self.agent.context_manager == self.context_manager
        assert self.agent.message_bus == self.message_bus
        assert isinstance(self.agent.specialized_agents, dict)
        assert isinstance(self.agent.performance_metrics, dict)
    
    def test_register_specialized_agent(self):
        """Test registering specialized agents."""
        # Create mock handlers
        greeting_handler = MagicMock()
        collecting_handler = MagicMock()
        
        # Register handlers
        self.agent.register_specialized_agent(WorkflowState.GREETING, greeting_handler)
        self.agent.register_specialized_agent(WorkflowState.COLLECTING_INFO, collecting_handler)
        
        # Check they were registered
        assert self.agent.specialized_agents[WorkflowState.GREETING] == greeting_handler
        assert self.agent.specialized_agents[WorkflowState.COLLECTING_INFO] == collecting_handler
        
        # Check they're retrieved correctly
        assert self.agent._get_specialized_agent(WorkflowState.GREETING) == greeting_handler
        assert self.agent._get_specialized_agent(WorkflowState.COLLECTING_INFO) == collecting_handler
        assert self.agent._get_specialized_agent(WorkflowState.DOCUMENT_UPLOAD) is None
    
    def test_track_state_transition(self):
        """Test tracking state transitions."""
        # Track some transitions
        self.agent._track_state_transition("state1", "state2")
        self.agent._track_state_transition("state1", "state3")
        self.agent._track_state_transition("state1", "state2")  # Duplicate
        
        # Check tracking
        metrics = self.agent.performance_metrics["state_transitions"]
        assert metrics["state1->state2"] == 2
        assert metrics["state1->state3"] == 1
    
    def test_process_basic_workflow(self):
        """Test basic processing of a workflow."""
        # Register a mock specialized agent
        collecting_handler = MagicMock(return_value={"handler_result": "success"})
        self.agent.register_specialized_agent(WorkflowState.COLLECTING_INFO, collecting_handler)
        
        # Create an initial context
        context = {
            "session_id": "test123",
            "workflow_state": WorkflowState.GREETING.value
        }
        
        # Process a query
        result = self.agent.process("Hello", context)
        
        # Should transition to COLLECTING_INFO
        assert "workflow_state" in result
        assert result["workflow_state"] == WorkflowState.COLLECTING_INFO.value
        
        # Should have executed the transition action
        assert result["action_result"] == "executed"
        
        # Should have called specialized agent
        collecting_handler.assert_called_once()
        assert result["handler_result"] == "success"
        
        # Should have workflow metrics
        assert "workflow_metrics" in result
        assert "processing_time" in result
    
    def test_process_with_context_specific_agent(self):
        """Test processing with context-specific agent handling."""
        # Create an agent that extracts specific context
        self.context_manager.extract_agent_specific_context.return_value = {
            "agent_name": "collecting_info",
            "extracted_field": "extracted_value"
        }
        
        # Create a handler that uses the extracted context
        collecting_handler = MagicMock(return_value={
            "response": "Using extracted_value",
            "received_context": {"extracted_field": "extracted_value"}
        })
        self.agent.register_specialized_agent(WorkflowState.COLLECTING_INFO, collecting_handler)
        
        # Create an initial context
        context = {
            "session_id": "test123",
            "workflow_state": WorkflowState.GREETING.value,
            "full_field": "full_value"
        }
        
        # Process a query
        result = self.agent.process("Hello", context)
        
        # Check the handler was called with the extracted context
        self.context_manager.extract_agent_specific_context.assert_called_with(
            ANY, "collecting_info"
        )
        
        # Check the handler result was merged back
        assert result["response"] == "Using extracted_value"
        assert result["received_context"]["extracted_field"] == "extracted_value"
    
    def test_process_with_conditional_transition(self):
        """Test processing with a conditional transition."""
        # Create an initial context
        context = {
            "session_id": "test123",
            "workflow_state": WorkflowState.COLLECTING_INFO.value
        }
        
        # Process a query with upload keyword
        result = self.agent.process("I want to upload a document", context)
        
        # Should transition to DOCUMENT_UPLOAD
        assert result["workflow_state"] == WorkflowState.DOCUMENT_UPLOAD.value
        
        # Process a query without upload keyword
        result = self.agent.process("I have a question", context)
        
        # Should stay in COLLECTING_INFO
        assert result["workflow_state"] == WorkflowState.COLLECTING_INFO.value
    
    def test_process_with_no_specialized_agent(self):
        """Test processing when no specialized agent is available."""
        # Create an initial context
        context = {
            "session_id": "test123",
            "workflow_state": WorkflowState.DOCUMENT_UPLOAD.value
        }
        
        # Process with no registered handler
        result = self.agent.process("Process this", context)
        
        # Should still process but use default response
        assert "response" in result
        assert "Current workflow state: document_upload" in result["response"]
    
    def test_process_with_error_in_handler(self):
        """Test processing with an error in the specialized handler."""
        # Create a handler that raises an exception
        def failing_handler(context):
            raise ValueError("Test error")
        
        self.agent.register_specialized_agent(WorkflowState.COLLECTING_INFO, failing_handler)
        
        # Create an initial context
        context = {
            "session_id": "test123",
            "workflow_state": WorkflowState.GREETING.value
        }
        
        # Process should handle the error with fallback
        result = self.agent.process("Hello", context)
        
        # Should have fallback flag
        assert "fallback" in result
        assert result["fallback"] is True
        
        # Should have error information
        assert "error_message" in result
        assert "Test error" in result["error_message"]
        
        # Error should be tracked in metrics
        assert "ValueError" in self.agent.performance_metrics["errors"]
        assert self.agent.performance_metrics["errors"]["ValueError"] > 0
    
    def test_reset_workflow(self):
        """Test resetting the workflow."""
        # Create a context with workflow state and other fields
        context = {
            "session_id": "test123",
            "workflow_state": WorkflowState.DOCUMENT_UPLOAD.value,
            "fallback_triggered": True,
            "other_field": "value"
        }
        
        # Reset the workflow
        result = self.agent.reset_workflow(context)
        
        # Should have initial state and preserve other fields
        assert result["workflow_state"] == WorkflowState.GREETING.value
        assert "fallback_triggered" not in result
        assert result["other_field"] == "value"
    
    def test_get_performance_metrics(self):
        """Test getting performance metrics."""
        # Create some test data
        self.agent.performance_metrics["processing_times"] = [0.1, 0.2, 0.3]
        self.agent.performance_metrics["state_transitions"] = {"a->b": 1}
        self.agent.performance_metrics["specialized_agent_calls"] = {"agent1": 2}
        self.agent.performance_metrics["errors"] = {"ValueError": 1}
        
        # Get metrics
        metrics = self.agent.get_performance_metrics()
        
        # Check structure
        assert "processing_times" in metrics
        assert "state_transitions" in metrics
        assert "specialized_agent_calls" in metrics
        assert "errors" in metrics
        assert "workflow" in metrics
        assert "average_processing_time" in metrics
        
        # Check calculated values
        assert metrics["average_processing_time"] == 0.2
    
    def test_visualize_conversation_flow(self):
        """Test visualization of conversation flow."""
        # Create a context with history and state
        context = {
            "session_id": "test123",
            "workflow_state": WorkflowState.COLLECTING_INFO.value,
            "conversation_history": [
                {
                    "user_input": "Hello",
                    "agent_response": "Hi",
                    "metadata": {"workflow_state": WorkflowState.GREETING.value}
                },
                {
                    "user_input": "I need help",
                    "agent_response": "How can I help?",
                    "metadata": {"workflow_state": WorkflowState.COLLECTING_INFO.value}
                }
            ]
        }
        
        # Get visualization
        visualization = self.agent.visualize_conversation_flow(context)
        
        # Check structure
        assert "current_state" in visualization
        assert "conversation_states" in visualization
        assert "possible_next_states" in visualization
        
        # Check values
        assert visualization["current_state"] == WorkflowState.COLLECTING_INFO.value
        assert len(visualization["conversation_states"]) == 2
        assert len(visualization["possible_next_states"]) > 0
        
        # Check state history
        assert visualization["conversation_states"][0]["state"] == WorkflowState.GREETING.value
        assert visualization["conversation_states"][1]["state"] == WorkflowState.COLLECTING_INFO.value
