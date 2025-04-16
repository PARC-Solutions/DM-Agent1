"""
Specialized Agents Integration Tests

This module contains integration tests for all specialized agents to verify that
they can work together correctly with the coordinator agent.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open

from agent.core.coordinator import DenialAssistantAgent
from agent.core.session_manager import SessionManager
from agent.classifiers.denial_classifier import DenialClassifierAgent
from agent.analyzers.claims_analyzer import ClaimsAnalyzerAgent
from agent.advisors.remediation_advisor import RemediationAdvisorAgent


@pytest.fixture
def mock_knowledge_bases():
    """Fixture that provides mock knowledge bases for testing."""
    # Mock CARC/RARC knowledge base
    carc_rarc_kb = {
        "carc_codes": [
            {
                "code": "16",
                "denial_type": "missing_information",
                "description": "Claim lacks information",
                "resolution_steps": ["Verify patient info", "Resubmit claim"]
            },
            {
                "code": "97",
                "denial_type": "bundling",
                "description": "Payment adjusted",
                "resolution_steps": ["Review coding", "Appeal"]
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
    
    # Mock resolution knowledge base
    resolution_kb = {
        "resolution_strategies": {
            "missing_information": {
                "name": "Missing Information Resolution Strategy",
                "description": "Steps to resolve denials due to missing information",
                "general_steps": ["Identify missing information", "Resubmit claim"],
                "specific_strategies": ["Review claim for accuracy"],
                "documentation_requirements": ["Completed forms"]
            },
            "bundling": {
                "name": "Bundling Resolution Strategy",
                "description": "Steps to resolve denials due to bundling issues",
                "general_steps": ["Review coding guidelines", "Verify services", "Appeal or correct"],
                "specific_strategies": ["Use appropriate modifiers", "Separate services if applicable"],
                "documentation_requirements": ["Coding guidelines reference", "Service documentation"]
            }
        },
        "billing_rule_references": {
            "coding_references": ["CPT Guidelines"]
        }
    }
    
    # Mock compatibility knowledge base
    compatibility_kb = {
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
    
    return {
        "carc_rarc": carc_rarc_kb,
        "resolution": resolution_kb,
        "compatibility": compatibility_kb
    }


def test_coordinator_with_specialized_agents(mock_knowledge_bases):
    """Test that the coordinator agent can use specialized agents correctly."""
    # Set up mock knowledge bases
    carc_rarc_kb = mock_knowledge_bases["carc_rarc"]
    resolution_kb = mock_knowledge_bases["resolution"]
    compatibility_kb = mock_knowledge_bases["compatibility"]
    
    # Create patchers
    with patch('agent.classifiers.denial_classifier.open', mock_open()):
        with patch('agent.advisors.remediation_advisor.open', mock_open()):
            with patch.object(DenialClassifierAgent, '_load_knowledge_base', return_value=carc_rarc_kb):
                with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=resolution_kb):
                    with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=compatibility_kb):
                        # Create session manager
                        session_manager = SessionManager()
                        
                        # Create coordinator agent
                        coordinator = DenialAssistantAgent(session_manager)
                        
                        # Initialize the specialized agents
                        coordinator._initialize_sub_agents()
                        
                        # Verify specialized agents are initialized
                        assert coordinator.denial_classifier is not None
                        assert coordinator.claims_analyzer is not None
                        assert coordinator.remediation_advisor is not None
                        
                        # Test denial classification task
                        context = {"carc_code": "16", "rarc_code": "N01"}
                        response = coordinator._route_to_specialized_agent(
                            coordinator.TaskType.DENIAL_CLASSIFICATION,
                            "What does CARC code 16 mean?",
                            context
                        )
                        
                        # Verify response for denial classification
                        assert "missing_information" in response.lower()
                        assert "DENIAL ANALYSIS" in response
                        
                        # Test remediation advice task
                        context = {"denial_type": "missing_information", "carc_code": "16"}
                        response = coordinator._route_to_specialized_agent(
                            coordinator.TaskType.REMEDIATION_ADVICE,
                            "How do I fix this issue?",
                            context
                        )
                        
                        # Verify response for remediation advice
                        assert "STEPS TO RESOLVE" in response
                        assert "Identify missing information" in response


def test_workflow_integration(mock_knowledge_bases):
    """Test that all specialized agents can work together in a workflow."""
    # Set up mock knowledge bases
    carc_rarc_kb = mock_knowledge_bases["carc_rarc"]
    resolution_kb = mock_knowledge_bases["resolution"]
    compatibility_kb = mock_knowledge_bases["compatibility"]
    
    # Create patchers
    with patch('agent.classifiers.denial_classifier.open', mock_open()):
        with patch('agent.advisors.remediation_advisor.open', mock_open()):
            with patch.object(DenialClassifierAgent, '_load_knowledge_base', return_value=carc_rarc_kb):
                with patch.object(RemediationAdvisorAgent, '_load_resolution_knowledge_base', return_value=resolution_kb):
                    with patch.object(RemediationAdvisorAgent, '_load_compatibility_knowledge_base', return_value=compatibility_kb):
                        # Create the specialized agents
                        classifier = DenialClassifierAgent()
                        analyzer = ClaimsAnalyzerAgent()
                        advisor = RemediationAdvisorAgent()
                        
                        # Simulate workflow:
                        # 1. Classify a denial
                        classification = classifier.classify_denial("97")
                        assert classification["status"] == "success"
                        assert classification["denial_type"] == "bundling"
                        
                        # 2. Analyze claim details (simulate with a simple claim)
                        claim_details = {
                            "procedure_codes": ["80061", "82465"]
                        }
                        
                        issues = analyzer.identify_claim_issues(claim_details)
                        assert issues["status"] == "success"
                        
                        # 3. Get remediation steps based on classification and claim details
                        remediation = advisor.get_remediation_steps(
                            denial_type=classification["denial_type"],
                            claim_details=claim_details,
                            carc_code="97"
                        )
                        
                        assert remediation["status"] == "success"
                        assert remediation["denial_type"] == "bundling"
                        assert len(remediation["steps"]) > 0
                        
                        # 4. Check code compatibility
                        compatibility = advisor.check_code_compatibility("80061", "82465")
                        assert compatibility["status"] == "incompatible"
                        
                        # Verify the workflow produces consistent results
                        assert classification["denial_type"] == remediation["denial_type"]
                        assert any("bundled" in step.lower() for step in remediation["steps"])
