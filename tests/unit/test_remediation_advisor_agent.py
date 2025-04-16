"""
Remediation Advisor Agent Tests

This module contains tests for the RemediationAdvisorAgent class to verify that
it initializes correctly and can provide remediation steps for denials.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open

from agent.advisors.remediation_advisor import RemediationAdvisorAgent


def test_remediation_advisor_initialization():
    """Test that the remediation advisor agent initializes correctly."""
    # Create mock knowledge bases
    mock_resolution_kb = {
        "resolution_strategies": {
            "missing_information": {
                "name": "Missing Information Resolution Strategy",
                "description": "Steps to resolve denials due to missing information",
                "general_steps": ["Identify missing information", "Resubmit claim"],
                "specific_strategies": ["Review claim for accuracy"],
                "documentation_requirements": ["Completed forms"]
            }
        },
        "billing_rule_references": {
            "coding_references": ["CPT Guidelines"]
        }
    }
    
    mock_compatibility_kb = {
        "allowed_modifiers": ["59", "25"],
        "code_pairs": {
            "modifier_allowed": [
                {
                    "column1_code": "99213", 
                    "column2_code": "99214", 
                    "resolution_guidance": "Use appropriate modifier",
                    "effective_date": "20250101"
                }
            ],
            "modifier_not_allowed": [
                {
                    "column1_code": "80061", 
                    "column2_code": "82465", 
                    "resolution_guidance": "These codes represent bundled services",
                    "effective_date": "20250101"
                }
            ]
        }
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # Verify agent attributes
    assert "missing_information" in agent.resolution_strategies
    assert len(agent.resolution_strategies) == 1
    assert len(agent.allowed_modifiers) == 2
    assert "59" in agent.allowed_modifiers
    assert len(agent.modifier_allowed_pairs) == 1
    assert len(agent.modifier_not_allowed_pairs) == 1
    assert "CPT Guidelines" in agent.billing_rule_references.get("coding_references", [])
    
    # Verify denial type priority is defined
    assert "timely_filing" in agent.denial_type_priority
    assert "medical_necessity" in agent.denial_type_priority
    assert "missing_information" in agent.denial_type_priority


def test_get_remediation_steps_with_known_denial_type():
    """Test getting remediation steps for a known denial type."""
    # Create mock knowledge bases
    mock_resolution_kb = {
        "resolution_strategies": {
            "missing_information": {
                "name": "Missing Information Resolution Strategy",
                "description": "Steps to resolve denials due to missing information",
                "general_steps": ["Identify missing information", "Resubmit claim"],
                "specific_strategies": ["Review claim for accuracy"],
                "documentation_requirements": ["Completed forms"]
            }
        },
        "billing_rule_references": {}
    }
    
    mock_compatibility_kb = {
        "allowed_modifiers": [],
        "code_pairs": {"modifier_allowed": [], "modifier_not_allowed": []}
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # Create test claim details
    claim_details = {
        "patient_name": "John Doe",
        "patient_id": ""  # Missing patient ID
    }
    
    # Get remediation steps
    result = agent.get_remediation_steps("missing_information", claim_details, "16")
    
    # Verify result
    assert result["status"] == "success"
    assert result["denial_type"] == "missing_information"
    assert result["carc_code"] == "16"
    assert "steps" in result
    assert "documentation_requirements" in result
    assert "priority" in result
    
    # Verify steps include both general and specific strategies
    assert "Identify missing information" in result["steps"]
    assert "Resubmit claim" in result["steps"]
    assert "Review claim for accuracy" in result["steps"]
    
    # Verify claim-specific steps are included
    assert any("patient id" in step.lower() for step in result["steps"])
    
    # Verify documentation requirements
    assert "Completed forms" in result["documentation_requirements"]


def test_get_remediation_steps_with_unknown_denial_type():
    """Test getting remediation steps for an unknown denial type."""
    # Create mock knowledge bases
    mock_resolution_kb = {
        "resolution_strategies": {
            "missing_information": {
                "name": "Missing Information Resolution Strategy",
                "general_steps": ["Identify missing information", "Resubmit claim"]
            }
        },
        "billing_rule_references": {}
    }
    
    mock_compatibility_kb = {
        "allowed_modifiers": [],
        "code_pairs": {"modifier_allowed": [], "modifier_not_allowed": []}
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # Get remediation steps for unknown type
    result = agent.get_remediation_steps("unknown_type", {}, "999")
    
    # Verify result
    assert result["status"] == "partial"
    assert result["denial_type"] == "unknown_type"
    assert result["carc_code"] == "999"
    assert "steps" in result
    assert "documentation_requirements" in result
    assert "message" in result
    assert "Generic steps provided" in result["message"]
    
    # Verify generic steps are included
    assert len(result["steps"]) >= 3
    assert any("Review the denial details" in step for step in result["steps"])


def test_find_alternative_strategy():
    """Test finding an alternative strategy when exact match is not found."""
    # Create mock knowledge bases
    mock_resolution_kb = {
        "resolution_strategies": {
            "missing_information": {
                "name": "Missing Information Resolution Strategy",
                "general_steps": ["Step 1", "Step 2"]
            },
            "medical_necessity": {
                "name": "Medical Necessity Resolution Strategy",
                "general_steps": ["Get documentation", "Appeal"]
            }
        },
        "billing_rule_references": {}
    }
    
    mock_compatibility_kb = {
        "allowed_modifiers": [],
        "code_pairs": {"modifier_allowed": [], "modifier_not_allowed": []}
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # Test finding alternative for patient_information
    patient_info_strategy = agent._find_alternative_strategy("patient_information")
    assert patient_info_strategy is not None
    assert patient_info_strategy == mock_resolution_kb["resolution_strategies"]["missing_information"]
    
    # Test finding alternative for authorization_required
    auth_strategy = agent._find_alternative_strategy("authorization_required")
    assert auth_strategy is not None
    assert auth_strategy == mock_resolution_kb["resolution_strategies"]["medical_necessity"]
    
    # Test with no alternative available
    no_alt_strategy = agent._find_alternative_strategy("totally_unknown")
    assert no_alt_strategy is None


def test_generate_specific_steps_for_missing_information():
    """Test generating specific steps for missing information denial."""
    # Create mock knowledge bases
    mock_resolution_kb = {
        "resolution_strategies": {
            "missing_information": {
                "name": "Missing Information Resolution Strategy",
                "specific_strategies": ["Check patient demographics"]
            }
        },
        "billing_rule_references": {}
    }
    
    mock_compatibility_kb = {
        "allowed_modifiers": [],
        "code_pairs": {"modifier_allowed": [], "modifier_not_allowed": []}
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # Create claim details with missing fields
    claim_details = {
        "patient_name": "John Doe",
        "patient_dob": "",  # Missing DOB
        "patient_id": ""    # Missing ID
    }
    
    # Generate specific steps
    steps = agent._generate_specific_steps(
        "missing_information", 
        "16", 
        None, 
        claim_details, 
        mock_resolution_kb["resolution_strategies"]["missing_information"]
    )
    
    # Verify general strategy is included
    assert "Check patient demographics" in steps
    
    # Verify specific missing fields are addressed
    assert any("patient dob" in step.lower() for step in steps)
    assert any("patient id" in step.lower() for step in steps)


def test_generate_specific_steps_for_bundling():
    """Test generating specific steps for bundling denial."""
    # Create mock knowledge bases
    mock_resolution_kb = {
        "resolution_strategies": {
            "bundling": {
                "name": "Bundling Resolution Strategy",
                "specific_strategies": ["Check for modifiers"]
            }
        },
        "billing_rule_references": {}
    }
    
    mock_compatibility_kb = {
        "allowed_modifiers": ["59"],
        "code_pairs": {
            "modifier_allowed": [],
            "modifier_not_allowed": [
                {
                    "column1_code": "80061", 
                    "column2_code": "82465", 
                    "resolution_guidance": "These codes represent bundled services",
                    "effective_date": "20250101"
                }
            ]
        }
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # Create claim details with bundled codes
    claim_details = {
        "procedure_codes": ["80061", "82465"]
    }
    
    # Make check_code_compatibility return incompatible
    with patch.object(agent, 'check_code_compatibility') as mock_check:
        mock_check.return_value = {
            "status": "incompatible",
            "resolution": "These codes represent bundled services"
        }
        
        # Generate specific steps
        steps = agent._generate_specific_steps(
            "bundling", 
            "97", 
            None, 
            claim_details, 
            mock_resolution_kb["resolution_strategies"]["bundling"]
        )
    
    # Verify general strategy is included
    assert "Check for modifiers" in steps
    
    # Verify bundling-specific advice
    assert any("Review all procedure codes" in step for step in steps)
    assert any("Address incompatible codes" in step for step in steps)


def test_check_code_compatibility():
    """Test checking code compatibility."""
    # Create mock knowledge bases
    mock_resolution_kb = {"resolution_strategies": {}, "billing_rule_references": {}}
    
    mock_compatibility_kb = {
        "allowed_modifiers": ["59", "25"],
        "code_pairs": {
            "modifier_allowed": [
                {
                    "column1_code": "99213", 
                    "column2_code": "99214", 
                    "resolution_guidance": "Use appropriate modifier",
                    "effective_date": "20250101"
                }
            ],
            "modifier_not_allowed": [
                {
                    "column1_code": "80061", 
                    "column2_code": "82465", 
                    "resolution_guidance": "These codes represent bundled services",
                    "effective_date": "20250101"
                }
            ]
        }
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # Test compatible with modifier
    compatible_result = agent.check_code_compatibility("99213", "99214")
    assert compatible_result["status"] == "compatible_with_modifier"
    assert "99213" in [compatible_result["primary_code"], compatible_result["secondary_code"]]
    assert "99214" in [compatible_result["primary_code"], compatible_result["secondary_code"]]
    assert compatible_result["allowed_modifiers"] == ["59", "25"]
    assert "Use appropriate modifier" in compatible_result["resolution"]
    
    # Test incompatible
    incompatible_result = agent.check_code_compatibility("80061", "82465")
    assert incompatible_result["status"] == "incompatible"
    assert "80061" in [incompatible_result["primary_code"], incompatible_result["secondary_code"]]
    assert "82465" in [incompatible_result["primary_code"], incompatible_result["secondary_code"]]
    assert "bundled services" in incompatible_result["resolution"]
    
    # Test likely compatible (not found in either list)
    likely_result = agent.check_code_compatibility("99215", "81000")
    assert likely_result["status"] == "likely_compatible"
    assert "no specific compatibility rule found" in likely_result["message"].lower()


def test_get_resolution_strategy_by_type():
    """Test getting a resolution strategy by type."""
    # Create mock knowledge bases
    mock_resolution_kb = {
        "resolution_strategies": {
            "missing_information": {
                "name": "Missing Information Resolution Strategy",
                "description": "Steps to resolve denials due to missing information",
                "general_steps": ["Step 1", "Step 2"],
                "specific_strategies": ["Strategy A", "Strategy B"],
                "documentation_requirements": ["Doc 1", "Doc 2"]
            }
        },
        "billing_rule_references": {}
    }
    
    mock_compatibility_kb = {
        "allowed_modifiers": [],
        "code_pairs": {"modifier_allowed": [], "modifier_not_allowed": []}
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # Get strategy for existing type
    existing_strategy = agent.get_resolution_strategy_by_type("missing_information")
    assert existing_strategy["status"] == "success"
    assert existing_strategy["denial_type"] == "missing_information"
    assert existing_strategy["name"] == "Missing Information Resolution Strategy"
    assert existing_strategy["general_steps"] == ["Step 1", "Step 2"]
    assert existing_strategy["specific_strategies"] == ["Strategy A", "Strategy B"]
    assert existing_strategy["documentation_requirements"] == ["Doc 1", "Doc 2"]
    
    # Get strategy for non-existent type
    nonexistent_strategy = agent.get_resolution_strategy_by_type("nonexistent_type")
    assert nonexistent_strategy["status"] == "not_found"
    assert "no resolution strategy found" in nonexistent_strategy["message"].lower()


def test_list_incompatible_codes():
    """Test listing incompatible codes."""
    # Create mock knowledge bases
    mock_resolution_kb = {"resolution_strategies": {}, "billing_rule_references": {}}
    
    mock_compatibility_kb = {
        "allowed_modifiers": ["59"],
        "code_pairs": {
            "modifier_allowed": [
                {
                    "column1_code": "99213", 
                    "column2_code": "90471", 
                    "resolution_guidance": "Use modifier 25",
                    "effective_date": "20250101"
                }
            ],
            "modifier_not_allowed": [
                {
                    "column1_code": "80061", 
                    "column2_code": "82465", 
                    "resolution_guidance": "These codes represent bundled services",
                    "effective_date": "20250101"
                },
                {
                    "column1_code": "80061", 
                    "column2_code": "83721", 
                    "resolution_guidance": "Cannot bill together",
                    "effective_date": "20250101"
                }
            ]
        }
    }
    
    # Patch the knowledge base loading
    with patch('agent.advisors.remediation_advisor.open', mock_open()):
        with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=mock_resolution_kb):
            with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=mock_compatibility_kb):
                agent = RemediationAdvisorAgent()
    
    # List incompatible codes for 80061
    result = agent.list_incompatible_codes("80061")
    
    # Verify result
    assert result["status"] == "success"
    assert result["code"] == "80061"
    assert "incompatible_codes" in result
    assert "compatible_with_modifier_codes" in result
    assert result["incompatible_count"] == 2
    assert result["compatible_with_modifier_count"] == 0
    
    # Verify incompatible codes
    incompatible_codes = [item["code"] for item in result["incompatible_codes"]]
    assert "82465" in incompatible_codes
    assert "83721" in incompatible_codes
    
    # List incompatible codes for 99213
    result = agent.list_incompatible_codes("99213")
    
    # Verify result for compatible with modifier
    assert result["status"] == "success"
    assert result["code"] == "99213"
    assert result["incompatible_count"] == 0
    assert result["compatible_with_modifier_count"] == 1
    
    # Verify compatible with modifier codes
    compatible_codes = [item["code"] for item in result["compatible_with_modifier_codes"]]
    assert "90471" in compatible_codes
