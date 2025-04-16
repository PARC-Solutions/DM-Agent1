"""
Denial Assistant Coordinator Agent

This module implements the main coordinator agent for the Medical Billing Denial Agent system.
It handles the conversation flow with users and coordinates with specialized sub-agents
for denial classification, claims analysis, and remediation advice.

Features:
- Workflow-based conversation management
- Specialized agent orchestration
- Context sharing and state management
- HIPAA-compliant content moderation
- Robust error handling and fallback
"""

import logging
import os
import enum
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from agent.core.session_manager import SessionManager
from agent.core.sequential_agent import SequentialDenialAgent, default_sequential_agent
from agent.core.workflow import WorkflowState
from agent.core.context_manager import ContextManager
from agent.core.message import AgentMessage

from agent.classifiers.denial_classifier import DenialClassifierAgent
from agent.analyzers.claims_analyzer import ClaimsAnalyzerAgent
from agent.advisors.remediation_advisor import RemediationAdvisorAgent

from agent.security.content_moderation import ContentModerator, default_content_moderator
from agent.security.error_handler import default_error_handler, safe_execution_decorator

logger = logging.getLogger(__name__)

# For backward compatibility, maintain the original enums
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

# Mapping between workflow states and conversation states
WORKFLOW_TO_CONVERSATION_STATE = {
    WorkflowState.GREETING.value: ConversationState.GREETING.value,
    WorkflowState.COLLECTING_INFO.value: ConversationState.COLLECTING_INFO.value,
    WorkflowState.DOCUMENT_PROCESSING.value: ConversationState.DOCUMENT_PROCESSING.value,
    WorkflowState.DOCUMENT_UPLOAD.value: ConversationState.DOCUMENT_PROCESSING.value,
    WorkflowState.ANALYZING_DENIAL_CODES.value: ConversationState.ANALYZING_DENIAL.value,
    WorkflowState.IDENTIFYING_DENIAL_TYPE.value: ConversationState.ANALYZING_DENIAL.value,
    WorkflowState.PROVIDING_REMEDIATION.value: ConversationState.PROVIDING_REMEDIATION.value,
    WorkflowState.GENERATING_REMEDIATION.value: ConversationState.PROVIDING_REMEDIATION.value,
    WorkflowState.ANSWERING_QUESTIONS.value: ConversationState.ANSWERING_QUESTIONS.value,
    WorkflowState.CLOSING.value: ConversationState.CLOSING.value
}


