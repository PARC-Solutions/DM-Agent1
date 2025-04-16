"""
Denial Classifier Agent

This module implements a specialized agent that classifies denial types based on
CARC (Claim Adjustment Reason Codes) and RARC (Remittance Advice Remark Codes).

Features:
- CARC/RARC code interpretation
- Denial type classification
- Detailed explanations of denial reasons
- Severity assessment of denial issues
"""

import logging
import json
import os
from typing import Dict, List, Optional, Tuple, Any, Union

logger = logging.getLogger(__name__)


class DenialClassifierAgent:
    """
    Specialized agent for classifying denial types based on CARC/RARC codes.
    
    This agent interprets denial codes to determine the exact reason for claim denial
    and provides clear explanations that billing staff can understand.
    
    Features:
    - Accurate classification of denial types based on CARC/RARC codes
    - Detailed explanations of what each code means in plain language
    - Severity assessment to help prioritize resolution efforts
    - Integration with CARC/RARC knowledge base for up-to-date code information
    """
    
    def __init__(self):
        """
        Initialize the Denial Classifier Agent with knowledge base connection.
        """
        logger.info("Initializing DenialClassifierAgent")
        
        # Load the CARC/RARC knowledge base
        self.knowledge_base = self._load_knowledge_base()
        
        # Create lookup dictionaries for faster access
        self.carc_lookup = {code["code"]: code for code in self.knowledge_base.get("carc_codes", [])}
        self.rarc_lookup = {code["code"]: code for code in self.knowledge_base.get("rarc_codes", [])}
        self.group_code_lookup = {code["code"]: code for code in self.knowledge_base.get("group_codes", [])}
        
        # Define severity levels for different denial types
        self.severity_levels = {
            "medical_necessity": "high",
            "bundling": "medium",
            "timely_filing": "high",
            "missing_information": "medium",
            "documentation": "medium",
            "eligibility": "high",
            "authorization": "high",
            "coordination_of_benefits": "medium",
            "network": "medium",
            "duplicate": "low",
            "coding_error": "medium",
            "unknown": "medium"
        }
        
        logger.info(f"DenialClassifierAgent initialized with {len(self.carc_lookup)} CARC codes and {len(self.rarc_lookup)} RARC codes")
    
    def _load_knowledge_base(self) -> Dict:
        """
        Load the CARC/RARC knowledge base from JSON file.
        
        Returns:
            Dict: The knowledge base content
        """
        try:
            knowledge_base_path = os.path.join("knowledge_base", "carc_rarc", "carc_rarc_knowledge.json")
            with open(knowledge_base_path, 'r') as file:
                knowledge_base = json.load(file)
                
            logger.info(f"Loaded CARC/RARC knowledge base from {knowledge_base_path}")
            return knowledge_base
        except Exception as e:
            logger.error(f"Error loading CARC/RARC knowledge base: {e}")
            # Return empty knowledge base as fallback
            return {"carc_codes": [], "rarc_codes": [], "group_codes": []}
    
    def classify_denial(self, carc_code: str, rarc_code: Optional[str] = None,
                       group_code: Optional[str] = None) -> Dict:
        """
        Classify a denial based on CARC and optional RARC codes.
        
        Args:
            carc_code: Claim Adjustment Reason Code
            rarc_code: Optional Remittance Advice Remark Code
            group_code: Optional Group Code (CO, PR, etc.)
            
        Returns:
            Dict: Classification results including denial type, explanation, and severity
        """
        logger.info(f"Classifying denial with CARC: {carc_code}, RARC: {rarc_code}, Group: {group_code}")
        
        # Look up the CARC code information
        carc_info = self.carc_lookup.get(carc_code)
        if not carc_info:
            logger.warning(f"CARC code {carc_code} not found in knowledge base")
            return self._generate_unknown_code_response(carc_code, "CARC")
        
        # Look up the RARC code information if provided
        rarc_info = None
        if rarc_code:
            rarc_info = self.rarc_lookup.get(rarc_code)
            if not rarc_info:
                logger.warning(f"RARC code {rarc_code} not found in knowledge base")
        
        # Look up the group code information if provided
        group_info = None
        if group_code:
            group_info = self.group_code_lookup.get(group_code)
            if not group_info:
                logger.warning(f"Group code {group_code} not found in knowledge base")
        
        # Determine the denial type from the CARC code
        denial_type = carc_info.get("denial_type", "unknown")
        
        # Determine the severity of the denial
        severity = self.severity_levels.get(denial_type, "medium")
        
        # Build the explanation based on the available information
        explanation = self._build_explanation(carc_info, rarc_info, group_info)
        
        # Get resolution steps if available
        resolution_steps = carc_info.get("resolution_steps", [])
        
        # Construct and return the classification result
        result = {
            "status": "success",
            "carc_code": carc_code,
            "carc_description": carc_info.get("description", "No description available"),
            "denial_type": denial_type,
            "severity": severity,
            "explanation": explanation,
            "resolution_steps": resolution_steps
        }
        
        # Add RARC information if available
        if rarc_info:
            result["rarc_code"] = rarc_code
            result["rarc_description"] = rarc_info.get("description", "No description available")
        
        # Add group code information if available
        if group_info:
            result["group_code"] = group_code
            result["group_description"] = group_info.get("description", "No description available")
        
        logger.info(f"Classified denial as type: {denial_type}, severity: {severity}")
        return result
    
    def _build_explanation(self, carc_info: Dict, rarc_info: Optional[Dict] = None,
                         group_info: Optional[Dict] = None) -> str:
        """
        Build a clear explanation of the denial based on code information.
        
        Args:
            carc_info: Information about the CARC code
            rarc_info: Optional information about the RARC code
            group_info: Optional information about the group code
            
        Returns:
            str: A detailed explanation of the denial
        """
        # Start with the CARC explanation
        explanation = f"This claim was denied because: {carc_info.get('description', 'Unknown reason')}. "
        
        # Add information based on denial type
        denial_type = carc_info.get("denial_type", "unknown")
        
        if denial_type == "missing_information":
            explanation += "The claim is missing required information that the payer needs to process it. "
        elif denial_type == "medical_necessity":
            explanation += "The payer has determined that the service does not meet their criteria for medical necessity. "
        elif denial_type == "bundling":
            explanation += "The service is considered bundled with another service that was billed. "
        elif denial_type == "timely_filing":
            explanation += "The claim was not submitted within the payer's required timeframe. "
        elif denial_type == "documentation":
            explanation += "Additional documentation is required to support this claim. "
        
        # Add RARC information if available
        if rarc_info:
            explanation += f"Additional information from the payer: {rarc_info.get('description', '')}. "
        
        # Add group code information if available
        if group_info:
            if group_info.get('code') == 'CO':
                explanation += "This is a contractual obligation, meaning the provider is financially responsible for this adjustment. "
            elif group_info.get('code') == 'PR':
                explanation += "This is a patient responsibility, meaning the patient is financially responsible for this amount. "
        
        # Add resolution guidance
        if "resolution_steps" in carc_info and carc_info["resolution_steps"]:
            steps_text = ", ".join(carc_info["resolution_steps"])
            explanation += f"To resolve this issue, you should: {steps_text}."
        
        return explanation
    
    def _generate_unknown_code_response(self, code: str, code_type: str) -> Dict:
        """
        Generate a response for unknown CARC or RARC codes.
        
        Args:
            code: The unknown code
            code_type: The type of code (CARC or RARC)
            
        Returns:
            Dict: A response indicating the code is unknown
        """
        logger.warning(f"Generating response for unknown {code_type} code: {code}")
        
        return {
            "status": "unknown_code",
            f"{code_type.lower()}_code": code,
            "denial_type": "unknown",
            "severity": "medium",
            "explanation": f"The {code_type} code {code} is not in our knowledge base. Please refer to the official {code_type} code list for the most current information.",
            "resolution_steps": ["Verify the code is correct", "Check the payer's documentation", "Contact the payer for clarification"]
        }
    
    def get_code_information(self, code_type: str, code: str) -> Dict:
        """
        Get detailed information about a specific CARC or RARC code.
        
        Args:
            code_type: Type of code ("CARC" or "RARC")
            code: The code to look up
            
        Returns:
            Dict: Information about the code
        """
        logger.info(f"Looking up information for {code_type} code: {code}")
        
        if code_type.upper() == "CARC":
            code_info = self.carc_lookup.get(code)
            if not code_info:
                return self._generate_unknown_code_response(code, "CARC")
            return {
                "status": "success",
                "code_type": "CARC",
                "code": code,
                "description": code_info.get("description", "No description available"),
                "denial_type": code_info.get("denial_type", "unknown"),
                "resolution_steps": code_info.get("resolution_steps", [])
            }
        
        elif code_type.upper() == "RARC":
            code_info = self.rarc_lookup.get(code)
            if not code_info:
                return self._generate_unknown_code_response(code, "RARC")
            return {
                "status": "success",
                "code_type": "RARC",
                "code": code,
                "description": code_info.get("description", "No description available")
            }
        
        else:
            logger.error(f"Invalid code type: {code_type}")
            return {
                "status": "error",
                "message": f"Invalid code type: {code_type}. Must be either 'CARC' or 'RARC'."
            }
    
    def list_codes_by_denial_type(self, denial_type: str) -> Dict:
        """
        List all CARC codes associated with a specific denial type.
        
        Args:
            denial_type: The type of denial to look up codes for
            
        Returns:
            Dict: List of CARC codes matching the denial type
        """
        logger.info(f"Listing codes for denial type: {denial_type}")
        
        matching_codes = [
            {
                "code": code["code"],
                "description": code.get("description", "No description available"),
                "resolution_steps": code.get("resolution_steps", [])
            }
            for code in self.knowledge_base.get("carc_codes", [])
            if code.get("denial_type") == denial_type
        ]
        
        if not matching_codes:
            logger.warning(f"No codes found for denial type: {denial_type}")
            return {
                "status": "no_results",
                "message": f"No CARC codes found for denial type: {denial_type}"
            }
        
        return {
            "status": "success",
            "denial_type": denial_type,
            "severity": self.severity_levels.get(denial_type, "medium"),
            "matching_codes": matching_codes,
            "count": len(matching_codes)
        }
