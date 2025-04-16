"""
Denial Assistant Coordinator Agent

This module implements the main coordinator agent for the Medical Billing Denial Agent system.
It handles the conversation flow with users and coordinates with specialized sub-agents
for denial classification, claims analysis, and remediation advice.

Features:
- Structured conversation flow
- Task routing to specialized agents
- Session context management
- Professional response generation
"""

import logging
import os
import enum
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from agent.core.session_manager import SessionManager
from agent.classifiers.denial_classifier import DenialClassifierAgent
from agent.analyzers.claims_analyzer import ClaimsAnalyzerAgent
from agent.advisors.remediation_advisor import RemediationAdvisorAgent

logger = logging.getLogger(__name__)

class ConversationState(enum.Enum):
    """Enum representing the state of the conversation flow."""
    GREETING = "greeting"
    COLLECTING_INFO = "collecting_info"
    DOCUMENT_PROCESSING = "document_processing"
    ANALYZING_DENIAL = "analyzing_denial"
    PROVIDING_REMEDIATION = "providing_remediation"
    ANSWERING_QUESTIONS = "answering_questions"
    CLOSING = "closing"

class TaskType(enum.Enum):
    """Enum representing the type of tasks to route."""
    DENIAL_CLASSIFICATION = "denial_classification"
    CLAIM_ANALYSIS = "claim_analysis"
    REMEDIATION_ADVICE = "remediation_advice"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


