"""
Sequential Workflow System

This module implements the workflow system for the Medical Billing Denial Agent,
defining the sequential steps and transitions for handling denial resolution.

Features:
- Workflow state definitions
- Transition rules and conditions
- Branching logic based on denial types
- Performance monitoring
"""

import enum
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class WorkflowState(enum.Enum):
    """
    Enumeration of possible workflow states in the denial management process.
    
    These states represent the different stages a user might go through when
    resolving a denial, from initial greeting to final resolution.
    """
    # Initial states
    INITIALIZE = "initialize"
    GREETING = "greeting"
    
    # Information gathering states
    COLLECTING_INFO = "collecting_info"
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_PROCESSING = "document_processing"
    
    # Analysis states
    IDENTIFYING_DENIAL_TYPE = "identifying_denial_type"
    ANALYZING_CLAIM = "analyzing_claim"
    ANALYZING_EOB = "analyzing_eob"
    ANALYZING_DENIAL_CODES = "analyzing_denial_codes"
    
    # Resolution states
    GENERATING_REMEDIATION = "generating_remediation"
    PROVIDING_REMEDIATION = "providing_remediation"
    CHECKING_CODE_COMPATIBILITY = "checking_code_compatibility"
    SUGGESTING_ALTERNATIVES = "suggesting_alternatives"
    
    # Follow-up states
    ANSWERING_QUESTIONS = "answering_questions"
    EXPLAINING_RESOLUTION = "explaining_resolution"
    PROVIDING_REFERENCES = "providing_references"
    
    # Closing states
    CONFIRMING_UNDERSTANDING = "confirming_understanding"
    CLOSING = "closing"
    
    # Error states
    ERROR_HANDLING = "error_handling"
    FALLBACK = "fallback"


