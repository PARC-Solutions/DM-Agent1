"""
Tests for the workflow system.

This module contains tests for the workflow system that controls the conversation
flow in the Medical Billing Denial Agent.
"""

import pytest
from unittest.mock import MagicMock, patch
import time

from agent.core.workflow import (
    WorkflowState,
    WorkflowDefinition,
    WorkflowEngine,
    Transition,
    build_denial_management_workflow
)


class TestWorkflowDefinition:
    """Tests for the WorkflowDefinition class."""
    
    def test_initialization(self):
        """Test initialization of workflow definition."""
        workflow = WorkflowDefinition(
            initial_state=WorkflowState.GREETING,
            final_states={WorkflowState.CLOSING, WorkflowState.ERROR_HANDLING}
        )
        
        assert workflow.initial_state == WorkflowState.GREETING
        assert workflow.final_states == {WorkflowState.CLOSING, WorkflowState.ERROR_HANDLING}
        assert len(workflow.transitions) == 0
        
    def test_add_transition(self):
        """Test adding transitions to the workflow."""
        workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        
        # Define a mock condition and actions
        condition = MagicMock(return_value=True)
        action1 = MagicMock(return_value={})
        action2 = MagicMock(return_value={"key": "value"})
        
        # Add two transitions from GREETING
        workflow.add_transition(
            WorkflowState.GREETING,
            Transition(
                target_state=WorkflowState.COLLECTING_INFO,
                condition=condition,
                actions=[action1],
                description="Test transition 1"
            )
        )
        
        workflow.add_transition(
            WorkflowState.GREETING,
            Transition(
                target_state=WorkflowState.DOCUMENT_UPLOAD,
                actions=[action2],
                description="Test transition 2"
            )
        )
        
        # Check transitions were added
        assert len(workflow.transitions) == 1  # One source state
        assert len(workflow.transitions[WorkflowState.GREETING]) == 2  # Two transitions from GREETING
        assert workflow.transitions[WorkflowState.GREETING][0].target_state == WorkflowState.COLLECTING_INFO
        assert workflow.transitions[WorkflowState.GREETING][1].target_state == WorkflowState.DOCUMENT_UPLOAD
        
    def test_get_valid_transitions(self):
        """Test getting valid transitions based on conditions."""
        workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        
        # Define conditions that depend on context
        condition1 = lambda ctx: ctx.get("has_documents", False)
        condition2 = lambda ctx: ctx.get("has_codes", False)
        
        # Add transitions with conditions
        workflow.add_transition(
            WorkflowState.GREETING,
            Transition(
                target_state=WorkflowState.DOCUMENT_UPLOAD,
                condition=condition1,
                description="Document upload transition"
            )
        )
        
        workflow.add_transition(
            WorkflowState.GREETING,
            Transition(
                target_state=WorkflowState.ANALYZING_DENIAL_CODES,
                condition=condition2,
                description="Analyzing codes transition"
            )
        )
        
        # Test with empty context - no valid transitions
        context1 = {}
        valid1 = workflow.get_valid_transitions(WorkflowState.GREETING, context1)
        assert len(valid1) == 0
        
        # Test with documents - first transition valid
        context2 = {"has_documents": True}
        valid2 = workflow.get_valid_transitions(WorkflowState.GREETING, context2)
        assert len(valid2) == 1
        assert valid2[0].target_state == WorkflowState.DOCUMENT_UPLOAD
        
        # Test with codes - second transition valid
        context3 = {"has_codes": True}
        valid3 = workflow.get_valid_transitions(WorkflowState.GREETING, context3)
        assert len(valid3) == 1
        assert valid3[0].target_state == WorkflowState.ANALYZING_DENIAL_CODES
        
        # Test with both - both transitions valid
        context4 = {"has_documents": True, "has_codes": True}
        valid4 = workflow.get_valid_transitions(WorkflowState.GREETING, context4)
        assert len(valid4) == 2
        
    def test_is_final_state(self):
        """Test checking if a state is final."""
        workflow = WorkflowDefinition(
            initial_state=WorkflowState.GREETING,
            final_states={WorkflowState.CLOSING, WorkflowState.ERROR_HANDLING}
        )
        
        assert workflow.is_final_state(WorkflowState.CLOSING) is True
        assert workflow.is_final_state(WorkflowState.ERROR_HANDLING) is True
        assert workflow.is_final_state(WorkflowState.GREETING) is False
        assert workflow.is_final_state(WorkflowState.COLLECTING_INFO) is False


