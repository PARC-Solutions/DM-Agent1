"""
Content Moderation System

This module implements content moderation for agent responses in the Medical Billing 
Denial Agent system, ensuring HIPAA compliance, filtering inappropriate content,
and maintaining appropriate language and tone.

Features:
- PHI detection and handling
- Inappropriate content filtering
- Response standardization
- Disclaimer and warning addition
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from agent.security.phi_detector import default_phi_detector, PHIDetector

logger = logging.getLogger(__name__)

class ContentModerator:
    """
    Moderates content for HIPAA compliance and appropriate responses.
    
    This class provides methods to detect and handle PHI, filter inappropriate content,
    and ensure responses maintain an appropriate professional tone.
    """
    
    def __init__(self, 
                phi_detector: Optional[PHIDetector] = None,
                add_disclaimers: bool = True,
                redact_phi: bool = True):
        """
        Initialize the content moderator.
        
        Args:
            phi_detector: PHI detector to use
            add_disclaimers: Whether to add disclaimers to responses
            redact_phi: Whether to redact PHI from responses
        """
        self.phi_detector = phi_detector or default_phi_detector
        self.add_disclaimers = add_disclaimers
        self.redact_phi = redact_phi
        
        # Initialize content filters
        self._initialize_content_filters()
        
        # Initialize disclaimer templates
        self._initialize_disclaimer_templates()
    
    def _initialize_content_filters(self):
        """Initialize content filter patterns."""
        # Define inappropriate content patterns
        self.inappropriate_patterns = {
            "profanity": re.compile(
                r'\b(damn|crap|hell|ass|asshole|fucking|fuck|shit|bullshit|bitch)\b', 
                re.IGNORECASE
            ),
            "personal_opinions": re.compile(
                r'\b(I think|I believe|In my opinion|I feel|I would)\b',
                re.IGNORECASE
            ),
            "non_professional": re.compile(
                r'\b(lol|haha|cool|awesome|wow|omg|oh my god|geez|gosh)\b',
                re.IGNORECASE
            ),
            "certainty_language": re.compile(
                r'\b(always|never|guaranteed|certainly|definitely|absolutely|100\%)\b',
                re.IGNORECASE
            ),
            "medical_advice": re.compile(
                r'\b(you should|you need to|you must|should take|recommend|prescribed|diagnosis|treatment|therapy)\b',
                re.IGNORECASE
            )
        }
        
        # Define content categories for tagging
        self.content_categories = {
            "medical_information": re.compile(
                r'\b(diagnosis|treatment|medical condition|symptoms|procedure|medication|drugs|prescription|therapy)\b',
                re.IGNORECASE
            ),
            "billing_advice": re.compile(
                r'\b(appeal|refile|resubmit|corrected claim|denial reason|modifier|code|billing|submit|claim)\b',
                re.IGNORECASE
            ),
            "legal_references": re.compile(
                r'\b(regulation|compliance|law|legal|statute|requirement|HIPAA|CMS rule|mandate)\b',
                re.IGNORECASE
            )
        }
    
    def _initialize_disclaimer_templates(self):
        """Initialize disclaimer templates for different content types."""
        self.disclaimers = {
            "medical_information": (
                "\n\nDISCLAIMER: The information provided is for general informational purposes "
                "only and should not be considered medical advice. Please consult with appropriate "
                "healthcare professionals for specific medical guidance."
            ),
            "billing_advice": (
                "\n\nDISCLAIMER: The billing guidance provided is based on general billing practices "
                "and may not account for specific payer requirements or exceptions. Always verify "
                "information with the specific payer or consult with certified billing specialists."
            ),
            "legal_references": (
                "\n\nDISCLAIMER: This information is not legal advice. Regulatory requirements may "
                "vary by jurisdiction and are subject to change. Consult with qualified legal counsel "
                "for specific legal questions."
            ),
            "general": (
                "\n\nDISCLAIMER: This information is provided for general guidance only and may not "
                "address all aspects of your specific situation."
            )
        }
    
    def _detect_content_categories(self, text: str) -> Set[str]:
        """
        Detect content categories in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Set of detected categories
        """
        categories = set()
        
        for category, pattern in self.content_categories.items():
            if pattern.search(text):
                categories.add(category)
                
        return categories
    
    def _filter_inappropriate_content(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Filter inappropriate content from text.
        
        Args:
            text: Text to filter
            
        Returns:
            Tuple of (filtered text, list of filter matches)
        """
        filter_matches = []
        filtered_text = text
        
        # Check for inappropriate patterns
        for filter_type, pattern in self.inappropriate_patterns.items():
            for match in pattern.finditer(text):
                filter_matches.append({
                    "type": filter_type,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end()
                })
                
        # Replace profanity
        if any(match["type"] == "profanity" for match in filter_matches):
            filtered_text = self.inappropriate_patterns["profanity"].sub("[inappropriate term]", filtered_text)
            
        # Don't replace other types, just log them for review
        
        return filtered_text, filter_matches
    
    def _add_appropriate_disclaimers(self, text: str, categories: Set[str]) -> str:
        """
        Add appropriate disclaimers based on content categories.
        
        Args:
            text: Text to add disclaimers to
            categories: Content categories detected
            
        Returns:
            Text with added disclaimers
        """
        if not self.add_disclaimers:
            return text
            
        # Determine which disclaimers to add
        disclaimers_to_add = set()
        for category in categories:
            if category in self.disclaimers:
                disclaimers_to_add.add(self.disclaimers[category])
                
        # Add general disclaimer if no specific ones apply
        if not disclaimers_to_add and "general" in self.disclaimers:
            disclaimers_to_add.add(self.disclaimers["general"])
            
        # Add disclaimers to text
        text_with_disclaimers = text
        for disclaimer in disclaimers_to_add:
            if disclaimer not in text_with_disclaimers:
                text_with_disclaimers += disclaimer
                
        return text_with_disclaimers
    
    def _standardize_formatting(self, text: str) -> str:
        """
        Standardize response formatting.
        
        Args:
            text: Text to standardize
            
        Returns:
            Standardized text
        """
        # Ensure proper heading formatting
        section_headings = {
            "STEPS TO RESOLVE:": r"(?i)\b(steps?[ \t]+to[ \t]+resolve|resolution[ \t]+steps?)\b\s*:?",
            "DENIAL ANALYSIS:": r"(?i)\b(denial[ \t]+analysis|analyzing[ \t]+the[ \t]+denial)\b\s*:?",
            "EXPLANATION:": r"(?i)\b(explanation|explaining)\b\s*:?",
            "REFERENCES:": r"(?i)\b(references|sources|further[ \t]+information)\b\s*:?"
        }
        
        for standard_heading, pattern in section_headings.items():
            # Check if we have this section but not with standard formatting
            if re.search(pattern, text) and standard_heading not in text:
                text = re.sub(pattern, standard_heading, text)
                
        # Ensure proper list formatting
        if "STEPS TO RESOLVE:" in text and not re.search(r'\d+\.\s+', text):
            lines = text.split('\n')
            in_steps_section = False
            numbered_lines = []
            
            step_num = 1
            for line in lines:
                if "STEPS TO RESOLVE:" in line:
                    in_steps_section = True
                    numbered_lines.append(line)
                elif in_steps_section and line.strip() and not line.strip().startswith('-'):
                    if re.match(r'^\d+\.\s+', line):
                        numbered_lines.append(line)
                    else:
                        numbered_lines.append(f"{step_num}. {line}")
                        step_num += 1
                else:
                    numbered_lines.append(line)
                    if line.strip() == "" and in_steps_section:
                        in_steps_section = False
                        
            text = '\n'.join(numbered_lines)
            
        return text
    
    def moderate_response(self, response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Moderate a response for compliance and appropriateness.
        
        Args:
            response: Response text to moderate
            context: Optional context information
            
        Returns:
            Dictionary containing moderated response and moderation details
        """
        context = context or {}
        moderation_result = {
            "original_response": response,
            "moderated_response": response,
            "moderation_details": {
                "phi_detected": False,
                "inappropriate_content": False,
                "disclaimers_added": False,
                "formatting_standardized": False,
                "categories": [],
                "filter_matches": []
            }
        }
        
        # Step 1: Detect and handle PHI
        if self.redact_phi:
            phi_detections = self.phi_detector.detect_phi(response)
            if phi_detections:
                moderation_result["moderation_details"]["phi_detected"] = True
                moderation_result["moderation_details"]["phi_detection"] = [
                    detection.to_dict() for detection in phi_detections
                ]
                moderated_text = self.phi_detector.redact_phi_by_category(response)
                moderation_result["moderated_response"] = moderated_text
            else:
                moderated_text = response
        else:
            moderated_text = response
        
        # Step 2: Filter inappropriate content
        filtered_text, filter_matches = self._filter_inappropriate_content(moderated_text)
        if filter_matches:
            moderation_result["moderation_details"]["inappropriate_content"] = True
            moderation_result["moderation_details"]["filter_matches"] = filter_matches
            moderation_result["moderated_response"] = filtered_text
        else:
            filtered_text = moderated_text
        
        # Step 3: Detect content categories
        categories = self._detect_content_categories(filtered_text)
        if categories:
            moderation_result["moderation_details"]["categories"] = list(categories)
        
        # Step 4: Add appropriate disclaimers
        text_with_disclaimers = self._add_appropriate_disclaimers(filtered_text, categories)
        if text_with_disclaimers != filtered_text:
            moderation_result["moderation_details"]["disclaimers_added"] = True
            moderation_result["moderated_response"] = text_with_disclaimers
        else:
            text_with_disclaimers = filtered_text
        
        # Step 5: Standardize formatting
        standardized_text = self._standardize_formatting(text_with_disclaimers)
        if standardized_text != text_with_disclaimers:
            moderation_result["moderation_details"]["formatting_standardized"] = True
            moderation_result["moderated_response"] = standardized_text
        
        # Log moderation actions if significant changes were made
        if moderation_result["moderated_response"] != response:
            logger.info(f"Response moderated with actions: {moderation_result['moderation_details']}")
        
        return moderation_result

    def check_medical_advice(self, text: str) -> bool:
        """
        Check if text contains medical advice.
        
        Args:
            text: Text to check
            
        Returns:
            True if medical advice is detected, False otherwise
        """
        medical_advice_pattern = self.inappropriate_patterns.get("medical_advice")
        return bool(medical_advice_pattern and medical_advice_pattern.search(text))
    
    def check_certainty_language(self, text: str) -> bool:
        """
        Check if text contains inappropriate certainty language.
        
        Args:
            text: Text to check
            
        Returns:
            True if certainty language is detected, False otherwise
        """
        certainty_pattern = self.inappropriate_patterns.get("certainty_language")
        return bool(certainty_pattern and certainty_pattern.search(text))

# Create a singleton instance
default_content_moderator = ContentModerator()
