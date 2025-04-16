"""
Tests for the security components.

This module contains tests for the security components used to ensure
HIPAA compliance, content moderation, and error handling in the Medical
Billing Denial Agent.
"""

import pytest
import json
import re
from unittest.mock import MagicMock, patch
import time

from agent.security.encryption import EncryptionManager
from agent.security.phi_detector import PHIDetector, PHIDetection
from agent.security.content_moderation import ContentModerator
from agent.security.error_handler import (
    ErrorHandler, FallbackSystem, ErrorSeverity, 
    ErrorCategory, ErrorDetails, safe_execution_decorator
)


class TestEncryptionManager:
    """Tests for the EncryptionManager class."""
    
    def test_initialization(self):
        """Test initialization of encryption manager."""
        # Test with auto-generated key
        with patch('os.getenv', return_value=None):
            encryption_manager = EncryptionManager(auto_generate_key=True)
            assert encryption_manager.key is not None
            assert encryption_manager.cipher_suite is not None
            
        # Test with environment key
        with patch('os.getenv', return_value="valid_key_in_env"):
            with patch('agent.security.encryption.Fernet'):
                encryption_manager = EncryptionManager(use_env_key=True)
                assert encryption_manager.key is not None
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption of data."""
        encryption_manager = EncryptionManager(auto_generate_key=True)
        
        # Test with string
        original_text = "This is sensitive information"
        encrypted_package = encryption_manager.encrypt(original_text)
        
        # Check package structure
        assert "encrypted_data" in encrypted_package
        assert "encryption_timestamp" in encrypted_package
        assert "encryption_version" in encrypted_package
        
        # Decrypt and check
        decrypted = encryption_manager.decrypt(encrypted_package)
        assert decrypted == original_text
        
        # Test with dictionary
        original_dict = {"key1": "value1", "key2": 123}
        encrypted_package = encryption_manager.encrypt(original_dict)
        decrypted = encryption_manager.decrypt(encrypted_package)
        assert decrypted == original_dict
    
    def test_encrypt_decrypt_field(self):
        """Test encryption and decryption of a field."""
        encryption_manager = EncryptionManager(auto_generate_key=True)
        
        # Encrypt a field
        original_value = "Patient name"
        encrypted_field = encryption_manager.encrypt_field(original_value)
        
        # Should be a JSON string
        assert isinstance(encrypted_field, str)
        package = json.loads(encrypted_field)
        assert "encrypted_data" in package
        
        # Decrypt and check
        decrypted = encryption_manager.decrypt_field(encrypted_field)
        assert decrypted == original_value
    
    def test_encrypt_decrypt_document(self):
        """Test encryption and decryption of a document with sensitive fields."""
        encryption_manager = EncryptionManager(auto_generate_key=True)
        
        # Create a document with sensitive information
        document = {
            "patient_name": "John Doe",
            "patient_id": "12345",
            "dob": "01/01/1970",
            "address": "123 Main St, Anytown, USA",
            "diagnosis": "Test diagnosis",
            "non_sensitive_field": "Regular information"
        }
        
        # Encrypt the document
        encrypted_doc = encryption_manager.encrypt_document(document)
        
        # Check that sensitive fields are encrypted
        for field in ["patient_name", "patient_id", "dob", "address", "diagnosis"]:
            assert isinstance(encrypted_doc[field], dict)
            assert encrypted_doc[field]["encrypted"] is True
            assert "value" in encrypted_doc[field]
            
        # Non-sensitive fields should be unchanged
        assert encrypted_doc["non_sensitive_field"] == "Regular information"
        
        # Decrypt the document
        decrypted_doc = encryption_manager.decrypt_document(encrypted_doc)
        
        # Original document should be restored
        for key, value in document.items():
            assert decrypted_doc[key] == value
    
    def test_rotate_key(self):
        """Test key rotation."""
        encryption_manager = EncryptionManager(auto_generate_key=True)
        
        # Save original key
        original_key = encryption_manager.key
        
        # Encrypt some data with the original key
        original_text = "This is sensitive information"
        encrypted_package = encryption_manager.encrypt(original_text)
        
        # Rotate the key
        new_key = encryption_manager.rotate_key()
        
        # Original key should be different from new key
        assert original_key != new_key
        
        # Trying to decrypt the original data should fail
        # This is because the cipher suite has been updated
        with pytest.raises(Exception):
            encryption_manager.decrypt(encrypted_package)


class TestPHIDetector:
    """Tests for the PHIDetector class."""
    
    def test_initialization(self):
        """Test initialization of PHI detector."""
        detector = PHIDetector()
        assert detector.confidence_threshold == 0.6
        assert isinstance(detector.phi_patterns, dict)
        
        # Custom threshold
        detector = PHIDetector(confidence_threshold=0.8)
        assert detector.confidence_threshold == 0.8
    
    def test_detect_phi_patient_name(self):
        """Test detection of patient names."""
        detector = PHIDetector()
        
        # Test with a patient name
        text = "The patient John Smith was admitted yesterday."
        detections = detector.detect_phi(text)
        
        # Should detect John Smith as a patient name
        assert len(detections) > 0
        assert any(d.category == "PATIENT_NAME" for d in detections)
        assert any(d.text == "John Smith" for d in detections)
        
        # Test with name in context
        text = "Patient name: Jane Doe"
        detections = detector.detect_phi(text)
        
        # Should detect with higher confidence due to context
        assert len(detections) > 0
        assert any(d.category == "PATIENT_NAME" and d.text == "Jane Doe" for d in detections)
    
    def test_detect_phi_ssn(self):
        """Test detection of SSNs."""
        detector = PHIDetector()
        
        # Test with SSN in different formats
        formats = [
            "SSN: 123-45-6789", 
            "Social Security: 123 45 6789",
            "SSN 123456789"
        ]
        
        for text in formats:
            detections = detector.detect_phi(text)
            assert len(detections) > 0
            assert any(d.category == "SSN" for d in detections)
    
    def test_has_phi(self):
        """Test checking if text has PHI."""
        detector = PHIDetector()
        
        # Test with PHI
        assert detector.has_phi("Patient: John Doe, DOB: 01/01/1970") is True
        
        # Test without PHI
        assert detector.has_phi("General medical information about treatments.") is False
    
    def test_redact_phi(self):
        """Test redacting PHI from text."""
        detector = PHIDetector()
        
        # Test redaction
        text = "Patient John Doe (DOB: 01/01/1970) lives at 123 Main St."
        redacted = detector.redact_phi(text)
        
        # Names, dates, and addresses should be redacted
        assert "John Doe" not in redacted
        assert "01/01/1970" not in redacted
        assert "123 Main St" not in redacted
        assert "[REDACTED]" in redacted
    
    def test_redact_phi_by_category(self):
        """Test redacting PHI by category."""
        detector = PHIDetector()
        
        # Test category-specific redaction
        text = "Patient John Doe (DOB: 01/01/1970, SSN: 123-45-6789)"
        redacted = detector.redact_phi_by_category(text)
        
        # Should use category-specific replacements
        assert "[NAME]" in redacted
        assert "[DOB]" in redacted
        assert "[SSN]" in redacted
        
        # Custom replacements
        custom_replacements = {
            "PATIENT_NAME": "<<NAME>>",
            "DATE_OF_BIRTH": "<<DOB>>",
            "SSN": "<<SSN>>"
        }
        
        redacted_custom = detector.redact_phi_by_category(text, custom_replacements)
        assert "<<NAME>>" in redacted_custom
        assert "<<DOB>>" in redacted_custom
        assert "<<SSN>>" in redacted_custom
    
    def test_add_remove_pattern(self):
        """Test adding and removing detection patterns."""
        detector = PHIDetector()
        
        # Add a new pattern
        detector.add_pattern(
            "test_pattern",
            {
                "category": "TEST_CATEGORY",
                "regex": r"TEST-\d{3}",
                "confidence": 0.9
            }
        )
        
        # Test detection with new pattern
        text = "This contains a test code: TEST-123"
        detections = detector.detect_phi(text)
        
        # Should detect with the new pattern
        assert any(d.category == "TEST_CATEGORY" and d.text == "TEST-123" for d in detections)
        
        # Remove the pattern
        detector.remove_pattern("test_pattern")
        
        # Test detection after removal
        detections = detector.detect_phi(text)
        
        # Should not detect anymore
        assert not any(d.category == "TEST_CATEGORY" for d in detections)


class TestContentModerator:
    """Tests for the ContentModerator class."""
    
    def test_initialization(self):
        """Test initialization of content moderator."""
        # Test with default settings
        moderator = ContentModerator()
        assert moderator.add_disclaimers is True
        assert moderator.redact_phi is True
        assert moderator.phi_detector is not None
        
        # Test with custom settings
        phi_detector = MagicMock(spec=PHIDetector)
        moderator = ContentModerator(
            phi_detector=phi_detector,
            add_disclaimers=False,
            redact_phi=False
        )
        assert moderator.phi_detector is phi_detector
        assert moderator.add_disclaimers is False
        assert moderator.redact_phi is False
    
    def test_detect_content_categories(self):
        """Test detection of content categories."""
        moderator = ContentModerator()
        
        # Test medical information
        medical_text = "This patient's diagnosis requires treatment with medication."
        categories = moderator._detect_content_categories(medical_text)
        assert "medical_information" in categories
        
        # Test billing advice
        billing_text = "You should refile the claim with the correct modifier code."
        categories = moderator._detect_content_categories(billing_text)
        assert "billing_advice" in categories
        
        # Test legal references
        legal_text = "According to HIPAA regulations, you must ensure compliance."
        categories = moderator._detect_content_categories(legal_text)
        assert "legal_references" in categories
        
        # Test multiple categories
        mixed_text = "The diagnosis requires treatment and you should refile the claim per HIPAA regulations."
        categories = moderator._detect_content_categories(mixed_text)
        assert "medical_information" in categories
        assert "billing_advice" in categories
        assert "legal_references" in categories
    
    def test_filter_inappropriate_content(self):
        """Test filtering inappropriate content."""
        moderator = ContentModerator()
        
        # Test profanity filtering
        profane_text = "This damn claim was rejected again."
        filtered_text, matches = moderator._filter_inappropriate_content(profane_text)
        assert "damn" not in filtered_text
        assert "[inappropriate term]" in filtered_text
        assert len(matches) > 0
        assert matches[0]["type"] == "profanity"
        
        # Test non-professional language
        unprofessional_text = "Wow, that's cool! The claim was approved, haha!"
        filtered_text, matches = moderator._filter_inappropriate_content(unprofessional_text)
        assert len(matches) > 0
        
        # Test certainty language
        certainty_text = "This will definitely be approved 100% of the time."
        filtered_text, matches = moderator._filter_inappropriate_content(certainty_text)
        assert len(matches) > 0
        assert any(match["type"] == "certainty_language" for match in matches)
    
    def test_add_appropriate_disclaimers(self):
        """Test adding appropriate disclaimers."""
        moderator = ContentModerator()
        
        # Test medical disclaimer
        medical_text = "The diagnosis requires treatment with medication."
        categories = {"medical_information"}
        with_disclaimer = moderator._add_appropriate_disclaimers(medical_text, categories)
        assert "DISCLAIMER:" in with_disclaimer
        assert "not constitute medical advice" in with_disclaimer
        
        # Test billing disclaimer
        billing_text = "Refile the claim with the correct modifier."
        categories = {"billing_advice"}
        with_disclaimer = moderator._add_appropriate_disclaimers(billing_text, categories)
        assert "DISCLAIMER:" in with_disclaimer
        assert "billing guidance" in with_disclaimer
        
        # Test multiple disclaimers
        mixed_text = "The diagnosis requires treatment and you should refile the claim."
        categories = {"medical_information", "billing_advice"}
        with_disclaimer = moderator._add_appropriate_disclaimers(mixed_text, categories)
        assert "DISCLAIMER:" in with_disclaimer
        # Should have two disclaimers
        assert with_disclaimer.count("DISCLAIMER:") > 1
        
        # Test with disclaimers disabled
        moderator.add_disclaimers = False
        no_disclaimer = moderator._add_appropriate_disclaimers(medical_text, categories)
        assert no_disclaimer == medical_text
    
    def test_standardize_formatting(self):
        """Test standardizing response formatting."""
        moderator = ContentModerator()
        
        # Test standardizing section headings
        text_with_nonstandard_heading = "Denial analysis:\n\nThe claim was denied due to..."
        standardized = moderator._standardize_formatting(text_with_nonstandard_heading)
        assert "DENIAL ANALYSIS:" in standardized
        
        # Test standardizing steps
        steps_text = "STEPS TO RESOLVE:\nCheck the code.\nResubmit the claim.\nFollow up."
        standardized = moderator._standardize_formatting(steps_text)
        assert "1. Check the code." in standardized or "1) Check the code." in standardized
    
    def test_moderate_response(self):
        """Test moderating a complete response."""
        # Create a mock PHI detector
        phi_detector = MagicMock(spec=PHIDetector)
        phi_detector.detect_phi.return_value = [
            PHIDetection(
                category="PATIENT_NAME",
                text="John Doe",
                start_pos=10,
                end_pos=18,
                confidence=0.9
            )
        ]
        phi_detector.redact_phi_by_category.return_value = "Patient [NAME] had a claim denied."
        
        # Create the moderator with the mock detector
        moderator = ContentModerator(phi_detector=phi_detector)
        
        # Test complete moderation
        response = "Patient John Doe had a claim denied. Steps to resolve:\nCheck the code.\nFix the error.\nThis will definitely work."
        context = {"medical_advice": True}
        
        result = moderator.moderate_response(response, context)
        
        # Check the result structure
        assert "original_response" in result
        assert "moderated_response" in result
        assert "moderation_details" in result
        
        # Check moderation actions
        details = result["moderation_details"]
        assert details["phi_detected"] is True
        assert "DISCLAIMER:" in result["moderated_response"]
        
        # Text should be reformatted
        assert "STEPS TO RESOLVE:" in result["moderated_response"]


class TestErrorHandler:
    """Tests for the ErrorHandler class."""
    
    def test_initialization(self):
        """Test initialization of error handler."""
        handler = ErrorHandler()
        assert handler.error_log == []
        assert handler.max_log_size > 0
        assert handler.error_counts == {}
        assert len(handler.error_categorizers) > 0
    
    def test_categorize_error(self):
        """Test error categorization."""
        handler = ErrorHandler()
        
        # Test timeout error
        timeout_error = TimeoutError("Operation timed out")
        category, severity = handler._categorize_error(timeout_error)
        assert category == ErrorCategory.TIMEOUT
        assert severity == ErrorSeverity.WARNING
        
        # Test value error (input error)
        value_error = ValueError("Invalid input")
        category, severity = handler._categorize_error(value_error)
        assert category == ErrorCategory.INPUT
        assert severity == ErrorSeverity.WARNING
        
        # Test network error
        connection_error = ConnectionError("Failed to connect")
        category, severity = handler._categorize_error(connection_error)
        assert category == ErrorCategory.NETWORK
        assert severity == ErrorSeverity.WARNING
    
    def test_handle_error(self):
        """Test handling an error."""
        handler = ErrorHandler()
        
        # Handle a test error
        test_error = ValueError("Test error")
        error_details = handler.handle_error(
            error=test_error,
            message="A test error occurred",
            context={"test_key": "test_value"}
        )
        
        # Check error details
        assert error_details.error == test_error
        assert error_details.error_type == "ValueError"
        assert error_details.message == "A test error occurred"
        assert error_details.context["test_key"] == "test_value"
        
        # Error should be tracked
        assert "ValueError" in handler.error_counts
        assert handler.error_counts["ValueError"] == 1
        
        # Error should be logged
        assert len(handler.error_log) == 1
        assert handler.error_log[0].error_type == "ValueError"
    
    def test_get_error_log(self):
        """Test getting the error log."""
        handler = ErrorHandler()
        
        # Add some test errors
        handler.handle_error(ValueError("Error 1"))
        handler.handle_error(TypeError("Error 2"))
        handler.handle_error(ValueError("Error 3"))
        
        # Get all errors
        all_errors = handler.get_error_log()
        assert len(all_errors) == 3
        
        # Get errors by category
        input_errors = handler.get_error_log(category=ErrorCategory.INPUT)
        assert len(input_errors) > 0
        
        # Get errors with limit
        limited_errors = handler.get_error_log(limit=1)
        assert len(limited_errors) == 1
    
    def test_get_error_stats(self):
        """Test getting error statistics."""
        handler = ErrorHandler()
        
        # Add some test errors
        handler.handle_error(ValueError("Error 1"))
        handler.handle_error(TypeError("Error 2"))
        handler.handle_error(ValueError("Error 3"))
        
        # Get stats
        stats = handler.get_error_stats()
        
        # Check stats structure
        assert "total_errors" in stats
        assert "error_counts_by_type" in stats
        assert "error_counts_by_category" in stats
        assert "error_counts_by_severity" in stats
        
        # Check values
        assert stats["total_errors"] == 3
        assert stats["error_counts_by_type"]["ValueError"] == 2
        assert stats["error_counts_by_type"]["TypeError"] == 1


class TestFallbackSystem:
    """Tests for the FallbackSystem class."""
    
    def test_initialization(self):
        """Test initialization of fallback system."""
        # Test with no error handler
        fallback = FallbackSystem()
        assert fallback.error_handler is None
        assert fallback.fallback_handlers == {}
        
        # Test with error handler
        error_handler = MagicMock(spec=ErrorHandler)
        fallback = FallbackSystem(error_handler=error_handler)
        assert fallback.error_handler is error_handler
    
    def test_register_fallback(self):
        """Test registering fallback handlers."""
        fallback = FallbackSystem()
        
        # Create a mock handler
        mock_handler = MagicMock()
        
        # Register the handler
        fallback.register_fallback("test_component", mock_handler)
        
        # Check it was registered
        assert fallback.fallback_handlers["test_component"] == mock_handler
    
    def test_safe_execute_success(self):
        """Test safe execution with successful function."""
        fallback = FallbackSystem()
        
        # Create a test function that succeeds
        def test_func(arg1, arg2=None):
            return {"result": arg1 + (arg2 or 0)}
        
        # Execute safely
        result, error = fallback.safe_execute(test_func, 1, arg2=2)
        
        # Should return result and no error
        assert result == {"result": 3}
        assert error is None
    
    def test_safe_execute_failure(self):
        """Test safe execution with failing function."""
        error_handler = MagicMock(spec=ErrorHandler)
        error_handler.handle_error.return_value = MagicMock()
        
        fallback = FallbackSystem(error_handler=error_handler)
        
        # Create a test function that fails
        def test_func():
            raise ValueError("Test error")
        
        # Execute safely
        result, error = fallback.safe_execute(test_func)
        
        # Should return fallback result and error details
        assert result["success"] is False
        assert result["fallback"] is True
        assert "I apologize" in result["message"]
        assert error is not None
        
        # Error handler should have been called
        error_handler.handle_error.assert_called_once()
    
    def test_safe_execute_with_component_fallback(self):
        """Test safe execution with component-specific fallback."""
        fallback = FallbackSystem()
        
        # Create a test function that fails
        def test_func():
            raise ValueError("Test error")
        
        # Create a component-specific fallback
        def component_fallback(error, args):
            return {"custom_fallback": True, "error_type": type(error).__name__}
        
        # Register the fallback
        fallback.register_fallback("test_component", component_fallback)
        
        # Execute safely with component name
        result, error = fallback.safe_execute(
            test_func, component_name="test_component"
        )
        
        # Should use component-specific fallback
        assert result["custom_fallback"] is True
        assert result["error_type"] == "ValueError"
        assert error is not None
    
    def test_safe_execution_decorator(self):
        """Test the safe execution decorator."""
        # Create a function with the decorator
        @safe_execution_decorator(component_name="test_component")
        def decorated_func(arg1, arg2=None):
            if arg1 < 0:
                raise ValueError("Negative argument")
            return {"result": arg1 + (arg2 or 0)}
        
        # Test with successful execution
        result = decorated_func(1, arg2=2)
        assert result["result"] == 3
        
        # Test with failure
        result = decorated_func(-1)
        assert "success" in result
        assert result["success"] is False