class TestTransition:
    """Tests for the Transition class."""
    
    def test_can_transition_no_condition(self):
        """Test transition with no condition."""
        transition = Transition(
            target_state=WorkflowState.COLLECTING_INFO,
            description="Test transition"
        )
        
        # Should return True with any context
        assert transition.can_transition({}) is True
        assert transition.can_transition({"some_key": "value"}) is True
    
    def test_can_transition_with_condition(self):
        """Test transition with condition."""
        # Condition that checks for a specific key
        condition = lambda ctx: ctx.get("required_key") == "required_value"
        
        transition = Transition(
            target_state=WorkflowState.COLLECTING_INFO,
            condition=condition,
            description="Test transition with condition"
        )
        
        # Should return False if condition not met
        assert transition.can_transition({}) is False
        assert transition.can_transition({"required_key": "wrong_value"}) is False
        
        # Should return True if condition met
        assert transition.can_transition({"required_key": "required_value"}) is True
    
    def test_execute_actions(self):
        """Test executing transition actions."""
        # Action that adds a key to context
        action1 = lambda ctx: {"action1_key": "action1_value"}
        
        # Action that modifies existing keys
        action2 = lambda ctx: {"counter": ctx.get("counter", 0) + 1}
        
        transition = Transition(
            target_state=WorkflowState.COLLECTING_INFO,
            actions=[action1, action2],
            description="Test transition with actions"
        )
        
        # Execute with empty context
        result1 = transition.execute({})
        assert result1["action1_key"] == "action1_value"
        assert result1["counter"] == 1
        
        # Execute with existing counter
        result2 = transition.execute({"counter": 5})
        assert result2["action1_key"] == "action1_value"
        assert result2["counter"] == 6
    
    def test_execute_with_error(self):
        """Test executing actions with an error."""
        # Action that raises an exception
        def failing_action(ctx):
            raise ValueError("Test error")
        
        transition = Transition(
            target_state=WorkflowState.ERROR_HANDLING,
            actions=[failing_action],
            description="Test transition with failing action"
        )
        
        # Execute should handle the error and continue
        result = transition.execute({})
        
        # Should have error information
        assert "errors" in result
        assert len(result["errors"]) == 1
        assert result["errors"][0]["error_type"] == "ValueError"
        assert result["errors"][0]["error_message"] == "Test error"
        assert result["errors"][0]["transition"] == WorkflowState.ERROR_HANDLING.value


class TestWorkflowEngine:
    """Tests for the WorkflowEngine class."""
    
    def test_initialization(self):
        """Test initialization of workflow engine."""
        workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        engine = WorkflowEngine(workflow)
        
        assert engine.workflow == workflow
        assert engine.current_state == WorkflowState.GREETING
        assert len(engine.workflow_history) == 0
    
    def test_get_current_state(self):
        """Test getting current state."""
        workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        engine = WorkflowEngine(workflow)
        
        assert engine.get_current_state() == WorkflowState.GREETING
    
    def test_is_complete(self):
        """Test checking if workflow is complete."""
        workflow = WorkflowDefinition(
            initial_state=WorkflowState.GREETING,
            final_states={WorkflowState.CLOSING}
        )
        engine = WorkflowEngine(workflow)
        
        # Should be False initially
        assert engine.is_complete() is False
        
        # Force to final state
        engine.current_state = WorkflowState.CLOSING
        assert engine.is_complete() is True
    
    def test_process_with_transition(self):
        """Test processing with a valid transition."""
        workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        
        # Add a transition
        workflow.add_transition(
            WorkflowState.GREETING,
            Transition(
                target_state=WorkflowState.COLLECTING_INFO,
                condition=lambda ctx: True,  # Always valid
                actions=[lambda ctx: {"action_executed": True}],
                description="Test transition"
            )
        )
        
        engine = WorkflowEngine(workflow)
        
        # Process with empty context
        new_state, updated_context, valid_transitions = engine.process({})
        
        # Should transition to new state
        assert new_state == WorkflowState.COLLECTING_INFO
        assert engine.current_state == WorkflowState.COLLECTING_INFO
        
        # Context should be updated with workflow state and action result
        assert updated_context["workflow_state"] == WorkflowState.COLLECTING_INFO.value
        assert updated_context["action_executed"] is True
        
        # Should have one valid transition
        assert len(valid_transitions) == 1
        
        # Should have history entry
        assert len(engine.workflow_history) == 1
        assert engine.workflow_history[0]["from_state"] == WorkflowState.GREETING.value
        assert engine.workflow_history[0]["to_state"] == WorkflowState.COLLECTING_INFO.value
    
    def test_process_no_valid_transitions(self):
        """Test processing with no valid transitions."""
        workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        
        # Add a transition with condition that's never met
        workflow.add_transition(
            WorkflowState.GREETING,
            Transition(
                target_state=WorkflowState.COLLECTING_INFO,
                condition=lambda ctx: False,  # Never valid
                description="Test transition that's never valid"
            )
        )
        
        engine = WorkflowEngine(workflow)
        
        # Process with empty context
        new_state, updated_context, valid_transitions = engine.process({})
        
        # Should stay in same state
        assert new_state == WorkflowState.GREETING
        assert engine.current_state == WorkflowState.GREETING
        
        # Context should have workflow state
        assert updated_context["workflow_state"] == WorkflowState.GREETING.value
        
        # Should have no valid transitions
        assert len(valid_transitions) == 0
        
        # Should not have history entry
        assert len(engine.workflow_history) == 0
    
    def test_force_transition(self):
        """Test forcing a transition."""
        workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        engine = WorkflowEngine(workflow)
        
        # Force transition to different state
        updated_context = engine.force_transition(WorkflowState.ERROR_HANDLING, {})
        
        # Should be in new state
        assert engine.current_state == WorkflowState.ERROR_HANDLING
        
        # Context should have workflow state and forced flag
        assert updated_context["workflow_state"] == WorkflowState.ERROR_HANDLING.value
        assert updated_context["forced_transition"] is True
        
        # Should have history entry with forced flag
        assert len(engine.workflow_history) == 1
        assert engine.workflow_history[0]["from_state"] == WorkflowState.GREETING.value
        assert engine.workflow_history[0]["to_state"] == WorkflowState.ERROR_HANDLING.value
        assert engine.workflow_history[0]["forced"] is True
    
    def test_get_workflow_metrics(self):
        """Test getting workflow metrics."""
        workflow = WorkflowDefinition(initial_state=WorkflowState.GREETING)
        
        # Add transitions to test metrics
        workflow.add_transition(
            WorkflowState.GREETING,
            Transition(
                target_state=WorkflowState.COLLECTING_INFO,
                condition=lambda ctx: True,
                description="First transition"
            )
        )
        
        workflow.add_transition(
            WorkflowState.COLLECTING_INFO,
            Transition(
                target_state=WorkflowState.DOCUMENT_UPLOAD,
                condition=lambda ctx: True,
                description="Second transition"
            )
        )
        
        engine = WorkflowEngine(workflow)
        
        # Process twice to create history
        engine.process({})
        time.sleep(0.1)  # Add delay to ensure state timing is measurable
        engine.process({})
        
        # Get metrics
        metrics = engine.get_workflow_metrics()
        
        # Check metric structure
        assert "state_timing" in metrics
        assert "average_state_times" in metrics
        assert "transition_counts" in metrics
        assert "total_transitions" in metrics
        assert "current_state" in metrics
        assert "is_complete" in metrics
        
        # Check values
        assert metrics["total_transitions"] == 2
        assert metrics["current_state"] == WorkflowState.DOCUMENT_UPLOAD.value
        assert metrics["is_complete"] is False
        
        # Should have timing for both states
        assert WorkflowState.GREETING.value in metrics["state_timing"]
        assert WorkflowState.COLLECTING_INFO.value in metrics["state_timing"]
        
        # Should have counts for both transitions
        transition1 = f"{WorkflowState.GREETING.value}->{WorkflowState.COLLECTING_INFO.value}"
        transition2 = f"{WorkflowState.COLLECTING_INFO.value}->{WorkflowState.DOCUMENT_UPLOAD.value}"
        assert metrics["transition_counts"][transition1] == 1
        assert metrics["transition_counts"][transition2] == 1


