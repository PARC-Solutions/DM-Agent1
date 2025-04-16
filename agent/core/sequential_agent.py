"""
Sequential Agent Implementation

This module implements the Sequential Agent pattern for the Medical Billing Denial Agent,
which follows a structured workflow to process user requests, involving multiple specialized
agents in a predefined sequence.

Features:
- Workflow-based conversation flow
- Specialized agent integration
- Context sharing and state management
- Performance monitoring
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import copy

from agent.core.workflow import (
    WorkflowState, 
    WorkflowDefinition, 
    WorkflowEngine, 
    build_denial_management_workflow
)
from agent.core.context_manager import ContextManager
from agent.core.message import AgentMessage, MessageBus, message_bus
from agent.security.error_handler import (
    default_error_handler, 
    default_fallback_system,
    safe_execution_decorator
)

logger = logging.getLogger(__name__)

class SequentialDenialAgent:
    """
    Implementation of the Sequential Agent pattern for denial management.
    
    This agent orchestrates the workflow for processing denial management tasks,
    coordinating the interaction between specialized agents and maintaining
    context throughout the conversation.
    """
    
    def __init__(self, 
                 workflow_definition: Optional[WorkflowDefinition] = None,
                 context_manager: Optional[ContextManager] = None,
                 message_bus_instance: Optional[MessageBus] = None):
        """
        Initialize the Sequential Denial Agent.
        
        Args:
            workflow_definition: Optional custom workflow definition
            context_manager: Optional context manager
            message_bus_instance: Optional message bus
        """
        # Initialize components
        self.workflow_definition = workflow_definition or build_denial_management_workflow()
        self.workflow_engine = WorkflowEngine(self.workflow_definition)
        self.context_manager = context_manager or ContextManager()
        self.message_bus = message_bus_instance or message_bus
        
        # Store specialized agent handlers
        self.specialized_agents = {}
        
        # Track performance metrics
        self.performance_metrics = {
            "processing_times": [],  # List of processing times for each request
            "state_transitions": {},  # Count of transitions between states
            "specialized_agent_calls": {},  # Count of calls to each specialized agent
            "errors": {},  # Count of errors by type
        }
        
        # Configure with safe execution
        self._configure_safe_execution()
        
        logger.info("SequentialDenialAgent initialized with workflow")
    
    def _configure_safe_execution(self):
        """Configure safe execution with error handling and fallbacks."""
        # Register fallbacks for specialized agents
        for state in WorkflowState:
            component_name = f"agent_handler_{state.value}"
            default_fallback_system.register_fallback(
                component_name=component_name,
                fallback_func=self._fallback_for_state
            )
    
    def _fallback_for_state(self, error: Exception, args: Tuple) -> Dict[str, Any]:
        """
        Fallback handler for state processing errors.
        
        Args:
            error: The exception that occurred
            args: Original arguments to the handler
            
        Returns:
            Fallback result
        """
        context = args[0] if args else {}
        current_state = context.get("workflow_state", "unknown")
        
        # Track the error
        error_type = type(error).__name__
        if error_type not in self.performance_metrics["errors"]:
            self.performance_metrics["errors"][error_type] = 0
        self.performance_metrics["errors"][error_type] += 1
        
        # Create fallback response
        fallback_response = {
            "success": False,
            "fallback": True,
            "response": "I apologize, but I'm having trouble processing this part of the conversation. Let's try a different approach.",
            "error_message": str(error),
            "error_type": error_type,
            "state": current_state
        }
        
        # Force transition to a fallback state
        context["fallback_triggered"] = True
        
        return fallback_response
    
    def register_specialized_agent(self, state: WorkflowState, handler_func):
        """
        Register a specialized agent for a specific workflow state.
        
        Args:
            state: The workflow state
            handler_func: Function to process this state
        """
        self.specialized_agents[state] = handler_func
        logger.info(f"Registered specialized agent for state: {state.value}")
        
        # Initialize performance tracking
        agent_name = state.value
        if agent_name not in self.performance_metrics["specialized_agent_calls"]:
            self.performance_metrics["specialized_agent_calls"][agent_name] = 0
    
    def _get_specialized_agent(self, state: WorkflowState):
        """
        Get the specialized agent for a state.
        
        Args:
            state: The workflow state
            
        Returns:
            Handler function or None if not found
        """
        return self.specialized_agents.get(state)
    
    def _track_state_transition(self, from_state: str, to_state: str):
        """
        Track a state transition for performance metrics.
        
        Args:
            from_state: State transitioning from
            to_state: State transitioning to
        """
        transition_key = f"{from_state}->{to_state}"
        if transition_key not in self.performance_metrics["state_transitions"]:
            self.performance_metrics["state_transitions"][transition_key] = 0
        self.performance_metrics["state_transitions"][transition_key] += 1
    
    @safe_execution_decorator(component_name="sequential_agent_process")
    def process(self, query: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user query through the workflow.
        
        Args:
            query: The user's query
            session_context: Context from the current session
            
        Returns:
            Updated context with response
        """
        start_time = time.time()
        
        # Make a working copy of the context
        context = copy.deepcopy(session_context)
        
        # Add the query to context
        context["last_query"] = query
        
        # If we don't have a workflow state, start at the beginning
        if "workflow_state" not in context:
            context["workflow_state"] = self.workflow_definition.initial_state.value
        
        # Get current workflow state
        current_state_value = context["workflow_state"]
        
        # Process the workflow
        current_state = WorkflowState(current_state_value)
        new_state, updated_context, valid_transitions = self.workflow_engine.process(context)
        
        # Track the state transition
        if current_state != new_state:
            self._track_state_transition(current_state.value, new_state.value)
        
        # Get specialized agent for this state if available
        specialized_agent = self._get_specialized_agent(new_state)
        
        # Call the specialized agent if available
        if specialized_agent:
            # Extract context specific to this agent
            agent_name = new_state.value
            agent_context = self.context_manager.extract_agent_specific_context(
                updated_context, agent_name
            )
            
            # Track specialized agent call
            self.performance_metrics["specialized_agent_calls"][agent_name] = \
                self.performance_metrics["specialized_agent_calls"].get(agent_name, 0) + 1
            
            # Call specialized agent with safe execution
            component_name = f"agent_handler_{new_state.value}"
            agent_result, error = default_fallback_system.safe_execute(
                specialized_agent, 
                agent_context, 
                component_name=component_name
            )
            
            # Handle fallback if needed
            if error:
                # Error already tracked by fallback system
                # Just merge the fallback response
                updated_context.update(agent_result)
            else:
                # Agent executed successfully
                # Merge the result back into the main context
                if isinstance(agent_result, dict):
                    updated_context.update(agent_result)
        else:
            # No specialized agent, generate a basic response
            updated_context["response"] = (
                f"I'm processing your request related to denial management. "
                f"Current workflow state: {new_state.value}"
            )
            logger.warning(f"No specialized agent for state: {new_state.value}")
        
        # Add workflow metrics
        workflow_metrics = self.workflow_engine.get_workflow_metrics()
        updated_context["workflow_metrics"] = workflow_metrics
        
        # Add performance information
        processing_time = time.time() - start_time
        self.performance_metrics["processing_times"].append(processing_time)
        updated_context["processing_time"] = processing_time
        
        return updated_context
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get the agent's performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        metrics = copy.deepcopy(self.performance_metrics)
        
        # Add workflow metrics
        workflow_metrics = self.workflow_engine.get_workflow_metrics()
        metrics["workflow"] = workflow_metrics
        
        # Add average processing time
        if self.performance_metrics["processing_times"]:
            metrics["average_processing_time"] = (
                sum(self.performance_metrics["processing_times"]) / 
                len(self.performance_metrics["processing_times"])
            )
        else:
            metrics["average_processing_time"] = 0
        
        return metrics
    
    def reset_workflow(self, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reset the workflow to its initial state.
        
        Args:
            session_context: Current session context
            
        Returns:
            Updated context with workflow reset
        """
        # Create a new workflow engine
        self.workflow_engine = WorkflowEngine(self.workflow_definition)
        
        # Make a copy of the context
        updated_context = copy.deepcopy(session_context)
        
        # Set workflow state to initial
        updated_context["workflow_state"] = self.workflow_definition.initial_state.value
        
        # Clear any workflow-specific fields
        if "fallback_triggered" in updated_context:
            del updated_context["fallback_triggered"]
        
        return updated_context
    
    def visualize_conversation_flow(self, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visualization of the conversation flow.
        
        Args:
            session_context: Current session context
            
        Returns:
            Visualization data
        """
        # Get the current workflow state
        current_state_value = session_context.get(
            "workflow_state", 
            self.workflow_definition.initial_state.value
        )
        
        # Get conversation history
        conversation_history = session_context.get("conversation_history", [])
        
        # Build visualization data
        visualization = {
            "current_state": current_state_value,
            "conversation_states": [],
            "possible_next_states": []
        }
        
        # Add conversation history
        for turn in conversation_history:
            if "metadata" in turn and "workflow_state" in turn["metadata"]:
                visualization["conversation_states"].append({
                    "state": turn["metadata"]["workflow_state"],
                    "user_input": turn.get("user_input", ""),
                    "agent_response": turn.get("agent_response", "")
                })
        
        # Get possible next states
        current_state = WorkflowState(current_state_value)
        valid_transitions = self.workflow_definition.get_valid_transitions(
            current_state, session_context
        )
        
        for transition in valid_transitions:
            visualization["possible_next_states"].append({
                "state": transition.target_state.value,
                "description": transition.description,
                "has_condition": transition.condition is not None
            })
        
        return visualization


# Create a singleton instance for the default denial management workflow
default_sequential_agent = SequentialDenialAgent()