@dataclass
class Transition:
    """
    Defines a possible transition between workflow states.
    
    A transition includes the target state, any conditions that must be met,
    and actions to perform during the transition.
    """
    target_state: WorkflowState
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    actions: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = field(default_factory=list)
    description: str = ""
    
    def can_transition(self, context: Dict[str, Any]) -> bool:
        """
        Check if this transition is valid given the current context.
        
        Args:
            context: The current context
            
        Returns:
            True if the transition is valid, False otherwise
        """
        if self.condition is None:
            return True
        
        try:
            return self.condition(context)
        except Exception as e:
            logger.error(f"Error evaluating transition condition: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the actions associated with this transition.
        
        Args:
            context: The current context
            
        Returns:
            Updated context after executing actions
        """
        updated_context = context.copy()
        
        for action in self.actions:
            try:
                action_result = action(updated_context)
                if isinstance(action_result, dict):
                    updated_context.update(action_result)
            except Exception as e:
                logger.error(f"Error executing transition action: {e}")
                # Add error information to context
                if "errors" not in updated_context:
                    updated_context["errors"] = []
                updated_context["errors"].append({
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "transition": self.target_state.value,
                    "timestamp": time.time()
                })
        
        return updated_context


class WorkflowDefinition:
    """
    Defines a complete workflow with states and transitions.
    
    This class manages the states, transitions, and execution of a workflow,
    tracking progress and handling state changes.
    """
    
    def __init__(self, 
                 initial_state: WorkflowState = WorkflowState.INITIALIZE,
                 final_states: Optional[Set[WorkflowState]] = None):
        """
        Initialize the workflow definition.
        
        Args:
            initial_state: The starting state for the workflow
            final_states: Optional set of states that represent workflow completion
        """
        self.initial_state = initial_state
        self.transitions = {}  # Dict from state to list of possible transitions
        
        # Default final states if none provided
        if final_states is None:
            self.final_states = {WorkflowState.CLOSING}
        else:
            self.final_states = final_states
        
        # Performance tracking
        self.state_timing = {}  # Dict to track time spent in each state
        self.transition_counts = {}  # Dict to track transition frequencies
        
    def add_transition(self, from_state: WorkflowState,
                      transition: Transition) -> 'WorkflowDefinition':
        """
        Add a transition to the workflow.
        
        Args:
            from_state: The state this transition starts from
            transition: The transition definition
            
        Returns:
            Self for method chaining
        """
        if from_state not in self.transitions:
            self.transitions[from_state] = []
            
        self.transitions[from_state].append(transition)
        return self
    
    def get_valid_transitions(self, current_state: WorkflowState,
                            context: Dict[str, Any]) -> List[Transition]:
        """
        Get all valid transitions from the current state.
        
        Args:
            current_state: The current workflow state
            context: The current context
            
        Returns:
            List of valid transitions
        """
        if current_state not in self.transitions:
            logger.warning(f"No transitions defined for state: {current_state}")
            return []
            
        valid_transitions = []
        for transition in self.transitions[current_state]:
            if transition.can_transition(context):
                valid_transitions.append(transition)
                
        return valid_transitions
    
    def is_final_state(self, state: WorkflowState) -> bool:
        """
        Check if a state is a final (terminal) state.
        
        Args:
            state: The state to check
            
        Returns:
            True if the state is a final state, False otherwise
        """
        return state in self.final_states


class WorkflowEngine:
    """
    Engine for executing and tracking workflow progress.
    
    This class manages the execution of a workflow, tracking the current state
    and handling transitions based on context.
    """
    
    def __init__(self, workflow_definition: WorkflowDefinition):
        """
        Initialize the workflow engine.
        
        Args:
            workflow_definition: The workflow definition to execute
        """
        self.workflow = workflow_definition
        self.current_state = workflow_definition.initial_state
        self.workflow_history = []
        self.state_entry_time = time.time()
        
    def get_current_state(self) -> WorkflowState:
        """
        Get the current workflow state.
        
        Returns:
            The current workflow state
        """
        return self.current_state
    
    def is_complete(self) -> bool:
        """
        Check if the workflow is in a final state.
        
        Returns:
            True if the workflow is complete, False otherwise
        """
        return self.workflow.is_final_state(self.current_state)
    
    def process(self, context: Dict[str, Any]) -> Tuple[WorkflowState, Dict[str, Any], List[Transition]]:
        """
        Process the current state and determine the next state.
        
        Args:
            context: The current context
            
        Returns:
            Tuple of (new_state, updated_context, valid_transitions)
        """
        # Record time spent in current state
        time_in_state = time.time() - self.state_entry_time
        if self.current_state.value not in self.workflow.state_timing:
            self.workflow.state_timing[self.current_state.value] = []
        self.workflow.state_timing[self.current_state.value].append(time_in_state)
        
        # Get valid transitions from current state
        valid_transitions = self.workflow.get_valid_transitions(self.current_state, context)
        
        # If we have valid transitions, take the first one
        if valid_transitions:
            selected_transition = valid_transitions[0]
            
            # Track transition frequency
            transition_key = f"{self.current_state.value}->{selected_transition.target_state.value}"
            self.workflow.transition_counts[transition_key] = \
                self.workflow.transition_counts.get(transition_key, 0) + 1
            
            # Add to history
            self.workflow_history.append({
                "from_state": self.current_state.value,
                "to_state": selected_transition.target_state.value,
                "timestamp": time.time(),
                "time_in_state": time_in_state
            })
            
            # Execute transition actions
            updated_context = selected_transition.execute(context)
            
            # Update current state
            self.current_state = selected_transition.target_state
            self.state_entry_time = time.time()
            
            # Add current state to context
            updated_context["workflow_state"] = self.current_state.value
            
            return self.current_state, updated_context, valid_transitions
        else:
            # No valid transitions, staying in current state
            logger.warning(f"No valid transitions from state: {self.current_state}")
            
            # Add current state to context
            updated_context = context.copy()
            updated_context["workflow_state"] = self.current_state.value
            
            return self.current_state, updated_context, []
    
    def force_transition(self, target_state: WorkflowState, 
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Force a transition to a specific state, bypassing conditions.
        
        This is useful for handling exceptions or manual intervention.
        
        Args:
            target_state: The state to transition to
            context: The current context
            
        Returns:
            Updated context
        """
        # Record time spent in current state
        time_in_state = time.time() - self.state_entry_time
        if self.current_state.value not in self.workflow.state_timing:
            self.workflow.state_timing[self.current_state.value] = []
        self.workflow.state_timing[self.current_state.value].append(time_in_state)
        
        # Add to history with forced flag
        self.workflow_history.append({
            "from_state": self.current_state.value,
            "to_state": target_state.value,
            "timestamp": time.time(),
            "time_in_state": time_in_state,
            "forced": True
        })
        
        # Update current state
        self.current_state = target_state
        self.state_entry_time = time.time()
        
        # Track transition frequency
        transition_key = f"{self.current_state.value}->{target_state.value}(forced)"
        self.workflow.transition_counts[transition_key] = \
            self.workflow.transition_counts.get(transition_key, 0) + 1
        
        # Add current state to context
        updated_context = context.copy()
        updated_context["workflow_state"] = self.current_state.value
        updated_context["forced_transition"] = True
        
        return updated_context
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of workflow state transitions.
        
        Returns:
            List of transition records
        """
        return self.workflow_history
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about workflow execution.
        
        Returns:
            Dictionary with workflow metrics
        """
        # Calculate average time in each state
        avg_state_times = {}
        for state, times in self.workflow.state_timing.items():
            if times:
                avg_state_times[state] = sum(times) / len(times)
            else:
                avg_state_times[state] = 0
        
        return {
            "state_timing": self.workflow.state_timing,
            "average_state_times": avg_state_times,
            "transition_counts": self.workflow.transition_counts,
            "total_transitions": len(self.workflow_history),
            "current_state": self.current_state.value,
            "is_complete": self.is_complete()
        }


def build_denial_management_workflow() -> WorkflowDefinition:
    """
    Build the standard workflow for denial management.
    
    This function defines the states and transitions for the denial management
    workflow, including conditions and actions for each transition.
    
    Returns:
        Configured WorkflowDefinition
    """
    workflow = WorkflowDefinition(
        initial_state=WorkflowState.INITIALIZE,
        final_states={WorkflowState.CLOSING, WorkflowState.ERROR_HANDLING}
    )
    
    # Define some common transition conditions
    def has_documents(context: Dict[str, Any]) -> bool:
        """Check if documents are present in the context."""
        return bool(context.get("documents"))
    
    def has_denial_codes(context: Dict[str, Any]) -> bool:
        """Check if denial codes are present in the context."""
        return bool(context.get("carc_code") or context.get("rarc_code") or context.get("denial_codes"))
    
    def has_denial_type(context: Dict[str, Any]) -> bool:
        """Check if a denial type has been identified."""
        return bool(context.get("denial_type"))
    
    def needs_code_compatibility_check(context: Dict[str, Any]) -> bool:
        """Check if code compatibility needs to be verified."""
        denial_type = context.get("denial_type", "").lower()
        return "bundling" in denial_type or "compatibility" in denial_type or "mutually exclusive" in denial_type
    
    def remediation_provided(context: Dict[str, Any]) -> bool:
        """Check if remediation steps have been provided."""
        return bool(context.get("remediation_provided"))
    
    def is_closing(context: Dict[str, Any]) -> bool:
        """Check if the conversation is ending."""
        last_message = ""
        history = context.get("conversation_history", [])
        if history:
            last_message = history[-1].get("user_input", "").lower()
        
        return any(term in last_message for term in ["thanks", "thank you", "bye", "goodbye", "exit"])
    
    # Define some common transition actions
    def log_state_transition(context: Dict[str, Any]) -> Dict[str, Any]:
        """Log the state transition."""
        logger.info(f"Workflow transitioning to state: {context.get('workflow_state')}")
        return {}
    
    def update_conversation_state(context: Dict[str, Any]) -> Dict[str, Any]:
        """Update the conversation state in the context."""
        workflow_state = context.get("workflow_state")
        
        # Map workflow states to conversation states
        state_mapping = {
            WorkflowState.GREETING.value: "greeting",
            WorkflowState.COLLECTING_INFO.value: "collecting_info",
            WorkflowState.DOCUMENT_PROCESSING.value: "document_processing",
            WorkflowState.ANALYZING_DENIAL_CODES.value: "analyzing_denial",
            WorkflowState.PROVIDING_REMEDIATION.value: "providing_remediation",
            WorkflowState.ANSWERING_QUESTIONS.value: "answering_questions",
            WorkflowState.CLOSING.value: "closing"
        }
        
        if workflow_state in state_mapping:
            return {"conversation_state": state_mapping[workflow_state]}
        return {}
    
    # Add transitions for each state
    
    # Transitions from INITIALIZE
    workflow.add_transition(
        WorkflowState.INITIALIZE,
        Transition(
            target_state=WorkflowState.GREETING,
            actions=[log_state_transition, update_conversation_state],
            description="Start the conversation with a greeting"
        )
    )
    
    # Transitions from GREETING
    workflow.add_transition(
        WorkflowState.GREETING,
        Transition(
            target_state=WorkflowState.COLLECTING_INFO,
            actions=[log_state_transition, update_conversation_state],
            description="Move to collecting information about the denial"
        )
    )
    
    # Transitions from COLLECTING_INFO
    workflow.add_transition(
        WorkflowState.COLLECTING_INFO,
        Transition(
            target_state=WorkflowState.DOCUMENT_UPLOAD,
            condition=lambda ctx: "upload" in ctx.get("last_query", "").lower(),
            actions=[log_state_transition],
            description="User wants to upload a document"
        )
    )
    
    workflow.add_transition(
        WorkflowState.COLLECTING_INFO,
        Transition(
            target_state=WorkflowState.ANALYZING_DENIAL_CODES,
            condition=has_denial_codes,
            actions=[log_state_transition, update_conversation_state],
            description="Denial codes have been provided, analyze them"
        )
    )
    
    # Transitions from DOCUMENT_UPLOAD
    workflow.add_transition(
        WorkflowState.DOCUMENT_UPLOAD,
        Transition(
            target_state=WorkflowState.DOCUMENT_PROCESSING,
            condition=has_documents,
            actions=[log_state_transition, update_conversation_state],
            description="Documents have been uploaded, process them"
        )
    )
    
    # Transitions from DOCUMENT_PROCESSING
    workflow.add_transition(
        WorkflowState.DOCUMENT_PROCESSING,
        Transition(
            target_state=WorkflowState.ANALYZING_CLAIM,
            condition=lambda ctx: any("cms1500" in doc.get("document_type", "").lower() for doc in ctx.get("documents", [])),
            actions=[log_state_transition],
            description="CMS-1500 form detected, analyze claim"
        )
    )
    
    workflow.add_transition(
        WorkflowState.DOCUMENT_PROCESSING,
        Transition(
            target_state=WorkflowState.ANALYZING_EOB,
            condition=lambda ctx: any("eob" in doc.get("document_type", "").lower() for doc in ctx.get("documents", [])),
            actions=[log_state_transition],
            description="EOB detected, analyze EOB"
        )
    )
    
    # Transitions from ANALYZING_CLAIM
    workflow.add_transition(
        WorkflowState.ANALYZING_CLAIM,
        Transition(
            target_state=WorkflowState.ANALYZING_DENIAL_CODES,
            condition=has_denial_codes,
            actions=[log_state_transition, update_conversation_state],
            description="Denial codes extracted from claim, analyze them"
        )
    )
    
    workflow.add_transition(
        WorkflowState.ANALYZING_CLAIM,
        Transition(
            target_state=WorkflowState.COLLECTING_INFO,
            actions=[log_state_transition, update_conversation_state],
            description="Need more information about the denial"
        )
    )
    
    # Transitions from ANALYZING_EOB
    workflow.add_transition(
        WorkflowState.ANALYZING_EOB,
        Transition(
            target_state=WorkflowState.ANALYZING_DENIAL_CODES,
            condition=has_denial_codes,
            actions=[log_state_transition, update_conversation_state],
            description="Denial codes extracted from EOB, analyze them"
        )
    )
    
    # Transitions from ANALYZING_DENIAL_CODES
    workflow.add_transition(
        WorkflowState.ANALYZING_DENIAL_CODES,
        Transition(
            target_state=WorkflowState.IDENTIFYING_DENIAL_TYPE,
            actions=[log_state_transition],
            description="Identify the type of denial"
        )
    )
    
    # Transitions from IDENTIFYING_DENIAL_TYPE
    workflow.add_transition(
        WorkflowState.IDENTIFYING_DENIAL_TYPE,
        Transition(
            target_state=WorkflowState.CHECKING_CODE_COMPATIBILITY,
            condition=needs_code_compatibility_check,
            actions=[log_state_transition],
            description="Check code compatibility for bundling issues"
        )
    )
    
    workflow.add_transition(
        WorkflowState.IDENTIFYING_DENIAL_TYPE,
        Transition(
            target_state=WorkflowState.GENERATING_REMEDIATION,
            condition=has_denial_type,
            actions=[log_state_transition],
            description="Generate remediation steps for the identified denial type"
        )
    )
    
    # Transitions from CHECKING_CODE_COMPATIBILITY
    workflow.add_transition(
        WorkflowState.CHECKING_CODE_COMPATIBILITY,
        Transition(
            target_state=WorkflowState.SUGGESTING_ALTERNATIVES,
            condition=lambda ctx: bool(ctx.get("incompatible_codes")),
            actions=[log_state_transition],
            description="Suggest alternative codes for incompatible ones"
        )
    )
    
    workflow.add_transition(
        WorkflowState.CHECKING_CODE_COMPATIBILITY,
        Transition(
            target_state=WorkflowState.GENERATING_REMEDIATION,
            actions=[log_state_transition],
            description="Generate remediation steps"
        )
    )
    
    # Transitions from SUGGESTING_ALTERNATIVES
    workflow.add_transition(
        WorkflowState.SUGGESTING_ALTERNATIVES,
        Transition(
            target_state=WorkflowState.GENERATING_REMEDIATION,
            actions=[log_state_transition],
            description="Generate remediation steps with alternative codes"
        )
    )
    
    # Transitions from GENERATING_REMEDIATION
    workflow.add_transition(
        WorkflowState.GENERATING_REMEDIATION,
        Transition(
            target_state=WorkflowState.PROVIDING_REMEDIATION,
            actions=[
                log_state_transition, 
                update_conversation_state,
                lambda ctx: {"remediation_provided": True}
            ],
            description="Provide remediation steps to the user"
        )
    )
    
    # Transitions from PROVIDING_REMEDIATION
    workflow.add_transition(
        WorkflowState.PROVIDING_REMEDIATION,
        Transition(
            target_state=WorkflowState.ANSWERING_QUESTIONS,
            actions=[log_state_transition, update_conversation_state],
            description="Answer follow-up questions about remediation"
        )
    )
    
    # Transitions from ANSWERING_QUESTIONS
    workflow.add_transition(
        WorkflowState.ANSWERING_QUESTIONS,
        Transition(
            target_state=WorkflowState.PROVIDING_REFERENCES,
            condition=lambda ctx: "reference" in ctx.get("last_query", "").lower(),
            actions=[log_state_transition],
            description="Provide references for remediation steps"
        )
    )
    
    workflow.add_transition(
        WorkflowState.ANSWERING_QUESTIONS,
        Transition(
            target_state=WorkflowState.EXPLAINING_RESOLUTION,
            condition=lambda ctx: any(term in ctx.get("last_query", "").lower() for term in ["why", "how", "explain"]),
            actions=[log_state_transition],
            description="Explain the resolution in more detail"
        )
    )
    
    workflow.add_transition(
        WorkflowState.ANSWERING_QUESTIONS,
        Transition(
            target_state=WorkflowState.CONFIRMING_UNDERSTANDING,
            condition=lambda ctx: "understand" in ctx.get("last_query", "").lower(),
            actions=[log_state_transition],
            description="Confirm user's understanding of the remediation"
        )
    )
    
    workflow.add_transition(
        WorkflowState.ANSWERING_QUESTIONS,
        Transition(
            target_state=WorkflowState.CLOSING,
            condition=is_closing,
            actions=[log_state_transition, update_conversation_state],
            description="End the conversation"
        )
    )
    
    # Transitions from PROVIDING_REFERENCES
    workflow.add_transition(
        WorkflowState.PROVIDING_REFERENCES,
        Transition(
            target_state=WorkflowState.ANSWERING_QUESTIONS,
            actions=[log_state_transition, update_conversation_state],
            description="Return to answering questions"
        )
    )
    
    # Transitions from EXPLAINING_RESOLUTION
    workflow.add_transition(
        WorkflowState.EXPLAINING_RESOLUTION,
        Transition(
            target_state=WorkflowState.ANSWERING_QUESTIONS,
            actions=[log_state_transition, update_conversation_state],
            description="Return to answering questions"
        )
    )
    
    # Transitions from CONFIRMING_UNDERSTANDING
    workflow.add_transition(
        WorkflowState.CONFIRMING_UNDERSTANDING,
        Transition(
            target_state=WorkflowState.ANSWERING_QUESTIONS,
            actions=[log_state_transition, update_conversation_state],
            description="Return to answering questions"
        )
    )
    
    workflow.add_transition(
        WorkflowState.CONFIRMING_UNDERSTANDING,
        Transition(
            target_state=WorkflowState.CLOSING,
            condition=is_closing,
            actions=[log_state_transition, update_conversation_state],
            description="End the conversation"
        )
    )
    
    # Add error transitions from all states to ERROR_HANDLING
    for state in WorkflowState:
        if state != WorkflowState.ERROR_HANDLING and state != WorkflowState.FALLBACK:
            workflow.add_transition(
                state,
                Transition(
                    target_state=WorkflowState.ERROR_HANDLING,
                    condition=lambda ctx: bool(ctx.get("errors")),
                    actions=[log_state_transition],
                    description="Handle error condition"
                )
            )
    
    # Add fallback transitions from all states to FALLBACK
    for state in WorkflowState:
        if state != WorkflowState.ERROR_HANDLING and state != WorkflowState.FALLBACK:
            workflow.add_transition(
                state,
                Transition(
                    target_state=WorkflowState.FALLBACK,
                    condition=lambda ctx: ctx.get("fallback_triggered", False),
                    actions=[log_state_transition],
                    description="Fall back to general handling when no other transitions apply"
                )
            )
    
    # Transitions from ERROR_HANDLING
    workflow.add_transition(
        WorkflowState.ERROR_HANDLING,
        Transition(
            target_state=WorkflowState.COLLECTING_INFO,
            actions=[
                log_state_transition, 
                update_conversation_state,
                lambda ctx: {"errors": []}  # Clear errors
            ],
            description="Recover from error and continue collecting information"
        )
    )
    
    # Transitions from FALLBACK
    workflow.add_transition(
        WorkflowState.FALLBACK,
        Transition(
            target_state=WorkflowState.COLLECTING_INFO,
            actions=[
                log_state_transition, 
                update_conversation_state,
                lambda ctx: {"fallback_triggered": False}  # Reset fallback trigger
            ],
            description="Return to collecting information after fallback"
        )
    )
    
    return workflow


class SequentialAgent:
    """
    Agent that follows a sequential workflow to accomplish tasks.
    
    This agent coordinates the flow of conversation through a predefined
    workflow, routing tasks to specialized agents as needed based on the
    current workflow state.
    """
    
    def __init__(self, workflow_definition: Optional[WorkflowDefinition] = None):
        """
        Initialize the sequential agent.
        
        Args:
            workflow_definition: Optional custom workflow definition
        """
        # Use the standard workflow if none provided
        if workflow_definition is None:
            self.workflow_definition = build_denial_management_workflow()
        else:
            self.workflow_definition = workflow_definition
            
        self.workflow_engine = WorkflowEngine(self.workflow_definition)
        self.agent_handlers = {}
        logger.info("SequentialAgent initialized with workflow")
        
    def register_agent_handler(self, state: WorkflowState, handler_func):
        """
        Register an agent handler for a specific workflow state.
        
        Args:
            state: The workflow state to handle
            handler_func: Function that processes context and returns response
        """
        self.agent_handlers[state] = handler_func
        logger.info(f"Registered handler for state: {state}")
    
    def process_step(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the current workflow step.
        
        Args:
            context: The current context
            
        Returns:
            Updated context with response
        """
        start_time = time.time()
        
        # Process workflow to determine current state
        current_state, updated_context, valid_transitions = self.workflow_engine.process(context)
        
        # Check if we have a handler for this state
        if current_state in self.agent_handlers:
            handler = self.agent_handlers[current_state]
            
            try:
                # Call the handler with the context
                handler_start_time = time.time()
                response = handler(updated_context)
                handler_duration = time.time() - handler_start_time
                
                # Add performance metrics to response
                if isinstance(response, dict):
                    response["performance"] = response.get("performance", {})
                    response["performance"]["handler_duration"] = handler_duration
                    
                    # Merge the handler response with our context
                    updated_context.update(response)
                else:
                    logger.warning(f"Handler for state {current_state} did not return a dict")
                    
            except Exception as e:
                logger.error(f"Error handling state {current_state}: {e}")
                
                # Add error to context
                if "errors" not in updated_context:
                    updated_context["errors"] = []
                updated_context["errors"].append({
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "state": current_state.value,
                    "timestamp": time.time()
                })
                
                # Force transition to error handling
                updated_context = self.workflow_engine.force_transition(
                    WorkflowState.ERROR_HANDLING, updated_context
                )
        else:
            logger.warning(f"No handler registered for state: {current_state}")
        
        # Add workflow metrics to context
        updated_context["workflow_metrics"] = self.workflow_engine.get_workflow_metrics()
        updated_context["processing_time"] = time.time() - start_time
        
        return updated_context
    
    def reset_workflow(self) -> None:
        """
        Reset the workflow to its initial state.
        
        This method creates a new workflow engine with the current definition,
        effectively restarting the workflow from the beginning.
        """
        self.workflow_engine = WorkflowEngine(self.workflow_definition)
        logger.info("Workflow reset to initial state")
    
    def visualize_workflow(self) -> Dict[str, Any]:
        """
        Generate a visualization of the workflow.
        
        This method creates a dictionary representation of the workflow
        that can be used to visualize the states and transitions.
        
        Returns:
            Dictionary with workflow visualization data
        """
        states = {}
        transitions = []
        
        # Add all states
        for state in WorkflowState:
            states[state.value] = {
                "name": state.value,
                "is_initial": state == self.workflow_definition.initial_state,
                "is_final": self.workflow_definition.is_final_state(state),
                "outgoing_transitions": []
            }
            
        # Add all transitions
        for from_state, trans_list in self.workflow_definition.transitions.items():
            for transition in trans_list:
                transition_data = {
                    "from": from_state.value,
                    "to": transition.target_state.value,
                    "description": transition.description,
                    "has_condition": transition.condition is not None
                }
                transitions.append(transition_data)
                states[from_state.value]["outgoing_transitions"].append(transition.target_state.value)
                
        # Add metrics if available
        metrics = {}
        if hasattr(self.workflow_engine, 'workflow_history') and self.workflow_engine.workflow_history:
            metrics = self.workflow_engine.get_workflow_metrics()
            
        return {
            "states": states,
            "transitions": transitions,
            "metrics": metrics,
            "current_state": self.workflow_engine.current_state.value
        }
