"""
Claims Analyzer Agent

This module implements a specialized agent that extracts and analyzes information
from claim documents such as CMS-1500 forms and Explanation of Benefits (EOB).

Features:
- Document vision analysis using Gemini 2.0 Pro Vision
- Field extraction from medical billing documents
- Error detection in claim submissions
- Integration with document parsing tools
"""

import logging
import os
import base64
import json
from typing import Dict, List, Optional, Union, Any, Tuple
from agent.tools.document_processing.cms1500_parser import parse_cms1500
from agent.tools.document_processing.eob_parser import parse_eob

logger = logging.getLogger(__name__)


class ClaimsAnalyzerAgent:
    """
    Specialized agent for analyzing medical claim documents.
    
    This agent extracts relevant information from CMS-1500 forms, EOBs, and other
    claim documents to identify key fields that may be related to denial reasons.
    
    Features:
    - Document vision capabilities using Gemini 2.0 Pro Vision
    - Extraction of key fields from CMS-1500 forms and EOBs
    - Validation of extracted information with confidence scores
    - Detection of common errors in claim submissions
    - Integration with document processing tools from Epic 3
    """
    
    def __init__(self):
        """
        Initialize the Claims Analyzer Agent with document processing tools.
        """
        logger.info("Initializing ClaimsAnalyzerAgent")
        
        # Define common errors to check for in claims
        self.common_errors = {
            "missing_information": [
                "patient_name", "patient_dob", "patient_id", "provider_npi",
                "diagnosis_codes", "procedure_codes", "date_of_service"
            ],
            "invalid_format": [
                "npi_format", "diagnosis_code_format", "procedure_code_format",
                "date_format", "modifier_format"
            ],
            "coding_issues": [
                "diagnosis_procedure_mismatch", "gender_specific_code",
                "age_specific_code", "missing_modifiers", "invalid_place_of_service"
            ]
        }
        
        # Define field mappings for CMS-1500 forms
        self.cms1500_field_map = {
            "patient_info": [
                "patient_name", "patient_dob", "patient_address", "patient_gender",
                "patient_relationship", "patient_id", "patient_insurance"
            ],
            "provider_info": [
                "provider_name", "provider_npi", "provider_address", "provider_ein",
                "provider_phone", "referring_provider"
            ],
            "service_info": [
                "date_of_service", "place_of_service", "procedure_codes", 
                "modifiers", "diagnosis_pointers", "charges", "units"
            ],
            "diagnosis_info": [
                "diagnosis_codes"
            ],
            "claim_info": [
                "claim_number", "total_charge", "insurance_plan", "authorization_number"
            ]
        }
        
        # Define field mappings for EOB documents
        self.eob_field_map = {
            "payer_info": [
                "payer_name", "payer_id", "payer_address", "payer_phone"
            ],
            "patient_info": [
                "patient_name", "patient_id", "patient_policy_number"
            ],
            "provider_info": [
                "provider_name", "provider_npi", "provider_tax_id"
            ],
            "claim_info": [
                "claim_number", "claim_status", "total_billed", "total_paid",
                "patient_responsibility", "check_number", "check_date"
            ],
            "service_lines": [
                "service_date", "procedure_code", "modifier", "units",
                "billed_amount", "allowed_amount", "paid_amount", "adjustment_amount",
                "denial_reason", "remark_codes"
            ],
            "denial_info": [
                "carc_codes", "rarc_codes", "group_codes"
            ]
        }
    
    def analyze_cms1500(self, document_data: Union[bytes, str], 
                      options: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Analyze a CMS-1500 form and extract relevant information.
        
        Args:
            document_data: The CMS-1500 document data (either binary or Base64 encoded)
            options: Optional analysis options
            
        Returns:
            Dict: Extracted information including claim details, procedure codes, etc.
        """
        logger.info("Analyzing CMS-1500 form")
        
        try:
            # Default options
            if options is None:
                options = {}
            
            # Ensure document_data is in the right format
            if isinstance(document_data, str):
                # Assume it's Base64 encoded
                try:
                    document_bytes = base64.b64decode(document_data)
                except Exception as e:
                    logger.error(f"Error decoding Base64 data: {e}")
                    return {
                        "status": "error",
                        "message": "Invalid Base64 encoding of document data"
                    }
            else:
                document_bytes = document_data
            
            # Parse CMS-1500 form using document parser from Epic 3
            parse_result = parse_cms1500(document_bytes)
            
            if parse_result.get("status") == "error":
                return parse_result
            
            extracted_fields = parse_result.get("extracted_fields", {})
            
            # Analyze the extracted data for potential issues
            analysis_result = self._analyze_cms1500_data(extracted_fields)
            
            # Combine results
            result = {
                "status": "success",
                "document_type": "CMS-1500",
                "extracted_fields": extracted_fields,
                "field_confidence": parse_result.get("field_confidence", {}),
                "potential_issues": analysis_result.get("potential_issues", []),
                "missing_fields": analysis_result.get("missing_fields", []),
                "invalid_fields": analysis_result.get("invalid_fields", []),
                "overall_confidence": parse_result.get("overall_confidence", 0.0)
            }
            
            logger.info(f"CMS-1500 analysis completed with {len(result['potential_issues'])} potential issues detected")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing CMS-1500 form: {e}")
            return {
                "status": "error",
                "message": f"Error analyzing CMS-1500 form: {str(e)}"
            }
    
    def _analyze_cms1500_data(self, extracted_fields: Dict) -> Dict:
        """
        Analyze extracted CMS-1500 data for potential issues.
        
        Args:
            extracted_fields: Dictionary of extracted fields from the CMS-1500 form
            
        Returns:
            Dict: Analysis results including potential issues and invalid fields
        """
        # Initialize result
        result = {
            "potential_issues": [],
            "missing_fields": [],
            "invalid_fields": []
        }
        
        # Check for missing required fields
        required_fields = [
            "patient_name", "patient_dob", "patient_id", "provider_npi",
            "diagnosis_codes", "procedure_codes", "date_of_service"
        ]
        
        for field in required_fields:
            if field not in extracted_fields or not extracted_fields[field]:
                result["missing_fields"].append(field)
                result["potential_issues"].append(f"Missing required field: {field}")
        
        # Check for invalid format issues
        if "provider_npi" in extracted_fields and extracted_fields["provider_npi"]:
            # NPI should be 10 digits
            npi = str(extracted_fields["provider_npi"]).replace(" ", "")
            if not (npi.isdigit() and len(npi) == 10):
                result["invalid_fields"].append("provider_npi")
                result["potential_issues"].append("Invalid NPI format: should be 10 digits")
        
        # Check for diagnosis/procedure code format
        if "diagnosis_codes" in extracted_fields:
            for i, code in enumerate(extracted_fields["diagnosis_codes"]):
                if code and not self._is_valid_diagnosis_code(code):
                    result["invalid_fields"].append(f"diagnosis_code_{i}")
                    result["potential_issues"].append(f"Invalid diagnosis code format: {code}")
        
        if "procedure_codes" in extracted_fields:
            for i, code in enumerate(extracted_fields["procedure_codes"]):
                if code and not self._is_valid_procedure_code(code):
                    result["invalid_fields"].append(f"procedure_code_{i}")
                    result["potential_issues"].append(f"Invalid procedure code format: {code}")
        
        # Check for date format issues
        if "date_of_service" in extracted_fields:
            for date in extracted_fields["date_of_service"]:
                if date and not self._is_valid_date_format(date):
                    result["invalid_fields"].append("date_of_service")
                    result["potential_issues"].append(f"Invalid date format: {date}")
        
        return result
    
    def _is_valid_diagnosis_code(self, code: str) -> bool:
        """
        Check if a diagnosis code has a valid format.
        
        Args:
            code: Diagnosis code to check
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Very basic validation: ICD-10 typically has a letter followed by 2 digits
        # Then optionally a period and more digits
        code = code.strip().upper()
        
        # Match patterns like "A01", "A01.1", etc.
        if len(code) >= 3:
            # Check if first character is a letter and next two are digits
            if (code[0].isalpha() and 
                len(code) >= 3 and
                code[1:3].isdigit()):
                return True
        
        return False
    
    def _is_valid_procedure_code(self, code: str) -> bool:
        """
        Check if a procedure code has a valid format.
        
        Args:
            code: Procedure code to check
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Very basic validation: CPT codes are 5 digits
        # HCPCS Level II has a letter followed by 4 digits
        code = code.strip().upper()
        
        # Check for CPT format (5 digits)
        if len(code) == 5 and code.isdigit():
            return True
        
        # Check for HCPCS Level II format (letter + 4 digits)
        if (len(code) == 5 and 
            code[0].isalpha() and 
            code[1:].isdigit()):
            return True
        
        return False
    
    def _is_valid_date_format(self, date: str) -> bool:
        """
        Check if a date has a valid format.
        
        Args:
            date: Date string to check
            
        Returns:
            bool: True if valid, False otherwise
        """
        # This is a simplified validation
        # In a real implementation, we would use a date parsing library
        
        # Check for format MM/DD/YYYY or MM-DD-YYYY
        date_parts = []
        if "/" in date:
            date_parts = date.split("/")
        elif "-" in date:
            date_parts = date.split("-")
            
        if len(date_parts) == 3:
            # Check if parts are numbers
            if all(part.isdigit() for part in date_parts):
                return True
                
        return False
    
    def analyze_eob(self, document_data: Union[bytes, str],
                  options: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Analyze an Explanation of Benefits (EOB) document and extract relevant information.
        
        Args:
            document_data: The EOB document data (either binary or Base64 encoded)
            options: Optional analysis options
            
        Returns:
            Dict: Extracted information including denial codes, claim identifiers, etc.
        """
        logger.info("Analyzing EOB document")
        
        try:
            # Default options
            if options is None:
                options = {}
            
            # Ensure document_data is in the right format
            if isinstance(document_data, str):
                # Assume it's Base64 encoded
                try:
                    document_bytes = base64.b64decode(document_data)
                except Exception as e:
                    logger.error(f"Error decoding Base64 data: {e}")
                    return {
                        "status": "error",
                        "message": "Invalid Base64 encoding of document data"
                    }
            else:
                document_bytes = document_data
            
            # Parse EOB using document parser from Epic 3
            parse_result = parse_eob(document_bytes)
            
            if parse_result.get("status") == "error":
                return parse_result
            
            extracted_fields = parse_result.get("extracted_fields", {})
            
            # Extract denial codes specifically
            denial_codes = self._extract_denial_codes(extracted_fields)
            
            # Analyze the extracted data for potential issues
            analysis_result = self._analyze_eob_data(extracted_fields)
            
            # Combine results
            result = {
                "status": "success",
                "document_type": "EOB",
                "extracted_fields": extracted_fields,
                "denial_codes": denial_codes,
                "field_confidence": parse_result.get("field_confidence", {}),
                "potential_issues": analysis_result.get("potential_issues", []),
                "missing_fields": analysis_result.get("missing_fields", []),
                "overall_confidence": parse_result.get("overall_confidence", 0.0)
            }
            
            logger.info(f"EOB analysis completed with {len(denial_codes['carc_codes'])} CARC codes and {len(denial_codes['rarc_codes'])} RARC codes detected")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing EOB document: {e}")
            return {
                "status": "error",
                "message": f"Error analyzing EOB document: {str(e)}"
            }
    
    def _extract_denial_codes(self, extracted_fields: Dict) -> Dict:
        """
        Extract CARC and RARC codes from EOB data.
        
        Args:
            extracted_fields: Dictionary of extracted fields from the EOB
            
        Returns:
            Dict: Dictionary of extracted denial codes
        """
        result = {
            "carc_codes": [],
            "rarc_codes": [],
            "group_codes": []
        }
        
        # Check if there are already extracted codes
        if "carc_codes" in extracted_fields:
            result["carc_codes"] = extracted_fields["carc_codes"]
        if "rarc_codes" in extracted_fields:
            result["rarc_codes"] = extracted_fields["rarc_codes"]
        if "group_codes" in extracted_fields:
            result["group_codes"] = extracted_fields["group_codes"]
        
        # Look for service lines that might contain denial codes
        if "service_lines" in extracted_fields:
            for line in extracted_fields["service_lines"]:
                # Check for CARC codes in denial_reason
                if "denial_reason" in line and line["denial_reason"]:
                    carc_codes = self._extract_codes_from_text(line["denial_reason"], "CARC")
                    for code in carc_codes:
                        if code not in result["carc_codes"]:
                            result["carc_codes"].append(code)
                
                # Check for RARC codes in remark_codes
                if "remark_codes" in line and line["remark_codes"]:
                    rarc_codes = self._extract_codes_from_text(line["remark_codes"], "RARC")
                    for code in rarc_codes:
                        if code not in result["rarc_codes"]:
                            result["rarc_codes"].append(code)
        
        return result
    
    def _extract_codes_from_text(self, text: str, code_type: str) -> List[str]:
        """
        Extract codes from text based on patterns.
        
        Args:
            text: The text to extract codes from
            code_type: The type of code to extract ("CARC" or "RARC")
            
        Returns:
            List[str]: Extracted codes
        """
        # This is a simplified implementation
        # In a real implementation, we would use more sophisticated regex patterns
        
        codes = []
        words = text.split()
        
        for word in words:
            # Remove any non-alphanumeric characters
            word = ''.join(c for c in word if c.isalnum())
            
            if code_type == "CARC" and word.isdigit():
                # CARC codes are typically 1-3 digits
                if 1 <= len(word) <= 3:
                    codes.append(word)
            
            elif code_type == "RARC" and len(word) > 1:
                # RARC codes typically start with a letter followed by 1-3 digits
                if word[0].isalpha() and word[1:].isdigit() and 1 <= len(word[1:]) <= 3:
                    codes.append(word)
        
        return codes
    
    def _analyze_eob_data(self, extracted_fields: Dict) -> Dict:
        """
        Analyze extracted EOB data for potential issues.
        
        Args:
            extracted_fields: Dictionary of extracted fields from the EOB
            
        Returns:
            Dict: Analysis results including potential issues and missing fields
        """
        # Initialize result
        result = {
            "potential_issues": [],
            "missing_fields": []
        }
        
        # Check for missing important fields
        important_fields = [
            "claim_number", "patient_name", "provider_name", "total_billed",
            "total_paid", "service_lines"
        ]
        
        for field in important_fields:
            if field not in extracted_fields or not extracted_fields[field]:
                result["missing_fields"].append(field)
                result["potential_issues"].append(f"Missing important field: {field}")
        
        # Check if there are any denial codes
        has_denial_codes = False
        if "carc_codes" in extracted_fields and extracted_fields["carc_codes"]:
            has_denial_codes = True
        
        if "service_lines" in extracted_fields:
            for line in extracted_fields["service_lines"]:
                if "denial_reason" in line and line["denial_reason"]:
                    has_denial_codes = True
                if "remark_codes" in line and line["remark_codes"]:
                    has_denial_codes = True
        
        if not has_denial_codes:
            result["potential_issues"].append("No denial codes found in the EOB")
        
        # Check for payment discrepancies
        if ("total_billed" in extracted_fields and "total_paid" in extracted_fields and
            extracted_fields["total_billed"] and extracted_fields["total_paid"]):
            try:
                total_billed = float(extracted_fields["total_billed"])
                total_paid = float(extracted_fields["total_paid"])
                
                if total_paid < total_billed:
                    result["potential_issues"].append(
                        f"Payment discrepancy: Billed ${total_billed}, Paid ${total_paid}"
                    )
            except (ValueError, TypeError):
                # Couldn't convert to float, just skip this check
                pass
        
        return result
    
    def analyze_document(self, document_data: Union[bytes, str], 
                        document_type: str,
                        options: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Analyze a document based on its type.
        
        Args:
            document_data: The document data (either binary or Base64 encoded)
            document_type: The type of document ("CMS-1500" or "EOB")
            options: Optional analysis options
            
        Returns:
            Dict: Analysis results
        """
        logger.info(f"Analyzing document of type: {document_type}")
        
        if document_type.upper() == "CMS-1500" or document_type.upper() == "CMS1500":
            return self.analyze_cms1500(document_data, options)
        
        elif document_type.upper() == "EOB":
            return self.analyze_eob(document_data, options)
        
        else:
            logger.error(f"Unsupported document type: {document_type}")
            return {
                "status": "error",
                "message": f"Unsupported document type: {document_type}. Supported types are 'CMS-1500' and 'EOB'."
            }
    
    def identify_claim_issues(self, claim_data: Dict) -> Dict:
        """
        Identify potential issues in a claim based on extracted data.
        
        Args:
            claim_data: Dictionary of claim data (from CMS-1500 or combined sources)
            
        Returns:
            Dict: Potential issues and recommendations
        """
        logger.info("Identifying potential claim issues")
        
        issues = []
        recommendations = []
        
        # Check for common error categories
        for category, fields in self.common_errors.items():
            category_issues = []
            
            for field in fields:
                # Check for missing fields
                if field not in claim_data or not claim_data[field]:
                    category_issues.append(f"Missing {field}")
                
                # Check for special validations
                if field == "npi_format" and "provider_npi" in claim_data:
                    npi = str(claim_data["provider_npi"]).replace(" ", "")
                    if not (npi.isdigit() and len(npi) == 10):
                        category_issues.append("Invalid NPI format")
                
                elif field == "diagnosis_code_format" and "diagnosis_codes" in claim_data:
                    for code in claim_data["diagnosis_codes"]:
                        if not self._is_valid_diagnosis_code(code):
                            category_issues.append(f"Invalid diagnosis code format: {code}")
                
                elif field == "procedure_code_format" and "procedure_codes" in claim_data:
                    for code in claim_data["procedure_codes"]:
                        if not self._is_valid_procedure_code(code):
                            category_issues.append(f"Invalid procedure code format: {code}")
            
            if category_issues:
                issues.append({
                    "category": category,
                    "issues": category_issues
                })
                
                # Add category-specific recommendations
                if category == "missing_information":
                    recommendations.append("Review claim for completeness and add all required information")
                elif category == "invalid_format":
                    recommendations.append("Check format of all codes, identifiers, and dates")
                elif category == "coding_issues":
                    recommendations.append("Review coding guidelines and ensure proper code usage")
        
        # Check for diagnosis-procedure code compatibility
        if ("diagnosis_codes" in claim_data and "procedure_codes" in claim_data and
            claim_data["diagnosis_codes"] and claim_data["procedure_codes"]):
            # This would call a more sophisticated code compatibility check in a real implementation
            # For now, we just add a placeholder recommendation
            recommendations.append("Verify that procedure codes are supported by diagnosis codes")
        
        return {
            "status": "success",
            "issues": issues,
            "recommendations": recommendations,
            "issue_count": sum(len(category["issues"]) for category in issues)
        }