class DenialAssistantAgent:
    """
    Main coordinator agent for the Medical Billing Denial Assistant.
    
    This agent handles direct user interactions, maintains conversation context,
    and delegates specialized tasks to sub-agents as needed.
    
    Features:
    - Structured conversation flow with state management
    - Intent detection for appropriate task routing
    - Context-aware response generation
    - Integration with specialized sub-agents
    
    Note: In a production environment, this would use the ADK's LLMAgent.
    This is a simplified implementation for development and testing.
    """
    
    def __init__(self, session_manager: SessionManager):
        """
        Initialize the Denial Assistant Coordinator Agent.
        
        Args:
            session_manager: Session manager for maintaining conversation context
        """
        logger.info("Initializing DenialAssistantAgent")
        
        self.session_manager = session_manager
        self.name = "medical_billing_denial_assistant"
        self.description = "Assists with resolving medical billing denials"
        
        # Get configuration from environment
        self.model_name = os.getenv("AGENT_MODEL", "gemini-2.0-pro")
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.2"))
        
        # Initialize specialized sub-agents (placeholders for now, will be properly implemented later)
        self.denial_classifier = None  # Will be initialized in Epic 5
        self.claims_analyzer = None    # Will be initialized in Epic 5
        self.remediation_advisor = None  # Will be initialized in Epic 5
        
        # Agent instructions
        self.instruction = """
        You are a helpful medical billing denial assistant.
        
        Help users understand why claims were denied and how to resolve them.
        Maintain a professional, factual tone and avoid speculating.
        Remember to follow all HIPAA regulations regarding PHI.
        
        For specific analyses of denial codes or claim documents, delegate to specialized agents.
        Always provide clear, actionable guidance that billing staff can follow.
        
        If you don't know something, say so clearly rather than making up information.
        When providing resolution steps, be specific and actionable.
        """
        
        # Define regex patterns for intent detection
        self.patterns = {
            "carc_rarc_codes": r'\b(carc|rarc)\s+code\s*:?\s*([A-Za-z0-9]+)',
            "denial_question": r'\b(why|reason|denied|rejection|denial)\b',
            "document_processing": r'\b(document|form|eob|cms|cms-?1500|upload)\b',
            "remediation": r'\b(how|resolve|fix|correct|appeal|resubmit|solution)\b',
            "greeting": r'\b(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))\b',
            "closing": r'\b(bye|goodbye|thank|thanks)\b',
        }
        
        logger.info(f"DenialAssistantAgent initialized with model: {self.model_name}, temperature: {self.temperature}")
    
    def _initialize_sub_agents(self):
        """Initialize the specialized sub-agents when needed."""
        logger.info("Initializing specialized sub-agents")
        
        # These will be properly implemented in Epic 5
        # For now, we'll initialize them as placeholders
        if not self.denial_classifier:
            self.denial_classifier = DenialClassifierAgent()
            
        if not self.claims_analyzer:
            self.claims_analyzer = ClaimsAnalyzerAgent()
            
        if not self.remediation_advisor:
            self.remediation_advisor = RemediationAdvisorAgent()
    
    def _content_moderation_callback(self, callback_context, llm_response):
        """
        Callback function to ensure responses comply with all requirements.
        
        This callback handles:
        - HIPAA compliance checks
        - Content safety filtering
        - Response formatting standardization
        
        Args:
            callback_context: Context of the callback
            llm_response: The response generated by the LLM
            
        Returns:
            str: The modified LLM response
        """
        logger.debug("Running content moderation callback")
        
        # This is a placeholder implementation that will be expanded in Epic 7
        # when we implement full HIPAA compliance and content moderation
        
        # Basic formatting standardization
        response = llm_response
        
        # Ensure response has proper structure with headers for steps
        if "steps" in callback_context and "STEPS TO RESOLVE:" not in response:
            # Format remediation steps with proper heading and numbers if needed
            if re.search(r'\b\d+\)\s', response) or re.search(r'\b\d+\.\s', response):
                # Already has numbered steps, just add header
                response = "STEPS TO RESOLVE:\n\n" + response
            else:
                # Try to identify steps and number them
                steps = re.split(r'\n(?=Step\s+\d+:|\b\d+\.|\b\d+\))', response)
                if len(steps) > 1:
                    response = "STEPS TO RESOLVE:\n\n" + response
        
        # Add disclaimer for medical information if needed
        if "medical_advice" in callback_context and "DISCLAIMER:" not in response:
            disclaimer = "\n\nDISCLAIMER: This guidance is for informational purposes only and does not constitute medical or legal advice. Please consult with appropriate healthcare professionals and/or legal counsel for specific situations."
            response += disclaimer
        
        return response
    
    def _detect_intent(self, query: str) -> Tuple[TaskType, Dict[str, Any]]:
        """
        Detect the user's intent from their query to route to appropriate handling.
        
        Args:
            query: The user's query
            
        Returns:
            Tuple containing the detected task type and any extracted information
        """
        extracted_info = {}
        
        # Check for CARC/RARC codes
        code_match = re.search(self.patterns["carc_rarc_codes"], query, re.IGNORECASE)
        if code_match:
            code_type, code_value = code_match.groups()
            extracted_info["code_type"] = code_type.upper()
            extracted_info["code_value"] = code_value
            return TaskType.DENIAL_CLASSIFICATION, extracted_info
            
        # Check for document processing intent
        if re.search(self.patterns["document_processing"], query, re.IGNORECASE):
            return TaskType.CLAIM_ANALYSIS, extracted_info
            
        # Check for remediation questions
        if re.search(self.patterns["remediation"], query, re.IGNORECASE):
            if re.search(self.patterns["denial_question"], query, re.IGNORECASE):
                return TaskType.REMEDIATION_ADVICE, extracted_info
                
        # Check for general denial questions
        if re.search(self.patterns["denial_question"], query, re.IGNORECASE):
            return TaskType.GENERAL_QUESTION, extracted_info
            
        # Default case - unknown intent
        return TaskType.UNKNOWN, extracted_info
    
    def _determine_conversation_state(self, session: Dict) -> ConversationState:
        """
        Determine the current state of the conversation based on session context.
        
        Args:
            session: The current session context
            
        Returns:
            ConversationState: The current conversation state
        """
        # Default state if nothing else matches
        state = ConversationState.GREETING
        
        # Check if we have a current state saved
        if "conversation_state" in session:
            try:
                state = ConversationState(session["conversation_state"])
            except ValueError:
                # Invalid state, reset to greeting
                state = ConversationState.GREETING
        else:
            # New conversation, check history length
            if len(session.get("conversation_history", [])) == 0:
                state = ConversationState.GREETING
            else:
                state = ConversationState.COLLECTING_INFO
                
        # Check for documents in processing
        if session.get("documents_processing", False):
            state = ConversationState.DOCUMENT_PROCESSING
            
        # Check if we're in the denial analysis phase
        if session.get("denial_codes") and not session.get("remediation_provided"):
            state = ConversationState.ANALYZING_DENIAL
            
        # Check if we're in remediation phase
        if session.get("remediation_provided"):
            state = ConversationState.ANSWERING_QUESTIONS
            
        return state
    
    def _update_conversation_state(self, session_id: str, state: ConversationState) -> None:
        """
        Update the conversation state in the session.
        
        Args:
            session_id: The session ID
            state: The new conversation state
        """
        self.session_manager.update_session(
            session_id=session_id,
            context_updates={"conversation_state": state.value}
        )
    
    def _format_response(self, response_type: str, content: str) -> str:
        """
        Format a response according to standards for different response types.
        
        Args:
            response_type: The type of response (greeting, instruction, analysis, etc.)
            content: The raw response content
            
        Returns:
            str: Properly formatted response
        """
        formatted_response = content
        
        if response_type == "greeting":
            if not content.startswith("Welcome"):
                formatted_response = "Welcome to the Medical Billing Denial Assistant. " + content
                
        elif response_type == "denial_analysis":
            if "DENIAL ANALYSIS:" not in content:
                formatted_response = "DENIAL ANALYSIS:\n\n" + content
                
        elif response_type == "remediation":
            if "STEPS TO RESOLVE:" not in content:
                # Check if content already has numbered steps
                if re.search(r'\b\d+\)\s', content) or re.search(r'\b\d+\.\s', content):
                    formatted_response = "STEPS TO RESOLVE:\n\n" + content
                else:
                    # Format steps with numbers
                    steps = content.split("\n")
                    formatted_steps = []
                    step_num = 1
                    
                    for step in steps:
                        if step.strip():
                            if not step.startswith(f"{step_num}.") and not step.startswith(f"{step_num})"):
                                formatted_steps.append(f"{step_num}. {step}")
                                step_num += 1
                            else:
                                formatted_steps.append(step)
                                
                    formatted_response = "STEPS TO RESOLVE:\n\n" + "\n".join(formatted_steps)
        
        return formatted_response
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a response to a prompt using the language model.
        
        This is a structured response generator that uses context and templates
        while simulating what would be handled by the ADK's LLMAgent in production.
        
        Args:
            prompt: The input prompt for the model
            context: Optional context information to guide response generation
            
        Returns:
            str: The generated response
        """
        logger.info(f"Generating response for prompt: {prompt[:50]}...")
        
        # In a real implementation, this would call an actual LLM
        # For this development version, we'll use structured templates
        
        # Set defaults
        context = context or {}
        state = context.get("conversation_state", ConversationState.GREETING)
        response_type = "general"
        
        # Greeting state responses
        if state == ConversationState.GREETING:
            response_type = "greeting"
            return self._format_response(response_type, 
                "I'm here to help with medical billing denial resolution. "
                "To assist you effectively, I'll need information about the denial. "
                "You can provide CARC/RARC codes, share claim details, or upload denial documentation like EOBs or CMS-1500 forms. "
                "How can I help with your denial today?"
            )
        
        # Handle intent-based responses
        if "carc_code" in context or "rarc_code" in context or "carc code" in prompt.lower() or "rarc code" in prompt.lower():
            response_type = "denial_analysis"
            return self._format_response(response_type,
                "CARC codes are Claim Adjustment Reason Codes that explain why a claim was adjusted or denied. "
                "Each code has a specific meaning related to payment decisions. "
                f"{'For specific code information, please provide the code number.' if 'code_value' not in context else ''}\n\n"
                f"{'Based on the codes you provided, this denial appears to be related to: [Explanation would be provided by classifier agent in full implementation]' if 'code_value' in context else ''}"
            )
            
        elif "document" in context or any(doc_term in prompt.lower() for doc_term in ["document", "upload", "cms1500", "eob"]):
            return "I can analyze claim documents like CMS-1500 forms and EOBs to identify potential issues. " \
                   "When you upload these documents, I'll extract key information and look for problems that might have caused the denial. " \
                   "Would you like to upload a document now?"
            
        elif re.search(self.patterns["remediation"], prompt.lower()):
            response_type = "remediation"
            return self._format_response(response_type,
                "To resolve this denial, I recommend following these steps:\n\n"
                "1. Review the specific denial reason from the CARC/RARC codes\n"
                "2. Gather all relevant documentation for the claim\n"
                "3. Check for common errors such as missing information or coding issues\n"
                "4. Make the necessary corrections based on the specific denial reason\n"
                "5. Resubmit the claim with appropriate supporting documentation\n\n"
                "For more specific guidance, please provide the denial codes or upload the EOB document."
            )
            
        else:
            # Default response for general questions
            return "I'm here to help with medical billing denials. To provide specific assistance, please share more details about your denial, such as the CARC/RARC codes or the explanation provided by the payer. You can also upload claim documents like CMS-1500 forms or EOBs for analysis."
    
    def _route_to_specialized_agent(self, task_type: TaskType, query: str, context: Dict[str, Any]) -> str:
        """
        Route a task to the appropriate specialized agent.
        
        Args:
            task_type: The type of task to route
            query: The user's query
            context: The session context
            
        Returns:
            str: The response from the specialized agent
        """
        # Initialize sub-agents if not already done
        self._initialize_sub_agents()
        
        if task_type == TaskType.DENIAL_CLASSIFICATION:
            # Extract CARC/RARC codes if present
            carc_code = context.get("carc_code")
            rarc_code = context.get("rarc_code")
            
            if not carc_code and "code_value" in context and context.get("code_type") == "CARC":
                carc_code = context["code_value"]
                
            if not rarc_code and "code_value" in context and context.get("code_type") == "RARC":
                rarc_code = context["code_value"]
            
            # In a full implementation, this would call the DenialClassifierAgent
            return "Based on the denial codes you've provided, I can determine that [classification would come from specialized agent]. Would you like me to suggest steps to address this issue?"
            
        elif task_type == TaskType.CLAIM_ANALYSIS:
            # In a full implementation, this would call the ClaimsAnalyzerAgent
            return "I've analyzed the claim documents and found the following information: [analysis would come from specialized agent]. This helps explain why the claim was denied."
            
        elif task_type == TaskType.REMEDIATION_ADVICE:
            # In a full implementation, this would call the RemediationAdvisorAgent
            response_type = "remediation"
            return self._format_response(response_type,
                "Based on my analysis, here are the specific steps to resolve this denial:\n\n"
                "1. Verify the patient information on the claim matches their insurance card\n"
                "2. Confirm the procedure codes are correctly assigned for the services provided\n"
                "3. Ensure all required documentation is attached to support medical necessity\n"
                "4. Check for any authorization requirements that might not have been met\n"
                "5. Correct the specific issues identified and resubmit the claim\n\n"
                "For more personalized guidance, I would need the specific denial codes or documents."
            )
            
        else:
            # Unknown task type or general questions
            return self.generate_text(query, context)
    
    def process_query(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query and generate a response.
        
        Args:
            query: The user's query
            session_id: Optional session ID for context retrieval
            
        Returns:
            Dict[str, Any]: The agent's response and session information
        """
        logger.info(f"Processing query with session_id: {session_id}")
        
        # Create a new session if one wasn't provided
        if not session_id:
            session_id = self.session_manager.create_session()
            logger.info(f"Created new session: {session_id}")
        
        # Retrieve session context
        session = self.session_manager.get_session(session_id)
        if not session:
            # Session expired or invalid; create a new one
            session_id = self.session_manager.create_session()
            session = self.session_manager.get_session(session_id)
            logger.info(f"Created replacement session: {session_id}")
        
        # Determine conversation state
        state = self._determine_conversation_state(session)
        logger.info(f"Current conversation state: {state}")
        
        # Detect user intent
        task_type, extracted_info = self._detect_intent(query)
        logger.info(f"Detected task type: {task_type}, extracted info: {extracted_info}")
        
        # Update session with extracted information
        if extracted_info:
            self.session_manager.update_session(
                session_id=session_id,
                context_updates=extracted_info
            )
            session.update(extracted_info)
        
        # Add conversation state to context for response generation
        context = {**session, "conversation_state": state}
        
        # Route to appropriate handling based on task type
        if task_type != TaskType.UNKNOWN:
            response = self._route_to_specialized_agent(task_type, query, context)
        else:
            # Generate a response based on current state and query
            response = self.generate_text(query, context)
        
        # Apply content moderation
        callback_context = {
            "task_type": task_type.value,
            "conversation_state": state.value,
            # Add other context as needed
            "steps": task_type == TaskType.REMEDIATION_ADVICE
        }
        response = self._content_moderation_callback(callback_context, response)
        
        # Add the conversation turn to session history
        self.session_manager.add_conversation_turn(
            session_id=session_id,
            user_input=query,
            agent_response=response
        )
        
        # Update conversation state based on interaction
        new_state = state
        if state == ConversationState.GREETING:
            new_state = ConversationState.COLLECTING_INFO
        elif task_type == TaskType.DENIAL_CLASSIFICATION and state == ConversationState.COLLECTING_INFO:
            new_state = ConversationState.ANALYZING_DENIAL
        elif task_type == TaskType.REMEDIATION_ADVICE:
            new_state = ConversationState.PROVIDING_REMEDIATION
            # Update session to mark remediation as provided
            self.session_manager.update_session(
                session_id=session_id,
                context_updates={"remediation_provided": True}
            )
        
        # Only update if state has changed
        if new_state != state:
            self._update_conversation_state(session_id, new_state)
        
        # Return the response along with session info
        return {
            "session_id": session_id,
            "response": response,
            "task_type": task_type.value,
            "conversation_state": new_state.value
        }