class TestDenialManagementWorkflow:
    """Tests for the denial management workflow builder."""
    
    def test_build_denial_management_workflow(self):
        """Test building the denial management workflow."""
        workflow = build_denial_management_workflow()
        
        # Check workflow configuration
        assert workflow.initial_state == WorkflowState.INITIALIZE
        assert WorkflowState.CLOSING in workflow.final_states
        assert WorkflowState.ERROR_HANDLING in workflow.final_states
        
        # Should have transitions for all states
        assert len(workflow.transitions) > 0
        
        # Check a few key transitions
        assert WorkflowState.INITIALIZE in workflow.transitions
        assert WorkflowState.GREETING in workflow.transitions
        assert WorkflowState.COLLECTING_INFO in workflow.transitions
        
        # Check that transitions are valid
        initialize_transitions = workflow.transitions[WorkflowState.INITIALIZE]
        assert len(initialize_transitions) > 0
        assert initialize_transitions[0].target_state == WorkflowState.GREETING
        
    def test_workflow_conditions(self):
        """Test conditions in the denial management workflow."""
        workflow = build_denial_management_workflow()
        
        # Test document condition
        doc_context = {"documents": ["doc1"]}
        no_doc_context = {}
        
        doc_transitions = workflow.get_valid_transitions(WorkflowState.DOCUMENT_UPLOAD, doc_context)
        no_doc_transitions = workflow.get_valid_transitions(WorkflowState.DOCUMENT_UPLOAD, no_doc_context)
        
        assert len(doc_transitions) > 0
        assert doc_transitions[0].target_state == WorkflowState.DOCUMENT_PROCESSING
        assert len(no_doc_transitions) == 0
        
        # Test denial code condition
        code_context = {"carc_code": "A123"}
        no_code_context = {}
        
        code_transitions = workflow.get_valid_transitions(WorkflowState.COLLECTING_INFO, code_context)
        
        has_analysis_transition = any(
            t.target_state == WorkflowState.ANALYZING_DENIAL_CODES for t in code_transitions
        )
        assert has_analysis_transition
        
    def test_workflow_actions(self):
        """Test actions in the denial management workflow."""
        workflow = build_denial_management_workflow()
        
        # Find a transition with update_conversation_state action
        greeting_transitions = workflow.transitions[WorkflowState.GREETING]
        greeting_to_collecting = greeting_transitions[0]
        
        # Execute the transition and check that conversation_state is updated
        result = greeting_to_collecting.execute({})
        assert "conversation_state" in result
        assert result["conversation_state"] == "collecting_info"
