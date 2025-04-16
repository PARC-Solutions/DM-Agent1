"""
PHI Detection System

This module implements functionality to detect Protected Health Information (PHI)
in text data to ensure HIPAA compliance in the Medical Billing Denial Agent system.

Features:
- Pattern-based PHI detection
- Confidence scoring
- PHI categorization
- Redaction capabilities
"""

import re
import logging
import json
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class PHIDetection:
    """
    Represents a detected PHI element.
    
    This class stores information about a detected PHI element,
    including its category, the detected text, position, and confidence.
    """
    category: str
    text: str
    start_pos: int
    end_pos: int
    confidence: float
    pattern_name: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the detection to a dictionary."""
        return {
            "category": self.category,
            "text": self.text,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "confidence": self.confidence,
            "pattern_name": self.pattern_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PHIDetection':
        """Create a detection from a dictionary."""
        return cls(
            category=data["category"],
            text=data["text"],
            start_pos=data["start_pos"],
            end_pos=data["end_pos"],
            confidence=data["confidence"],
            pattern_name=data.get("pattern_name", "")
        )


class PHIDetector:
    """
    Detects Protected Health Information (PHI) in text.
    
    This class provides methods to detect, categorize, and redact PHI
    in text data to ensure HIPAA compliance.
    """
    
    def __init__(self, 
                custom_patterns: Optional[Dict[str, Dict[str, Any]]] = None,
                confidence_threshold: float = 0.6):
        """
        Initialize the PHI detector.
        
        Args:
            custom_patterns: Optional dictionary of custom detection patterns
            confidence_threshold: Threshold for considering a detection valid
        """
        self.confidence_threshold = confidence_threshold
        self.phi_patterns = self._get_default_patterns()
        
        # Add any custom patterns
        if custom_patterns:
            for name, pattern_info in custom_patterns.items():
                self.phi_patterns[name] = pattern_info
                
        # Compile all regex patterns
        for name, pattern_info in self.phi_patterns.items():
            if "regex" in pattern_info and isinstance(pattern_info["regex"], str):
                try:
                    pattern_info["compiled_regex"] = re.compile(pattern_info["regex"], re.IGNORECASE)
                except re.error as e:
                    logger.error(f"Error compiling regex pattern '{name}': {e}")
    
    def _get_default_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the default PHI detection patterns.
        
        Returns:
            Dictionary of pattern definitions
        """
        return {
            # Patient identifiers
            "name": {
                "category": "PATIENT_NAME",
                "regex": r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b",
                "confidence": 0.7,
                "context_boost": [
                    r"\bpatient\b", r"\bname\b", r"\bclient\b", 
                    r"\bMr\.?\b", r"\bMs\.?\b", r"\bMrs\.?\b", r"\bDr\.?\b"
                ]
            },
            "ssn": {
                "category": "SSN",
                "regex": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
                "confidence": 0.9,
                "context_boost": [
                    r"\bssn\b", r"\bsocial security\b", r"\bsoc sec\b"
                ]
            },
            "mrn": {
                "category": "MEDICAL_RECORD_NUMBER",
                "regex": r"\b(MRN|Medical Record)[-:\s]+([A-Z0-9]{6,10})\b",
                "confidence": 0.9,
                "context_boost": [
                    r"\bmrn\b", r"\bmedical record\b", r"\brecord number\b"
                ]
            },
            "date_of_birth": {
                "category": "DATE_OF_BIRTH",
                "regex": r"\b(0?[1-9]|1[0-2])[\/\-](0?[1-9]|[12]\d|3[01])[\/\-](19|20)\d{2}\b",
                "confidence": 0.8,
                "context_boost": [
                    r"\bdob\b", r"\bdate of birth\b", r"\bbirthday\b", r"\bborn\b"
                ]
            },
            "address": {
                "category": "ADDRESS",
                "regex": r"\b\d+\s+[A-Za-z0-9\s,\.]+\b(Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Ln|Rd|Blvd|Dr|St)\b",
                "confidence": 0.8,
                "context_boost": [
                    r"\baddress\b", r"\blives at\b", r"\bresides at\b", r"\bhome\b"
                ]
            },
            "phone": {
                "category": "PHONE_NUMBER",
                "regex": r"\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
                "confidence": 0.8,
                "context_boost": [
                    r"\bphone\b", r"\bcall\b", r"\btel\b", r"\btelephone\b"
                ]
            },
            
            # Insurance identifiers
            "insurance_id": {
                "category": "INSURANCE_ID",
                "regex": r"\b([A-Z]{3,5}[-\s]?\d{5,12})\b",
                "confidence": 0.7,
                "context_boost": [
                    r"\binsurance\b", r"\bpolicy\b", r"\bmember\b", r"\bid\b"
                ]
            },
            "group_number": {
                "category": "GROUP_NUMBER",
                "regex": r"\b(Group|GRP)[-:\s]+([A-Z0-9]{5,12})\b",
                "confidence": 0.8,
                "context_boost": [
                    r"\bgroup\b", r"\bgrp\b", r"\bplan\b"
                ]
            },
            
            # Medical information
            "diagnosis_code": {
                "category": "DIAGNOSIS_CODE",
                "regex": r"\b([A-Z]\d{2}(?:\.\d{1,2})?)\b",
                "confidence": 0.6,
                "context_boost": [
                    r"\bicd\b", r"\bdiagnosis\b", r"\bdx\b", r"\bcondition\b"
                ]
            },
            "procedure_code": {
                "category": "PROCEDURE_CODE",
                "regex": r"\b\d{5}(?:\-[A-Z0-9]{2})?\b",
                "confidence": 0.6,
                "context_boost": [
                    r"\bcpt\b", r"\bprocedure\b", r"\bhcpcs\b", r"\bservice\b"
                ]
            }
        }
    
    def _check_context_boost(self, text: str, pattern_info: Dict[str, Any], 
                           match_start: int, match_end: int) -> float:
        """
        Check if the context around a match increases confidence.
        
        Args:
            text: Full text being analyzed
            pattern_info: Pattern information
            match_start: Start position of the match
            match_end: End position of the match
            
        Returns:
            Confidence boost amount
        """
        if "context_boost" not in pattern_info:
            return 0.0
            
        # Extract context window (50 chars before and after)
        context_start = max(0, match_start - 50)
        context_end = min(len(text), match_end + 50)
        context = text[context_start:context_end].lower()
        
        # Check for boosting terms
        boost = 0.0
        for boost_pattern in pattern_info["context_boost"]:
            if re.search(boost_pattern, context, re.IGNORECASE):
                boost += 0.1  # Add 0.1 for each context match
                
        return min(boost, 0.3)  # Cap the boost at 0.3
    
    def detect_phi(self, text: str) -> List[PHIDetection]:
        """
        Detect PHI in the provided text.
        
        Args:
            text: Text to analyze for PHI
            
        Returns:
            List of PHI detections
        """
        if not text:
            return []
            
        detections = []
        
        # Apply each pattern
        for name, pattern_info in self.phi_patterns.items():
            if "compiled_regex" not in pattern_info:
                continue
                
            regex = pattern_info["compiled_regex"]
            base_confidence = pattern_info.get("confidence", 0.5)
            category = pattern_info["category"]
            
            # Find all matches
            for match in regex.finditer(text):
                match_text = match.group(0)
                start_pos = match.start()
                end_pos = match.end()
                
                # Calculate confidence with context boost
                confidence = base_confidence
                context_boost = self._check_context_boost(text, pattern_info, start_pos, end_pos)
                confidence += context_boost
                
                # Only include if confidence is above threshold
                if confidence >= self.confidence_threshold:
                    detection = PHIDetection(
                        category=category,
                        text=match_text,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        confidence=confidence,
                        pattern_name=name
                    )
                    detections.append(detection)
        
        # Sort by position
        detections.sort(key=lambda d: d.start_pos)
        
        return detections
    
    def has_phi(self, text: str) -> bool:
        """
        Check if the text contains any PHI.
        
        Args:
            text: Text to check
            
        Returns:
            True if PHI is detected, False otherwise
        """
        detections = self.detect_phi(text)
        return len(detections) > 0
    
    def redact_phi(self, text: str, replacement: str = "[REDACTED]") -> str:
        """
        Redact PHI from the text.
        
        Args:
            text: Text to redact
            replacement: String to replace PHI with
            
        Returns:
            Redacted text
        """
        detections = self.detect_phi(text)
        if not detections:
            return text
            
        # Build redacted text from back to front to maintain positions
        redacted_text = text
        for detection in reversed(detections):
            redacted_text = (
                redacted_text[:detection.start_pos] + 
                replacement + 
                redacted_text[detection.end_pos:]
            )
            
        return redacted_text
    
    def redact_phi_by_category(self, text: str, 
                             category_replacements: Dict[str, str] = None) -> str:
        """
        Redact PHI from the text with category-specific replacements.
        
        Args:
            text: Text to redact
            category_replacements: Dictionary mapping categories to replacement strings
            
        Returns:
            Redacted text
        """
        if category_replacements is None:
            category_replacements = {
                "PATIENT_NAME": "[NAME]",
                "SSN": "[SSN]",
                "MEDICAL_RECORD_NUMBER": "[MRN]",
                "DATE_OF_BIRTH": "[DOB]",
                "ADDRESS": "[ADDRESS]",
                "PHONE_NUMBER": "[PHONE]",
                "INSURANCE_ID": "[INSURANCE ID]",
                "GROUP_NUMBER": "[GROUP NUMBER]",
                "DIAGNOSIS_CODE": "[DIAGNOSIS]",
                "PROCEDURE_CODE": "[PROCEDURE]"
            }
            
        detections = self.detect_phi(text)
        if not detections:
            return text
            
        # Build redacted text from back to front to maintain positions
        redacted_text = text
        for detection in reversed(detections):
            replacement = category_replacements.get(
                detection.category, "[REDACTED]"
            )
            redacted_text = (
                redacted_text[:detection.start_pos] + 
                replacement + 
                redacted_text[detection.end_pos:]
            )
            
        return redacted_text
    
    def summarize_phi(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Provide a summary of detected PHI.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping categories to lists of detected PHI
        """
        detections = self.detect_phi(text)
        if not detections:
            return {}
            
        summary = {}
        for detection in detections:
            if detection.category not in summary:
                summary[detection.category] = []
                
            summary[detection.category].append({
                "text": detection.text,
                "confidence": detection.confidence
            })
            
        return summary
    
    def add_pattern(self, name: str, pattern_info: Dict[str, Any]) -> None:
        """
        Add a new PHI detection pattern.
        
        Args:
            name: Pattern name
            pattern_info: Pattern definition
        """
        if "regex" not in pattern_info:
            raise ValueError("Pattern must include a regex")
            
        if "category" not in pattern_info:
            raise ValueError("Pattern must include a category")
            
        # Set defaults
        if "confidence" not in pattern_info:
            pattern_info["confidence"] = 0.5
            
        # Compile the regex
        try:
            pattern_info["compiled_regex"] = re.compile(pattern_info["regex"], re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
            
        self.phi_patterns[name] = pattern_info
        logger.info(f"Added PHI detection pattern: {name}")
    
    def remove_pattern(self, name: str) -> None:
        """
        Remove a PHI detection pattern.
        
        Args:
            name: Pattern name to remove
        """
        if name in self.phi_patterns:
            del self.phi_patterns[name]
            logger.info(f"Removed PHI detection pattern: {name}")

# Create a singleton instance
default_phi_detector = PHIDetector()
