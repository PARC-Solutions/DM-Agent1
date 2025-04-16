"""
Remediation Advisor Agent

This module implements a specialized agent that provides actionable steps for
resolving denial issues, based on denial types and claim details.

Features:
- Step-by-step remediation guidance
- Code compatibility verification
- Documentation requirement recommendations
- Integration with resolution knowledge base
- Regulatory reference inclusion
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any, Tuple, Union

logger = logging.getLogger(__name__)


class RemediationAdvisorAgent:
    """
    Specialized agent for providing actionable steps to resolve claim denials.
    
    This agent generates specific corrective actions based on the denial reason
    and claim details, with concrete, step-by-step guidance for billing staff.
    
    Features:
    - Generation of detailed, step-by-step remediation instructions
    - Integration with resolution knowledge base for up-to-date strategies
    - Code compatibility verification to identify billing conflicts
    - Documentation requirement recommendations for claim resubmission
    - Prioritized actions based on denial type and severity
    - Regulatory references for compliance support
    """
    
    def __init__(self):
        """
        Initialize the Remediation Advisor Agent with knowledge base connections.
        """
        logger.info("Initializing RemediationAdvisorAgent")
        
        # Load the resolution knowledge base
        self.resolution_knowledge_base = self._load_resolution_knowledge_base()
        
        # Load the code compatibility knowledge base
        self.compatibility_knowledge_base = self._load_compatibility_knowledge_base()
        
        # Create lookup dictionaries for faster access
        self.resolution_strategies = {
            strategy_name: strategy_data 
            for strategy_name, strategy_data in self.resolution_knowledge_base.get("resolution_strategies", {}).items()
        }
        
        # Create compatibility lookup
        self.allowed_modifiers = self.compatibility_knowledge_base.get("allowed_modifiers", [])
        self.modifier_allowed_pairs = {}
        self.modifier_not_allowed_pairs = {}
        
        # Process code pairs for faster lookup
        for pair in self.compatibility_knowledge_base.get("code_pairs", {}).get("modifier_allowed", []):
            key = f"{pair['column1_code']}_{pair['column2_code']}"
            self.modifier_allowed_pairs[key] = pair
            
        for pair in self.compatibility_knowledge_base.get("code_pairs", {}).get("modifier_not_allowed", []):
            key = f"{pair['column1_code']}_{pair['column2_code']}"
            self.modifier_not_allowed_pairs[key] = pair
        
        # Reference information
        self.billing_rule_references = self.resolution_knowledge_base.get("billing_rule_references", {})
        
        # Denial type priority (for prioritizing steps)
        self.denial_type_priority = {
            "timely_filing": 1,      # Highest priority due to strict deadlines
            "authorization": 2,      # Authorization issues need prompt attention
            "medical_necessity": 3,  # Medical necessity denials often require documentation
            "bundling": 4,           # Bundling issues involve code corrections
            "missing_information": 5 # Missing information is often straightforward to fix
        }
        
        logger.info(f"RemediationAdvisorAgent initialized with {len(self.resolution_strategies)} resolution strategies")
    
    def _load_resolution_knowledge_base(self) -> Dict:
        """
        Load the resolution knowledge base from JSON file.
        
        Returns:
            Dict: The knowledge base content
        """
        try:
            knowledge_base_path = os.path.join("knowledge_base", "resolution", "resolution_knowledge.json")
            with open(knowledge_base_path, 'r') as file:
                knowledge_base = json.load(file)
                
            logger.info(f"Loaded resolution knowledge base from {knowledge_base_path}")
            return knowledge_base
        except Exception as e:
            logger.error(f"Error loading resolution knowledge base: {e}")
            # Return empty knowledge base as fallback
            return {"resolution_strategies": {}, "billing_rule_references": {}}
    
    def _load_compatibility_knowledge_base(self) -> Dict:
        """
        Load the code compatibility knowledge base from JSON file.
        
        Returns:
            Dict: The knowledge base content
        """
        try:
            knowledge_base_path = os.path.join("knowledge_base", "dont_bill_together", "dont_bill_together_knowledge.json")
            with open(knowledge_base_path, 'r') as file:
                knowledge_base = json.load(file)
                
            logger.info(f"Loaded compatibility knowledge base from {knowledge_base_path}")
            return knowledge_base
        except Exception as e:
            logger.error(f"Error loading compatibility knowledge base: {e}")
            # Return empty knowledge base as fallback
            return {"allowed_modifiers": [], "code_pairs": {"modifier_allowed": [], "modifier_not_allowed": []}}
    
    def get_remediation_steps(self, denial_type: str, claim_details: Dict, 
                             carc_code: str, rarc_code: Optional[str] = None) -> Dict:
        """
        Get specific remediation steps for a denial.
        
        Args:
            denial_type: The type of denial (e.g., "missing_information", "coding_error")
            claim_details: Details about the claim from document analysis
            carc_code: Claim Adjustment Reason Code
            rarc_code: Optional Remittance Advice Remark Code
            
        Returns:
            Dict: Remediation information including steps, documentation requirements, etc.
        """
        logger.info(f"Getting remediation steps for denial type: {denial_type}, CARC: {carc_code}, RARC: {rarc_code}")
        
        # Find the matching strategy based on denial type
        strategy = self.resolution_strategies.get(denial_type)
        
        # If no matching strategy, try to find a close match or use a general approach
        if not strategy:
            logger.warning(f"No specific strategy found for denial type: {denial_type}")
            strategy = self._find_alternative_strategy(denial_type)
        
        if not strategy:
            logger.error(f"No suitable strategy found for denial type: {denial_type}")
            return self._generate_generic_steps(denial_type, carc_code, rarc_code)
        
        # Start building the response
        result = {
            "status": "success",
            "denial_type": denial_type,
            "carc_code": carc_code,
            "steps": [],
            "documentation_requirements": [],
            "references": [],
            "priority": self.denial_type_priority.get(denial_type, 10)  # Default to low priority
        }
        
        # Add RARC if provided
        if rarc_code:
            result["rarc_code"] = rarc_code
        
        # Add general steps from the strategy
        if "general_steps" in strategy:
            result["steps"].extend(strategy["general_steps"])
        
        # Add specific strategies based on the CARC code and claim details
        additional_steps = self._generate_specific_steps(
            denial_type, carc_code, rarc_code, claim_details, strategy
        )
        
        # Add the specific steps
        if additional_steps:
            result["steps"].extend(additional_steps)
        
        # Add documentation requirements
        if "documentation_requirements" in strategy:
            result["documentation_requirements"].extend(strategy["documentation_requirements"])
        
        # Add any claim-specific documentation requirements
        claim_specific_docs = self._get_claim_specific_documentation(
            denial_type, claim_details
        )
        if claim_specific_docs:
            result["documentation_requirements"].extend(claim_specific_docs)
        
        # Add relevant references
        references = self._get_relevant_references(denial_type, carc_code)
        if references:
            result["references"] = references
        
        # Deduplicate steps and requirements
        result["steps"] = list(dict.fromkeys(result["steps"]))
        result["documentation_requirements"] = list(dict.fromkeys(result["documentation_requirements"]))
        
        logger.info(f"Generated {len(result['steps'])} remediation steps for {denial_type} denial")
        return result
    
    def _find_alternative_strategy(self, denial_type: str) -> Optional[Dict]:
        """
        Find an alternative strategy when the exact match is not found.
        
        Args:
            denial_type: The denial type to find an alternative for
            
        Returns:
            Optional[Dict]: An alternative strategy or None if none found
        """
        # Map common alternative names
        alternatives = {
            "coding_error": "bundling",
            "provider_information": "missing_information",
            "patient_information": "missing_information",
            "coverage_issue": "medical_necessity",
            "authorization_required": "medical_necessity",
            "insurance_verification": "coordination_of_benefits"
        }
        
        # Try to find an alternative
        alt_type = alternatives.get(denial_type)
        if alt_type:
            return self.resolution_strategies.get(alt_type)
        
        return None
    
    def _generate_generic_steps(self, denial_type: str, carc_code: str, rarc_code: Optional[str] = None) -> Dict:
        """
        Generate generic steps when no specific strategy is found.
        
        Args:
            denial_type: The type of denial
            carc_code: Claim Adjustment Reason Code
            rarc_code: Optional Remittance Advice Remark Code
            
        Returns:
            Dict: Generic remediation steps
        """
        logger.info(f"Generating generic steps for denial type: {denial_type}")
        
        # Create a generic response
        result = {
            "status": "partial",
            "denial_type": denial_type,
            "carc_code": carc_code,
            "steps": [
                "Review the denial details and CARC/RARC codes carefully",
                "Verify all patient and provider information is correct",
                "Check if there are any coding or billing errors",
                "Ensure all required documentation is available",
                "Contact the payer for specific guidance on this denial"
            ],
            "documentation_requirements": [
                "Patient demographic information",
                "Insurance verification",
                "Complete medical records related to the service"
            ],
            "references": [],
            "priority": self.denial_type_priority.get(denial_type, 10),
            "message": "Generic steps provided as no specific strategy was found for this denial type"
        }
        
        # Add RARC if provided
        if rarc_code:
            result["rarc_code"] = rarc_code
        
        return result
    
    def _generate_specific_steps(self, denial_type: str, carc_code: str, 
                               rarc_code: Optional[str], claim_details: Dict,
                               strategy: Dict) -> List[str]:
        """
        Generate specific steps based on the claim details and codes.
        
        Args:
            denial_type: The type of denial
            carc_code: Claim Adjustment Reason Code
            rarc_code: Optional Remittance Advice Remark Code
            claim_details: Details from the claim document
            strategy: The resolution strategy
            
        Returns:
            List[str]: Specific remediation steps
        """
        specific_steps = []
        
        # Add specific strategies from the knowledge base
        if "specific_strategies" in strategy:
            specific_steps.extend(strategy["specific_strategies"])
        
        # Add steps based on the denial type
        if denial_type == "missing_information":
            # Check which fields are missing and add steps to address them
            if claim_details:
                for field in ["patient_name", "patient_dob", "patient_id", "provider_npi"]:
                    if field not in claim_details or not claim_details[field]:
                        specific_steps.append(f"Add the missing {field.replace('_', ' ')} to the claim")
        
        elif denial_type == "bundling":
            # Add steps for reviewing codes
            if "procedure_codes" in claim_details and len(claim_details["procedure_codes"]) > 1:
                specific_steps.append("Review all procedure codes for possible bundling conflicts")
                specific_steps.append("Check if appropriate modifiers should be used")
                
                # Check code compatibility for pairs of codes
                codes = claim_details.get("procedure_codes", [])
                for i in range(len(codes)):
                    for j in range(i+1, len(codes)):
                        compatibility = self.check_code_compatibility(codes[i], codes[j])
                        if compatibility.get("status") == "incompatible":
                            specific_steps.append(
                                f"Address incompatible codes: {codes[i]} and {codes[j]} - {compatibility.get('resolution', '')}"
                            )
        
        elif denial_type == "medical_necessity":
            specific_steps.append("Gather all clinical documentation supporting medical necessity")
            specific_steps.append("Verify that the diagnosis codes support the procedures performed")
            specific_steps.append("Consider obtaining a letter of medical necessity from the provider")
        
        elif denial_type == "timely_filing":
            specific_steps.append("Gather evidence of original timely submission (electronic submission records, certified mail receipts)")
            specific_steps.append("Check payer's timely filing limits and appeal policies")
        
        # Add steps for RARC code if present
        if rarc_code:
            specific_steps.append(f"Address the specific issue indicated by RARC code {rarc_code}")
        
        return specific_steps
    
    def _get_claim_specific_documentation(self, denial_type: str, claim_details: Dict) -> List[str]:
        """
        Get claim-specific documentation requirements.
        
        Args:
            denial_type: The type of denial
            claim_details: Details from the claim document
            
        Returns:
            List[str]: Documentation requirements
        """
        documentation = []
        
        # Add documentation based on the denial type and claim details
        if denial_type == "medical_necessity":
            if "diagnosis_codes" in claim_details:
                documentation.append("Clinical documentation supporting the diagnosis codes")
            if "procedure_codes" in claim_details:
                documentation.append("Documentation showing medical necessity for the procedures performed")
                
        elif denial_type == "bundling":
            documentation.append("Documentation to support the use of modifiers if applicable")
            
        elif denial_type == "missing_information":
            if claim_details:
                missing_fields = []
                for field in ["patient_name", "patient_dob", "patient_id", "provider_npi"]:
                    if field not in claim_details or not claim_details[field]:
                        missing_fields.append(field.replace("_", " "))
                
                if missing_fields:
                    documentation.append(f"Updated information for: {', '.join(missing_fields)}")
        
        return documentation
    
    def _get_relevant_references(self, denial_type: str, carc_code: str) -> List[str]:
        """
        Get relevant references for the denial type.
        
        Args:
            denial_type: The type of denial
            carc_code: Claim Adjustment Reason Code
            
        Returns:
            List[str]: Relevant references
        """
        references = []
        
        # Add references based on the denial type
        if denial_type == "bundling":
            if "coding_references" in self.billing_rule_references:
                references.extend(self.billing_rule_references["coding_references"])
                
        elif denial_type == "medical_necessity":
            if "coverage_policies" in self.billing_rule_references:
                references.extend(self.billing_rule_references["coverage_policies"])
        
        # Add general Medicare references if available
        if "medicare_manuals" in self.billing_rule_references:
            references.append(f"Medicare Claims Processing Manual: {self.billing_rule_references['medicare_manuals'][0]}")
        
        return references
    
    def check_code_compatibility(self, primary_code: str, secondary_code: str) -> Dict:
        """
        Check if two billing codes can be submitted together.
        
        Args:
            primary_code: The primary procedure/service code
            secondary_code: The secondary procedure/service code
            
        Returns:
            Dict: Compatibility status and explanation
        """
        logger.info(f"Checking compatibility of codes: {primary_code} and {secondary_code}")
        
        # Check in both directions (order shouldn't matter)
        key1 = f"{primary_code}_{secondary_code}"
        key2 = f"{secondary_code}_{primary_code}"
        
        # Check if pair exists in modifier allowed list
        pair_info = self.modifier_allowed_pairs.get(key1) or self.modifier_allowed_pairs.get(key2)
        if pair_info:
            return {
                "status": "compatible_with_modifier",
                "primary_code": primary_code,
                "secondary_code": secondary_code,
                "allowed_modifiers": self.allowed_modifiers,
                "resolution": pair_info.get("resolution_guidance", "Use appropriate modifier"),
                "documentation_requirements": pair_info.get("documentation_requirements", []),
                "effective_date": pair_info.get("effective_date")
            }
        
        # Check if pair exists in modifier not allowed list
        pair_info = self.modifier_not_allowed_pairs.get(key1) or self.modifier_not_allowed_pairs.get(key2)
        if pair_info:
            return {
                "status": "incompatible",
                "primary_code": primary_code,
                "secondary_code": secondary_code,
                "resolution": pair_info.get("resolution_guidance", "These codes cannot be billed together"),
                "documentation_requirements": pair_info.get("documentation_requirements", []),
                "effective_date": pair_info.get("effective_date")
            }
        
        # If not found in either list, assume compatible
        return {
            "status": "likely_compatible",
            "primary_code": primary_code,
            "secondary_code": secondary_code,
            "message": "No specific compatibility rule found. Verify with payer policies."
        }
    
    def get_resolution_strategy_by_type(self, denial_type: str) -> Dict:
        """
        Get the complete resolution strategy for a denial type.
        
        Args:
            denial_type: The type of denial to get strategy for
            
        Returns:
            Dict: Resolution strategy information
        """
        logger.info(f"Getting resolution strategy for denial type: {denial_type}")
        
        strategy = self.resolution_strategies.get(denial_type)
        
        if not strategy:
            logger.warning(f"No strategy found for denial type: {denial_type}")
            return {
                "status": "not_found",
                "message": f"No resolution strategy found for denial type: {denial_type}"
            }
        
        return {
            "status": "success",
            "denial_type": denial_type,
            "name": strategy.get("name", f"{denial_type.capitalize()} Resolution Strategy"),
            "description": strategy.get("description", ""),
            "general_steps": strategy.get("general_steps", []),
            "specific_strategies": strategy.get("specific_strategies", []),
            "documentation_requirements": strategy.get("documentation_requirements", [])
        }
    
    def list_incompatible_codes(self, code: str) -> Dict:
        """
        List all codes that are incompatible with a given code.
        
        Args:
            code: The procedure code to check
            
        Returns:
            Dict: List of incompatible codes and compatibility information
        """
        logger.info(f"Listing incompatible codes for: {code}")
        
        # Find all incompatible codes
        incompatible = []
        compatible_with_modifier = []
        
        # Check modifier not allowed pairs
        for key, pair_info in self.modifier_not_allowed_pairs.items():
            codes = key.split("_")
            if code in codes:
                other_code = codes[0] if codes[1] == code else codes[1]
                incompatible.append({
                    "code": other_code,
                    "resolution": pair_info.get("resolution_guidance", "These codes cannot be billed together"),
                    "documentation_requirements": pair_info.get("documentation_requirements", []),
                    "effective_date": pair_info.get("effective_date")
                })
        
        # Check modifier allowed pairs
        for key, pair_info in self.modifier_allowed_pairs.items():
            codes = key.split("_")
            if code in codes:
                other_code = codes[0] if codes[1] == code else codes[1]
                compatible_with_modifier.append({
                    "code": other_code,
                    "allowed_modifiers": self.allowed_modifiers,
                    "resolution": pair_info.get("resolution_guidance", "Use appropriate modifier"),
                    "documentation_requirements": pair_info.get("documentation_requirements", []),
                    "effective_date": pair_info.get("effective_date")
                })
        
        return {
            "status": "success",
            "code": code,
            "incompatible_codes": incompatible,
            "compatible_with_modifier_codes": compatible_with_modifier,
            "incompatible_count": len(incompatible),
            "compatible_with_modifier_count": len(compatible_with_modifier)
        }