class DenialAssistantAgent:
    """
    Main coordinator agent for the Medical Billing Denial Assistant.
    
    This agent handles direct user interactions, maintains conversation context,
    and delegates specialized tasks to sub-agents as needed, using a sequential
    workflow to manage the conversation flow.
    
    Features:
    - Workflow-based conversation management
    - Context-aware response generation
    - Integration with specialized sub-agents
    - HIPAA-compliant content moderation
    - Robust error handling and fallback mechanisms
    """
    
    def __init__(self, 
                 session_manager: SessionManager,
                 sequential_agent: Optional[SequentialDenialAgent] = None,
                 content_moderator: Optional[ContentModerator] = None):
        """
        Initialize the Denial Assistant Coordinator Agent.
        
        Args:
            session_manager: Session manager for maintaining conversation context
            sequential_agent: Optional sequential agent for workflow management
            content_moderator: Optional content moderator for response filtering
        """
        logger.info("Initializing DenialAssistantAgent")
        
        self.session_manager = session_manager
        self.name = "medical_billing_denial_assistant"
        self.description = "Assists with resolving medical billing denials"
        
        # Get configuration from environment
        self.model_name = os.getenv("AGENT_MODEL", "gemini-2.0-pro")
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.2"))
        
        # Initialize workflow components
        self.sequential_agent = sequential_agent or default_sequential_agent
        self.context_manager = ContextManager()
        self.content_moderator = content_moderator or default_content_moderator
        
        # Initialize specialized sub-agents
        self.denial_classifier = None
        self.claims_analyzer = None
        self.remediation_advisor = None
        
        # Register specialized agent handlers
        self._initialize_specialized_agents()
        
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
        
        # Define regex patterns for intent detection (for backward compatibility)
        self.patterns = {
            "carc_rarc_codes": r'\b(carc|rarc)\s+code\s*:?\s*([A-Za-z0-9]+)',
            "denial_question": r'\b(why|reason|denied|rejection|denial)\b',
            "document_processing": r'\b(document|form|eob|cms|cms-?1500|upload)\b',
            "remediation": r'\b(how|resolve|fix|correct|appeal|resubmit|solution)\b',
            "greeting": r'\b(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))\b',
            "closing": r'\b(bye|goodbye|thank|thanks)\b',
        }
        
        logger.info(f"DenialAssistantAgent initialized with model: {self.model_name}, temperature: {self.temperature}")
    
    def _initialize_specialized_agents(self):
        """Initialize and register specialized agents with the workflow."""
        logger.info("Initializing specialized agents")
        
        # Initialize specialized agents if needed
        if not self.denial_classifier:
            self.denial_classifier = DenialClassifierAgent()
        
        if not self.claims_analyzer:
            self.claims_analyzer = ClaimsAnalyzerAgent()
        
        if not self.remediation_advisor:
            self.remediation_advisor = RemediationAdvisorAgent()
        
        # Register handlers for specific workflow states
        self.sequential_agent.register_specialized_agent(
            WorkflowState.ANALYZING_DENIAL_CODES,
            self._handle_denial_classification
        )
        
        self.sequential_agent.register_specialized_agent(
            WorkflowState.ANALYZING_CLAIM,
            self._handle_claim_analysis
        )
        
        self.sequential_agent.register_specialized_agent(
            WorkflowState.ANALYZING_EOB,
            self._handle_claim_analysis  # Reuse same handler for both
        )
        
        self.sequential_agent.register_specialized_agent(
            WorkflowState.GENERATING_REMEDIATION,
            self._handle_remediation_advice
        )
        
        self.sequential_agent.register_specialized_agent(
            WorkflowState.PROVIDING_REMEDIATION,
            self._handle_remediation_advice  # Reuse same handler
        )
        
        logger.info("Specialized agents registered with workflow")
    
    def _handle_denial_classification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle denial classification requests.
        
        Args:
            context: Session context with denial codes
            
        Returns:
            Updated context with classification results
        """
        # Extract denial codes from context
        carc_code = context.get("carc_code")
        rarc_code = context.get("rarc_code")
        group_code = context.get("group_code")
        
        if not carc_code and not rarc_code:
            return {
                "response": "To analyze a denial, I need the CARC (Claim Adjustment Reason Code) " 
                          "or RARC (Remittance Advice Remark Code) from your denial."
            }
        
        # Call the classifier agent
        classification_result = self.denial_classifier.classify_denial(
            carc_code=carc_code,
            rarc_code=rarc_code,
            group_code=group_code
        )
        
        # Format the response
        denial_type = classification_result.get("denial_type", "unknown")
        explanation = classification_result.get("explanation", "")
        severity = classification_result.get("severity", "medium")
        
        response = (
            f"Based on the denial codes you've provided "
            f"(CARC: {carc_code if carc_code else 'N/A'}"
            f"{', RARC: ' + rarc_code if rarc_code else ''}"
            f"{', Group: ' + group_code if group_code else ''}):\n\n"
            f"DENIAL ANALYSIS:\n\n"
            f"This is a {denial_type} denial with {severity} severity.\n\n"
            f"{explanation}\n\n"
            f"Would you like me to suggest steps for resolving this issue?"
        )
        
        return {
            "response": response,
            "denial_type": denial_type,
            "denial_explanation": explanation,
            "denial_severity": severity
        }
    
    def _handle_claim_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle claim and EOB document analysis.
        
        Args:
            context: Session context with document references
            
        Returns:
            Updated context with analysis results
        """
        # Check for document references
        documents = context.get("documents", [])
        
        if not documents:
            return {
                "response": "To analyze claim documents, I'll need you to upload "
                          "a CMS-1500 form, EOB, or other relevant documents."
            }
        
        document_types = [doc.get("document_type", "").lower() for doc in documents]
        
        # Determine document type for analysis
        is_cms1500 = any("cms" in doc_type or "1500" in doc_type for doc_type in document_types)
        is_eob = any("eob" in doc_type for doc_type in document_types)
        
        # Call appropriate analyzer method
        if is_cms1500:
            analysis_result = self.claims_analyzer.analyze_cms1500(documents)
            title = "CMS-1500 ANALYSIS:"
        elif is_eob:
            analysis_result = self.claims_analyzer.analyze_eob(documents)
            title = "EOB ANALYSIS:"
        else:
            analysis_result = self.claims_analyzer.analyze_generic(documents)
            title = "DOCUMENT ANALYSIS:"
        
        # Extract codes if present
        if "carc_code" in analysis_result and analysis_result["carc_code"]:
            carc_code = analysis_result["carc_code"]
            # Update context with extracted code
            context.update({"carc_code": carc_code})
        
        if "rarc_code" in analysis_result and analysis_result["rarc_code"]:
            rarc_code = analysis_result["rarc_code"]
            # Update context with extracted code
            context.update({"rarc_code": rarc_code})
        
        # Format response
        issues = analysis_result.get("issues", [])
        issues_text = "\n".join([f"- {issue}" for issue in issues]) if issues else "No specific issues identified."
        
        response = (
            f"{title}\n\n"
            f"{analysis_result.get('summary', 'I have analyzed the document.')}\n\n"
            f"POTENTIAL ISSUES:\n{issues_text}\n\n"
            f"{'Would you like me to provide specific steps to resolve these issues?' if issues else ''}"
        )
        
        return {
            "response": response,
            "analysis_result": analysis_result,
            "identified_issues": issues
        }
    
    def _handle_remediation_advice(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle remediation advice requests.
        
        Args:
            context: Session context with denial information
            
        Returns:
            Updated context with remediation steps
        """
        # Get denial information
        denial_type = context.get("denial_type")
        carc_code = context.get("carc_code")
        rarc_code = context.get("rarc_code")
        
        if not denial_type and not carc_code:
            return {
                "response": "To provide specific remediation steps, I need more information about "
                          "the denial. Can you provide the denial reason or CARC/RARC codes?"
            }
        
        # If we have codes but no type, try to classify first
        if carc_code and not denial_type:
            classification = self.denial_classifier.classify_denial(
                carc_code=carc_code,
                rarc_code=rarc_code
            )
            denial_type = classification.get("denial_type", "unknown")
        
        # Get remediation steps
        remediation = self.remediation_advisor.get_remediation_steps(
            denial_type=denial_type,
            carc_code=carc_code,
            rarc_code=rarc_code,
            claim_details=context.get("claim_details", {})
        )
        
        # Format response
        steps = remediation.get("steps", [])
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        
        requirements = remediation.get("documentation_requirements", [])
        req_text = "\n".join([f"- {req}" for req in requirements]) if requirements else ""
        
        references = remediation.get("references", [])
        ref_text = "\n".join([f"- {ref}" for ref in references]) if references else ""
        
        response = (
            f"STEPS TO RESOLVE:\n\n"
            f"{steps_text}\n\n"
        )
        
        if req_text:
            response += f"REQUIRED DOCUMENTATION:\n{req_text}\n\n"
        
        if ref_text:
            response += f"REFERENCES:\n{ref_text}"
        
        return {
            "response": response,
            "remediation_steps": steps,
            "documentation_requirements": requirements,
            "references": references,
            "remediation_provided": True
        }
    
    @safe_execution_decorator(component_name="content_moderation")
    def _moderate_response(self, response: str, context: Dict[str, Any]) -> str:
        """
        Apply content moderation to a response.
        
        This method handles:
        - HIPAA compliance checks
        - PHI detection and redaction
        - Content safety filtering
        - Response formatting standardization
        - Adding appropriate disclaimers
        
        Args:
            response: The response to moderate
            context: Session context
            
        Returns:
            Moderated response text
        """
        # Extract moderation context
        moderation_context = {
            "task_type": context.get("task_type", "unknown"),
            "conversation_state": context.get("conversation_state", "unknown"),
            "workflow_state": context.get("workflow_state", "unknown"),
            "medical_advice": "diagnosis" in response.lower() or "treatment" in response.lower(),
            "steps": "steps to resolve" in response.lower() or "remediation" in context.get("task_type", "").lower()
        }
        
        # Apply content moderation
        moderation_result = self.content_moderator.moderate_response(
            response=response,
            context=moderation_context
        )
        
        # Log moderation actions if significant changes were made
        if moderation_result["moderated_response"] != response:
            logger.info(f"Response moderated with actions: {moderation_result['moderation_details']}")
        
        return moderation_result["moderated_response"]
    
    def _detect_intent(self, query: str) -> Tuple[TaskType, Dict[str, Any]]:
        """
        Detect the user's intent from their query to augment workflow context.
        
        NOTE: This is maintained for backward compatibility. The workflow system
        now handles most routing based on context and state.
        
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
            if code_type.upper() == "CARC":
                extracted_info["carc_code"] = code_value
            else:
                extracted_info["rarc_code"] = code_value
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
    
    def _map_workflow_to_conversation_state(self, workflow_state: str) -> str:
        """
        Map a workflow state to a conversation state.
        
        This is used for backward compatibility with existing code.
        
        Args:
            workflow_state: The workflow state
            
        Returns:
            The equivalent conversation state
        """
        return WORKFLOW_TO_CONVERSATION_STATE.get(
            workflow_state, ConversationState.COLLECTING_INFO.value
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
            group_code = context.get("group_code")
            
            if not carc_code and "code_value" in context and context.get("code_type") == "CARC":
                carc_code = context["code_value"]
                
            if not rarc_code and "code_value" in context and context.get("code_type") == "RARC":
                rarc_code = context["code_value"]
            
            # If we have a CARC code, call the denial classifier agent
            if carc_code:
                logger.info(f"Classifying denial with CARC code: {carc_code}")
                classification_result = self.denial_classifier.classify_denial(
                    carc_code=carc_code,
                    rarc_code=rarc_code,
                    group_code=group_code
                )
                
                # Extract the explanation from the result
                explanation = classification_result.get("explanation", "")
                denial_type = classification_result.get("denial_type", "unknown")
                severity = classification_result.get("severity", "medium")
                
                # Format the response
                response_type = "denial_analysis"
                response = (
                    f"Based on the denial codes you've provided (CARC: {carc_code}"
                    f"{', RARC: ' + rarc_code if rarc_code else ''}"
                    f"{', Group: ' + group_code if group_code else ''}), "
                    f"I can determine that this is a {denial_type} denial with {severity} severity.\n\n"
                    f"{explanation}\n\n"
                    "Would you like me to suggest steps to address this issue?"
                )
                
                return self._format_response(response_type, response)
            else:
                # No CARC code provided
                return "To classify a denial, I need the CARC (Claim Adjustment Reason Code) from your denial. This code explains why the claim was adjusted or denied. You can usually find this on your Explanation of Benefits (EOB) or remittance advice."
            
        elif task_type == TaskType.CLAIM_ANALYSIS:
            # In a full implementation, this would use document data from context
            # For now, we'll return a message about the document analysis process
            
            # Check if we have document references in the session
            document_references = context.get("documents", [])
            
            if document_references:
                # If we have document references, we would analyze them
                # For now, simulate an analysis result
                document_type = document_references[0].get("document_type", "claim document")
                
                # Format response based on document type
                if "cms" in document_type.lower() or "1500" in document_type:
                    analysis_message = (
                        "I've analyzed the CMS-1500 form and found the following information:\n\n"
                        "- Patient demographics appear complete\n"
                        "- Provider information is present\n"
                        "- Procedure codes are included\n"
                        "- Diagnosis codes are included\n\n"
                        "Several potential issues could be contributing to the denial:\n"
                        "1. The diagnosis codes may not support the procedures performed\n"
                        "2. There might be missing modifiers needed for proper coding\n"
                        "3. Some required authorization information appears to be missing\n\n"
                        "For a more detailed analysis, I would need to extract and verify specific fields."
                    )
                elif "eob" in document_type.lower():
                    analysis_message = (
                        "I've analyzed the EOB document and found the following information:\n\n"
                        "- The claim has been processed but not paid in full\n"
                        "- Several adjustment codes are present that explain the denial\n"
                        "- Patient responsibility amount is indicated\n\n"
                        "The denial appears to be related to [specific reason would be extracted]. "
                        "Based on the CARC/RARC codes in the document, this is typically due to [specific reason]."
                    )
                else:
                    analysis_message = (
                        "I've analyzed the claim document and found information that may help understand the denial. "
                        "For more specific analysis, I would need to know what type of document this is (CMS-1500, EOB, etc.) "
                        "and extract the specific fields to identify potential issues."
                    )
                
                return analysis_message
            else:
                # No document references found
                return "To analyze claim documents, I'll need you to upload or provide the CMS-1500 form, Explanation of Benefits (EOB), or other relevant documents. These will help me identify specific issues that might have caused the denial."
            
        elif task_type == TaskType.REMEDIATION_ADVICE:
            # Get denial information from context
            denial_type = context.get("denial_type", "unknown")
            carc_code = context.get("carc_code")
            rarc_code = context.get("rarc_code")
            claim_details = context.get("claim_details", {})
            
            # If we have a CARC code but no denial type, try to get it from the classifier
            if carc_code and denial_type == "unknown":
                classification_result = self.denial_classifier.classify_denial(
                    carc_code=carc_code,
                    rarc_code=rarc_code
                )
                denial_type = classification_result.get("denial_type", "unknown")
            
            # If we have a denial type, get remediation steps
            if denial_type != "unknown":
                logger.info(f"Getting remediation steps for denial type: {denial_type}")
                remediation_result = self.remediation_advisor.get_remediation_steps(
                    denial_type=denial_type,
                    claim_details=claim_details,
                    carc_code=carc_code if carc_code else "",
                    rarc_code=rarc_code
                )
                
                # Extract steps and requirements
                steps = remediation_result.get("steps", [])
                requirements = remediation_result.get("documentation_requirements", [])
                references = remediation_result.get("references", [])
                
                # Format the steps into a readable response
                steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
                requirements_text = "\n".join([f"• {req}" for req in requirements])
                references_text = "\n".join([f"• {ref}" for ref in references])
                
                response = (
                    f"Based on my analysis of this {denial_type} denial"
                    f"{' with CARC code ' + carc_code if carc_code else ''}"
                    f"{' and RARC code ' + rarc_code if rarc_code else ''}"
                    f", here are specific steps to resolve it:\n\n"
                    f"{steps_text}\n\n"
                )
                
                # Add documentation requirements if available
                if requirements:
                    response += f"You will need the following documentation:\n{requirements_text}\n\n"
                
                # Add references if available
                if references:
                    response += f"Relevant references:\n{references_text}"
                
                response_type = "remediation"
                return self._format_response(response_type, response)
            else:
                # No specific denial type identified
                response_type = "remediation"
                generic_steps = (
                    "Based on the information provided, here are general steps to address the denial:\n\n"
                    "1. Verify the patient information on the claim matches their insurance card\n"
                    "2. Confirm the procedure codes are correctly assigned for the services provided\n"
                    "3. Ensure all required documentation is attached to support medical necessity\n"
                    "4. Check for any authorization requirements that might not have been met\n"
                    "5. Correct any identified issues and resubmit the claim\n\n"
                    "For more personalized guidance, I would need the specific denial codes (CARC/RARC) or denial documents."
                )
                return self._format_response(response_type, generic_steps)
            
        else:
            # Unknown task type or general questions
            return self.generate_text(query, context)
    
    @safe_execution_decorator(component_name="coordinator_process_query")
    def process_query(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query and generate a response using the workflow system.
        
        Args:
            query: The user's query
            session_id: Optional session ID for context retrieval
            
        Returns:
            Dict[str, Any]: The agent's response and session information
        """
        process_start_time = time.time()
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
        
        # Detect intent and extract any relevant information
        task_type, extracted_info = self._detect_intent(query)
        logger.info(f"Detected task type: {task_type}, extracted info: {extracted_info}")
        
        # Update session with extracted information
        if extracted_info:
            self.session_manager.update_session(
                session_id=session_id,
                context_updates=extracted_info
            )
            session.update(extracted_info)
        
        # Process the query through the sequential workflow
        processed_context = self.sequential_agent.process(query, session)
        
        # Extract the response from the processed context
        response = processed_context.get("response", "")
        
        # Apply content moderation for HIPAA compliance and appropriateness
        moderated_response = self._moderate_response(response, processed_context)
        
        # Get conversation state (for backward compatibility)
        workflow_state = processed_context.get("workflow_state", WorkflowState.GREETING.value)
        conversation_state = self._map_workflow_to_conversation_state(workflow_state)
        
        # Add the conversation turn to session history
        conversation_turn = {
            "user_input": query,
            "agent_response": moderated_response,
            "metadata": {
                "workflow_state": workflow_state,
                "task_type": task_type.value,
                "processing_time": time.time() - process_start_time
            }
        }
        
        self.session_manager.update_session(
            session_id=session_id,
            context_updates={
                "last_query": query,
                "task_type": task_type.value,
                "conversation_state": conversation_state,
                "conversation_history": session.get("conversation_history", []) + [conversation_turn]
            }
        )
        
        # Merge processed context back to session to preserve all data
        # Filter out transient entries
        session_updates = {
            k: v for k, v in processed_context.items() 
            if k not in ["response", "processing_time", "workflow_metrics", "errors"]
        }
        
        self.session_manager.update_session(
            session_id=session_id,
            context_updates=session_updates
        )
        
        # Get performance metrics for logging
        performance_metrics = self.sequential_agent.get_performance_metrics()
        logger.debug(f"Performance metrics: {performance_metrics}")
        
        # Return the response along with session info
        return {
            "session_id": session_id,
            "response": moderated_response,
            "task_type": task_type.value,
            "conversation_state": conversation_state,
            "workflow_state": workflow_state,
            "processing_time": time.time() - process_start_time
        }
    
    def reset_session_workflow(self, session_id: str) -> Dict[str, Any]:
        """
        Reset the workflow for a session.
        
        This is useful when a conversation needs to be restarted from the beginning.
        
        Args:
            session_id: The session ID
            
        Returns:
            Updated session information
        """
        # Get current session
        session = self.session_manager.get_session(session_id)
        if not session:
            logger.warning(f"Cannot reset workflow: Session {session_id} not found")
            return {
                "success": False,
                "message": "Session not found"
            }
        
        # Reset the workflow using sequential agent
        updated_context = self.sequential_agent.reset_workflow(session)
        
        # Update session with reset context
        self.session_manager.update_session(
            session_id=session_id,
            context_updates=updated_context
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Workflow reset successfully",
            "workflow_state": updated_context.get("workflow_state")
        }
    
    def visualize_session_workflow(self, session_id: str) -> Dict[str, Any]:
        """
        Generate a visualization of the session workflow.
        
        This is useful for understanding the conversation flow and debugging.
        
        Args:
            session_id: The session ID
            
        Returns:
            Visualization data
        """
        # Get current session
        session = self.session_manager.get_session(session_id)
        if not session:
            logger.warning(f"Cannot visualize workflow: Session {session_id} not found")
            return {
                "success": False,
                "message": "Session not found"
            }
        
        # Get visualization from sequential agent
        visualization = self.sequential_agent.visualize_conversation_flow(session)
        
        return {
            "success": True,
            "session_id": session_id,
            "visualization": visualization
        }
