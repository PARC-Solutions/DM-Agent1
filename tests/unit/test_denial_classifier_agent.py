"""
Denial Classifier Agent Tests

This module contains tests for the DenialClassifierAgent class to verify that
it initializes correctly and accurately classifies denial codes.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open

from agent.classifiers.denial_classifier import DenialClassifierAgent


def test_denial_classifier_initialization():
    """Test that the denial classifier agent initializes correctly."""
    # Create mock knowledge base
    mock_knowledge_base = {
        "carc_codes": [{"code": "16", "denial_type": "missing_information"}],
        "rarc_codes": [{"code": "N01", "description": "Alert: Documentation needed"}],
        "group_codes": [{"code": "CO", "description": "Contractual Obligation"}]
    }
    
    # Patch the knowledge base loading
    with patch('agent.classifiers.denial_classifier.open', mock_open()):
        with patch('json.load', return_value=mock_knowledge_base):
            agent = DenialClassifierAgent()
    
    # Verify agent attributes
    assert len(agent.carc_lookup) == 1
    assert "16" in agent.carc_lookup
    assert len(agent.rarc_lookup) == 1
    assert "N01" in agent.rarc_lookup
    assert len(agent.group_code_lookup) == 1
    assert "CO" in agent.group_code_lookup
    
    # Verify severity levels are defined
    assert "medical_necessity" in agent.severity_levels
    assert "bundling" in agent.severity_levels
    assert "missing_information" in agent.severity_levels


def test_classify_denial_with_known_codes():
    """Test classification of denial with known CARC and RARC codes."""
    # Create mock knowledge base
    mock_knowledge_base = {
        "carc_codes": [
            {
                "code": "16",
                "denial_type": "missing_information",
                "description": "Claim lacks information",
                "resolution_steps": ["Verify patient info", "Resubmit claim"]
            }
        ],
        "rarc_codes": [
            {
                "code": "N01",
                "description": "Alert: Documentation needed"
            }
        ],
        "group_codes": [
            {
                "code": "CO",
                "description": "Contractual Obligation"
            }
        ]
    }
    
    # Patch the knowledge base loading
    with patch('agent.classifiers.denial_classifier.open', mock_open()):
        with patch('json.load', return_value=mock_knowledge_base):
            agent = DenialClassifierAgent()
    
    # Classify a denial with known codes
    result = agent.classify_denial(carc_code="16", rarc_code="N01", group_code="CO")
    
    # Verify the result
    assert result["status"] == "success"
    assert result["carc_code"] == "16"
    assert result["denial_type"] == "missing_information"
    assert "severity" in result
    assert "explanation" in result
    assert "missing information" in result["explanation"].lower()
    assert result["rarc_code"] == "N01"
    assert result["group_code"] == "CO"
    assert len(result["resolution_steps"]) > 0


def test_classify_denial_with_unknown_carc():
    """Test classification of denial with unknown CARC code."""
    # Create mock knowledge base
    mock_knowledge_base = {
        "carc_codes": [{"code": "16", "denial_type": "missing_information"}],
        "rarc_codes": [{"code": "N01", "description": "Alert: Documentation needed"}],
        "group_codes": [{"code": "CO", "description": "Contractual Obligation"}]
    }
    
    # Patch the knowledge base loading
    with patch('agent.classifiers.denial_classifier.open', mock_open()):
        with patch('json.load', return_value=mock_knowledge_base):
            agent = DenialClassifierAgent()
    
    # Classify a denial with unknown CARC code
    result = agent.classify_denial(carc_code="999")
    
    # Verify the result
    assert result["status"] == "unknown_code"
    assert result["carc_code"] == "999"
    assert result["denial_type"] == "unknown"
    assert "explanation" in result
    assert "not in our knowledge base" in result["explanation"]
    assert len(result["resolution_steps"]) > 0


def test_build_explanation():
    """Test building an explanation from code information."""
    # Create mock knowledge base
    mock_knowledge_base = {
        "carc_codes": [{"code": "16", "denial_type": "missing_information"}],
        "rarc_codes": [{"code": "N01", "description": "Alert: Documentation needed"}],
        "group_codes": [{"code": "CO", "description": "Contractual Obligation"}]
    }
    
    # Patch the knowledge base loading
    with patch('agent.classifiers.denial_classifier.open', mock_open()):
        with patch('json.load', return_value=mock_knowledge_base):
            agent = DenialClassifierAgent()
    
    # Create code info objects
    carc_info = {
        "code": "16",
        "denial_type": "missing_information",
        "description": "Claim lacks information",
        "resolution_steps": ["Verify patient info", "Resubmit claim"]
    }
    rarc_info = {
        "code": "N01",
        "description": "Alert: Documentation needed"
    }
    group_info = {
        "code": "CO",
        "description": "Contractual Obligation"
    }
    
    # Build an explanation
    explanation = agent._build_explanation(carc_info, rarc_info, group_info)
    
    # Verify the explanation
    assert "denied" in explanation.lower()
    assert "claim lacks information" in explanation.lower()
    assert "documentation needed" in explanation.lower()
    assert "contractual obligation" in explanation.lower()
    assert "verify patient info" in explanation.lower()


def test_get_code_information():
    """Test getting detailed information about a specific code."""
    # Create mock knowledge base
    mock_knowledge_base = {
        "carc_codes": [
            {
                "code": "16",
                "denial_type": "missing_information",
                "description": "Claim lacks information",
                "resolution_steps": ["Verify patient info", "Resubmit claim"]
            }
        ],
        "rarc_codes": [
            {
                "code": "N01",
                "description": "Alert: Documentation needed"
            }
        ],
        "group_codes": [{"code": "CO", "description": "Contractual Obligation"}]
    }
    
    # Patch the knowledge base loading
    with patch('agent.classifiers.denial_classifier.open', mock_open()):
        with patch('json.load', return_value=mock_knowledge_base):
            agent = DenialClassifierAgent()
    
    # Get information about a CARC code
    carc_result = agent.get_code_information("CARC", "16")
    
    # Verify the CARC result
    assert carc_result["status"] == "success"
    assert carc_result["code_type"] == "CARC"
    assert carc_result["code"] == "16"
    assert carc_result["description"] == "Claim lacks information"
    assert carc_result["denial_type"] == "missing_information"
    assert len(carc_result["resolution_steps"]) > 0
    
    # Get information about a RARC code
    rarc_result = agent.get_code_information("RARC", "N01")
    
    # Verify the RARC result
    assert rarc_result["status"] == "success"
    assert rarc_result["code_type"] == "RARC"
    assert rarc_result["code"] == "N01"
    assert rarc_result["description"] == "Alert: Documentation needed"
    
    # Get information about an unknown code
    unknown_result = agent.get_code_information("CARC", "999")
    
    # Verify the unknown result
    assert unknown_result["status"] == "unknown_code"
    assert unknown_result["carc_code"] == "999"
    
    # Get information with invalid code type
    invalid_result = agent.get_code_information("INVALID", "16")
    
    # Verify the invalid result
    assert invalid_result["status"] == "error"
    assert "invalid code type" in invalid_result["message"].lower()


def test_list_codes_by_denial_type():
    """Test listing codes by denial type."""
    # Create mock knowledge base
    mock_knowledge_base = {
        "carc_codes": [
            {
                "code": "16",
                "denial_type": "missing_information",
                "description": "Claim lacks information"
            },
            {
                "code": "29",
                "denial_type": "timely_filing",
                "description": "Time limit expired"
            },
            {
                "code": "50",
                "denial_type": "medical_necessity",
                "description": "Non-covered service"
            }
        ],
        "rarc_codes": [{"code": "N01", "description": "Alert: Documentation needed"}],
        "group_codes": [{"code": "CO", "description": "Contractual Obligation"}]
    }
    
    # Patch the knowledge base loading
    with patch('agent.classifiers.denial_classifier.open', mock_open()):
        with patch('json.load', return_value=mock_knowledge_base):
            agent = DenialClassifierAgent()
    
    # List codes for a specific denial type
    result = agent.list_codes_by_denial_type("medical_necessity")
    
    # Verify the result
    assert result["status"] == "success"
    assert result["denial_type"] == "medical_necessity"
    assert "severity" in result
    assert len(result["matching_codes"]) == 1
    assert result["matching_codes"][0]["code"] == "50"
    assert result["count"] == 1
    
    # List codes for a type with multiple codes
    result = agent.list_codes_by_denial_type("missing_information")
    
    # Verify result with multiple codes
    assert result["status"] == "success"
    assert len(result["matching_codes"]) == 1
    assert result["count"] == 1
    
    # List codes for unknown type
    result = agent.list_codes_by_denial_type("unknown_type")
    
    # Verify result with no matches
    assert result["status"] == "no_results"
    assert "no carc codes found" in result["message"].lower()
