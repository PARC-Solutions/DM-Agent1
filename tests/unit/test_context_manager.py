"""
Tests for the context management system.

This module contains tests for the context management system that handles context
enrichment, truncation, and sharing between agents in the Medical Billing Denial Agent.
"""

import pytest
from unittest.mock import MagicMock, patch
import json

from agent.core.context_manager import ContextManager


class TestContextManager:
    """Tests for the ContextManager class."""
    
    def test_initialization(self):
        """Test initialization of context manager."""
        # Test with default max_context_size
        context_manager = ContextManager()
        assert context_manager.max_context_size == 2048
        assert context_manager.token_approx_ratio == 4
        
        # Test with custom max_context_size
        context_manager = ContextManager(max_context_size=4096)
        assert context_manager.max_context_size == 4096
    
    def test_estimate_token_count(self):
        """Test the token count estimation."""
        context_manager = ContextManager()
        
        # Test with empty string
        assert context_manager._estimate_token_count("") == 0
        
        # Test with short text
        short_text = "This is a short test."
        expected_tokens = len(short_text) // context_manager.token_approx_ratio
        assert context_manager._estimate_token_count(short_text) == expected_tokens
        
        # Test with longer text
        long_text = "This is a longer test that should result in more tokens. " * 10
        expected_tokens = len(long_text) // context_manager.token_approx_ratio
        assert context_manager._estimate_token_count(long_text) == expected_tokens
    
    def test_truncate_context_no_truncation_needed(self):
        """Test context truncation when no truncation is needed."""
        context_manager = ContextManager(max_context_size=1000)
        
        # Create a small context that doesn't need truncation
        context = {
            "key1": "value1",
            "key2": "value2",
            "key3": 123
        }
        
        # Estimate token count
        context_str = json.dumps(context)
        estimated_tokens = context_manager._estimate_token_count(context_str)
        
        # Verify it's under the limit
        assert estimated_tokens <= context_manager.max_context_size
        
        # Truncate and verify it's unchanged
        truncated = context_manager._truncate_context(context)
        assert truncated == context
    
    def test_truncate_context_conversation_history(self):
        """Test truncation of conversation history."""
        context_manager = ContextManager(max_context_size=100)  # Small limit for testing
        
        # Create a context with large conversation history
        context = {
            "conversation_history": [
                {"user_input": "Hello " * 20, "agent_response": "Hi " * 20},
                {"user_input": "How are you?", "agent_response": "I'm fine, thanks!"},
                {"user_input": "What's new?", "agent_response": "Not much."}
            ],
            "session_id": "test123",
            "metadata": {"key": "value"}
        }
        
        # Truncate
        truncated = context_manager._truncate_context(context)
        
        # Should have truncated conversation history
        assert len(truncated["conversation_history"]) < len(context["conversation_history"])
        
        # Should preserve other fields
        assert truncated["session_id"] == context["session_id"]
        assert truncated["metadata"] == context["metadata"]
    
    def test_truncate_context_document_content(self):
        """Test truncation of document content."""
        context_manager = ContextManager(max_context_size=100)  # Small limit for testing
        
        # Create a context with large document content
        context = {
            "document_content": "This is a very long document content. " * 50,
            "session_id": "test123",
            "metadata": {"key": "value"}
        }
        
        # Truncate
        truncated = context_manager._truncate_context(context)
        
        # Should have truncated document content
        assert len(truncated["document_content"]) < len(context["document_content"])
        assert "...truncated..." in truncated["document_content"]
        
        # Should preserve other fields
        assert truncated["session_id"] == context["session_id"]
        assert truncated["metadata"] == context["metadata"]
    
    def test_truncate_context_document_list(self):
        """Test truncation of document list."""
        context_manager = ContextManager(max_context_size=100)  # Small limit for testing
        
        # Create a context with a list of documents
        context = {
            "documents": [
                {"content": "Document 1 " * 20, "metadata": {"type": "type1"}},
                {"content": "Document 2 " * 20, "metadata": {"type": "type2"}},
                {"content": "Document 3 " * 20, "metadata": {"type": "type3"}}
            ],
            "session_id": "test123"
        }
        
        # Truncate
        truncated = context_manager._truncate_context(context)
        
        # Should have truncated document list
        assert len(truncated["documents"]) < len(context["documents"])
        
        # Should preserve other fields
        assert truncated["session_id"] == context["session_id"]
    
    def test_truncate_context_lower_priority_fields(self):
        """Test truncation with lower priority fields."""
        context_manager = ContextManager(max_context_size=100)  # Small limit for testing
        
        # Create a context with lower priority fields
        context = {
            "session_id": "test123",
            "essential_info": "This must be kept",
            "extracted_entities": ["entity1", "entity2", "entity3"] * 10,
            "debug_info": {"key": "value"} * 10,
            "reference_materials": ["ref1", "ref2"] * 10
        }
        
        # Truncate
        truncated = context_manager._truncate_context(context)
        
        # Should preserve essential fields
        assert truncated["session_id"] == context["session_id"]
        assert truncated["essential_info"] == context["essential_info"]
        
        # Should remove lower priority fields
        lower_priority_removed = any(
            field not in truncated for field in [
                "extracted_entities", "debug_info", "reference_materials"
            ]
        )
        assert lower_priority_removed
    
    def test_enrich_context_basic(self):
        """Test basic context enrichment."""
        context_manager = ContextManager()
        
        # Base context
        base_context = {
            "session_id": "test123",
            "user_id": "user456",
            "counter": 5
        }
        
        # Supplementary info
        supplementary_info = {
            "new_field": "new_value",
            "counter": 10  # This should overwrite existing value
        }
        
        # Enrich context
        enriched = context_manager.enrich_context(base_context, supplementary_info)
        
        # Check results
        assert enriched["session_id"] == "test123"
        assert enriched["user_id"] == "user456"
        assert enriched["new_field"] == "new_value"
        assert enriched["counter"] == 10  # Should be updated
    
    def test_enrich_context_list_fields(self):
        """Test enrichment of list fields."""
        context_manager = ContextManager()
        
        # Base context
        base_context = {
            "session_id": "test123",
            "items": ["item1", "item2"],
            "counters": [1, 2, 3]
        }
        
        # Supplementary info
        supplementary_info = {
            "items": ["item3", "item4"],  # These should be appended
            "new_list": ["new1", "new2"]
        }
        
        # Enrich context
        enriched = context_manager.enrich_context(base_context, supplementary_info)
        
        # Check results
        assert enriched["session_id"] == "test123"
        assert enriched["items"] == ["item1", "item2", "item3", "item4"]
        assert enriched["counters"] == [1, 2, 3]
        assert enriched["new_list"] == ["new1", "new2"]
    
    def test_enrich_context_dict_fields(self):
        """Test enrichment of dictionary fields."""
        context_manager = ContextManager()
        
        # Base context
        base_context = {
            "session_id": "test123",
            "metadata": {
                "key1": "value1",
                "key2": "value2"
            }
        }
        
        # Supplementary info
        supplementary_info = {
            "metadata": {
                "key2": "updated_value2",  # This should update existing key
                "key3": "value3"  # This should be added
            }
        }
        
        # Enrich context
        enriched = context_manager.enrich_context(base_context, supplementary_info)
        
        # Check results
        assert enriched["session_id"] == "test123"
        assert enriched["metadata"]["key1"] == "value1"
        assert enriched["metadata"]["key2"] == "updated_value2"
        assert enriched["metadata"]["key3"] == "value3"
    
    def test_enrich_context_with_priority_fields(self):
        """Test context enrichment with priority fields."""
        context_manager = ContextManager(max_context_size=100)  # Small limit for testing
        
        # Base context with a lot of content
        base_context = {
            "session_id": "test123",
            "critical_info": "This must be preserved",
            "large_field": "X" * 200,  # This should cause truncation
            "another_field": "Y" * 200
        }
        
        # Supplementary info
        supplementary_info = {
            "new_field": "new_value"
        }
        
        # Priority fields
        priority_fields = ["session_id", "critical_info"]
        
        # Enrich context with priority fields
        enriched = context_manager.enrich_context(
            base_context, supplementary_info, priority_fields
        )
        
        # Priority fields should be preserved
        assert enriched["session_id"] == "test123"
        assert enriched["critical_info"] == "This must be preserved"
        
        # Should have truncated content
        assert len(json.dumps(enriched)) < len(json.dumps(base_context))
    
    def test_extract_agent_specific_context(self):
        """Test extraction of agent-specific context."""
        context_manager = ContextManager()
        
        # Create a comprehensive context
        context = {
            "session_id": "test123",
            "user_id": "user456",
            "conversation_history": [
                {"user_input": "Hello", "agent_response": "Hi"}
            ],
            "carc_code": "A123",
            "rarc_code": "B456",
            "denial_codes": ["code1", "code2"],
            "document_content": "Document text here",
            "patient_information": {"name": "John Doe"},
            "provider_information": {"name": "Dr. Smith"},
            "diagnosis_codes": ["D1", "D2"],
            "denial_type": "billing_error",
            "metadata": {"key": "value"}
        }
        
        # Extract context for denial classifier
        classifier_context = context_manager.extract_agent_specific_context(
            context, "denial_classifier"
        )
        
        # Should include relevant fields for classifier
        assert "carc_code" in classifier_context
        assert "rarc_code" in classifier_context
        assert "denial_codes" in classifier_context
        assert "session_id" in classifier_context  # Default field
        
        # Should exclude irrelevant fields
        assert "document_content" not in classifier_context
        
        # Extract context for claims analyzer
        analyzer_context = context_manager.extract_agent_specific_context(
            context, "claims_analyzer"
        )
        
        # Should include relevant fields for analyzer
        assert "document_content" in analyzer_context
        assert "patient_information" in analyzer_context
        assert "diagnosis_codes" in analyzer_context
        assert "session_id" in analyzer_context  # Default field
        
        # Should exclude irrelevant fields
        assert "denial_type" not in analyzer_context
        
        # Extract context for remediation advisor
        advisor_context = context_manager.extract_agent_specific_context(
            context, "remediation_advisor"
        )
        
        # Should include relevant fields for advisor
        assert "denial_type" in advisor_context
        assert "carc_code" in advisor_context
        assert "provider_information" in advisor_context
        assert "session_id" in advisor_context  # Default field
        
        # Check agent name and timestamp added
        assert advisor_context["agent_name"] == "remediation_advisor"
        assert "context_timestamp" in advisor_context
    
    def test_extract_agent_specific_context_with_required_fields(self):
        """Test extraction of agent-specific context with required fields."""
        context_manager = ContextManager()
        
        # Create a context
        context = {
            "session_id": "test123",
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        
        # Required fields
        required_fields = ["field1", "field3", "non_existent_field"]
        
        # Extract context with required fields
        agent_context = context_manager.extract_agent_specific_context(
            context, "test_agent", required_fields
        )
        
        # Should include required fields that exist
        assert "field1" in agent_context
        assert "field3" in agent_context
        
        # Should include default fields
        assert "session_id" in agent_context
        
        # Should exclude non-required fields
        assert "field2" not in agent_context
        
        # Non-existent required fields should be excluded
        assert "non_existent_field" not in agent_context
    
    def test_merge_agent_results(self):
        """Test merging results from multiple agents."""
        context_manager = ContextManager()
        
        # Base context
        base_context = {
            "session_id": "test123",
            "user_id": "user456",
            "conversation_history": [
                {"user_input": "Hello", "agent_response": "Hi"}
            ],
            "metadata": {"key": "value"},
            "documents": ["doc1", "doc2"]
        }
        
        # Agent results
        agent_results = [
            {
                "agent_name": "agent1",
                "context_timestamp": 123456789,
                "field1": "value1",
                "shared_field": "value_from_agent1",
                "list_field": ["A", "B"]
            },
            {
                "agent_name": "agent2",
                "context_timestamp": 123456790,
                "field2": "value2",
                "shared_field": "value_from_agent2",  # Conflict
                "list_field": ["C", "D"]  # Will be merged
            }
        ]
        
        # Merge agent results
        merged = context_manager.merge_agent_results(base_context, agent_results)
        
        # Should preserve preserve_fields from base context
        assert merged["session_id"] == "test123"
        assert merged["user_id"] == "user456"
        assert merged["conversation_history"] == base_context["conversation_history"]
        assert merged["metadata"] == base_context["metadata"]
        assert merged["documents"] == base_context["documents"]
        
        # Should include fields from both agents
        assert merged["field1"] == "value1"
        assert merged["field2"] == "value2"
        
        # Latest value should win for shared field
        assert merged["shared_field"] == "value_from_agent2"
        
        # List fields should be combined
        assert merged["list_field"] == ["A", "B", "C", "D"]
        
        # Agent identifiers should be excluded
        assert "agent_name" not in merged
        assert "context_timestamp" not in merged
    
    def test_merge_agent_results_with_custom_preserve_fields(self):
        """Test merging results with custom preserved fields."""
        context_manager = ContextManager()
        
        # Base context
        base_context = {
            "session_id": "test123",
            "user_id": "user456",
            "critical_field": "critical_value",
            "normal_field": "normal_value"
        }
        
        # Agent results
        agent_results = [
            {
                "agent_name": "agent1",
                "normal_field": "updated_normal_value",
                "critical_field": "updated_critical_value"  # Should not overwrite
            }
        ]
        
        # Custom preserve fields
        preserve_fields = {"session_id", "critical_field"}
        
        # Merge agent results with custom preserve fields
        merged = context_manager.merge_agent_results(
            base_context, agent_results, preserve_fields
        )
        
        # Preserved fields should be kept from base context
        assert merged["session_id"] == "test123"
        assert merged["critical_field"] == "critical_value"
        
        # Non-preserved fields should be updated
        assert merged["normal_field"] == "updated_normal_value"
        
        # Other base fields should be maintained
        assert merged["user_id"] == "user456"
