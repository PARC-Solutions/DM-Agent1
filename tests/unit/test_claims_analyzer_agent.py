"""
Claims Analyzer Agent Tests

This module contains tests for the ClaimsAnalyzerAgent class to verify that
it initializes correctly and can analyze claim documents properly.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open

from agent.analyzers.claims_analyzer import ClaimsAnalyzerAgent


def test_claims_analyzer_initialization():
    """Test that the claims analyzer agent initializes correctly."""
    agent = ClaimsAnalyzerAgent()
    
    # Verify agent attributes
    assert "missing_information" in agent.common_errors
    assert "invalid_format" in agent.common_errors
    assert "coding_issues" in agent.common_errors
    
    # Verify field mappings
    assert "patient_info" in agent.cms1500_field_map
    assert "provider_info" in agent.cms1500_field_map
    assert "service_info" in agent.cms1500_field_map
    
    assert "payer_info" in agent.eob_field_map
    assert "claim_info" in agent.eob_field_map
    assert "denial_info" in agent.eob_field_map


@patch('agent.analyzers.claims_analyzer.parse_cms1500')
def test_analyze_cms1500(mock_parse):
    """Test analysis of CMS-1500 form."""
    # Mock the return value from parse_cms1500
    mock_parse.return_value = {
        "status": "success",
        "extracted_fields": {
            "patient_name": "John Doe",
            "patient_dob": "01/01/1970",
            "patient_id": "12345",
            "provider_npi": "1234567890",
            "diagnosis_codes": ["Z23"],
            "procedure_codes": ["99213"],
            "date_of_service": ["01/15/2025"]
        },
        "field_confidence": {
            "patient_name": 0.95,
            "patient_dob": 0.9
        },
        "overall_confidence": 0.9
    }
    
    # Initialize agent and analyze document
    agent = ClaimsAnalyzerAgent()
    result = agent.analyze_cms1500(b"mock document data")
    
    # Verify result
    assert result["status"] == "success"
    assert result["document_type"] == "CMS-1500"
    assert "extracted_fields" in result
    assert "field_confidence" in result
    assert "potential_issues" in result
    assert "overall_confidence" in result
    
    # Verify parse_cms1500 was called
    mock_parse.assert_called_once()


@patch('agent.analyzers.claims_analyzer.parse_cms1500')
def test_analyze_cms1500_with_base64(mock_parse):
    """Test analysis of CMS-1500 form with base64 encoded data."""
    # Mock the return value from parse_cms1500
    mock_parse.return_value = {
        "status": "success",
        "extracted_fields": {
            "patient_name": "John Doe",
            "provider_npi": "1234567890"
        },
        "overall_confidence": 0.8
    }
    
    # Initialize agent and analyze document
    agent = ClaimsAnalyzerAgent()
    
    # Create base64 encoded string (this is not actual base64 content)
    base64_data = "bW9jayBkb2N1bWVudCBkYXRh"
    
    # Patch base64.b64decode to return expected bytes
    with patch('base64.b64decode', return_value=b"mock document data"):
        result = agent.analyze_cms1500(base64_data)
    
    # Verify result
    assert result["status"] == "success"
    assert "extracted_fields" in result
    assert "potential_issues" in result
    
    # Verify parse_cms1500 was called
    mock_parse.assert_called_once()


@patch('agent.analyzers.claims_analyzer.parse_cms1500')
def test_analyze_cms1500_with_error(mock_parse):
    """Test analysis of CMS-1500 form with error from parser."""
    # Mock the return value from parse_cms1500
    mock_parse.return_value = {
        "status": "error",
        "message": "Failed to parse document"
    }
    
    # Initialize agent and analyze document
    agent = ClaimsAnalyzerAgent()
    result = agent.analyze_cms1500(b"mock document data")
    
    # Verify result
    assert result["status"] == "error"
    assert "message" in result
    assert "Failed to parse document" in result["message"]


@patch('agent.analyzers.claims_analyzer.parse_eob')
def test_analyze_eob(mock_parse):
    """Test analysis of EOB document."""
    # Mock the return value from parse_eob
    mock_parse.return_value = {
        "status": "success",
        "extracted_fields": {
            "claim_number": "ABC123",
            "patient_name": "John Doe",
            "provider_name": "Dr. Smith",
            "total_billed": "1000.00",
            "total_paid": "800.00",
            "carc_codes": ["16"],
            "rarc_codes": ["N01"],
            "service_lines": [
                {
                    "procedure_code": "99213",
                    "billed_amount": "200.00",
                    "paid_amount": "160.00",
                    "denial_reason": "CARC 16",
                    "remark_codes": "RARC N01"
                }
            ]
        },
        "field_confidence": {},
        "overall_confidence": 0.85
    }
    
    # Initialize agent and analyze document
    agent = ClaimsAnalyzerAgent()
    result = agent.analyze_eob(b"mock document data")
    
    # Verify result
    assert result["status"] == "success"
    assert result["document_type"] == "EOB"
    assert "extracted_fields" in result
    assert "denial_codes" in result
    assert "carc_codes" in result["denial_codes"]
    assert "rarc_codes" in result["denial_codes"]
    assert "potential_issues" in result
    assert "overall_confidence" in result
    
    # Verify parse_eob was called
    mock_parse.assert_called_once()


def test_extract_denial_codes():
    """Test extraction of denial codes from EOB data."""
    agent = ClaimsAnalyzerAgent()
    
    # Create test EOB data
    eob_data = {
        "carc_codes": ["16", "50"],
        "rarc_codes": ["N01"],
        "group_codes": ["CO"],
        "service_lines": [
            {
                "denial_reason": "Claim denied CARC 97",
                "remark_codes": "RARC M76"
            },
            {
                "denial_reason": "CARC 29 - timely filing",
                "remark_codes": "N/A"
            }
        ]
    }
    
    # Extract codes
    result = agent._extract_denial_codes(eob_data)
    
    # Verify result
    assert "carc_codes" in result
    assert "rarc_codes" in result
    assert "group_codes" in result
    
    # Verify existing codes are preserved
    assert "16" in result["carc_codes"]
    assert "50" in result["carc_codes"]
    assert "N01" in result["rarc_codes"]
    assert "CO" in result["group_codes"]
    
    # Verify extracted codes are added
    assert "97" in result["carc_codes"]
    assert "29" in result["carc_codes"]
    assert "M76" in result["rarc_codes"]


def test_extract_codes_from_text():
    """Test extraction of codes from text."""
    agent = ClaimsAnalyzerAgent()
    
    # Test CARC code extraction
    carc_text = "Claim denied per CARC 16, CARC 97, and CARC 50."
    carc_codes = agent._extract_codes_from_text(carc_text, "CARC")
    
    # Verify CARC codes
    assert "16" in carc_codes
    assert "97" in carc_codes
    assert "50" in carc_codes
    
    # Test RARC code extraction
    rarc_text = "Additional information from RARC M76 and RARC N01."
    rarc_codes = agent._extract_codes_from_text(rarc_text, "RARC")
    
    # Verify RARC codes
    assert "M76" in rarc_codes
    assert "N01" in rarc_codes


def test_is_valid_diagnosis_code():
    """Test validation of diagnosis code format."""
    agent = ClaimsAnalyzerAgent()
    
    # Valid ICD-10 codes
    assert agent._is_valid_diagnosis_code("A01")
    assert agent._is_valid_diagnosis_code("Z23")
    assert agent._is_valid_diagnosis_code("F10.2")
    assert agent._is_valid_diagnosis_code("S82.101A")
    
    # Invalid codes
    assert not agent._is_valid_diagnosis_code("123")
    assert not agent._is_valid_diagnosis_code("ABCD")
    assert not agent._is_valid_diagnosis_code("")


def test_is_valid_procedure_code():
    """Test validation of procedure code format."""
    agent = ClaimsAnalyzerAgent()
    
    # Valid CPT codes
    assert agent._is_valid_procedure_code("99213")
    assert agent._is_valid_procedure_code("12345")
    
    # Valid HCPCS codes
    assert agent._is_valid_procedure_code("G0001")
    assert agent._is_valid_procedure_code("J0100")
    
    # Invalid codes
    assert not agent._is_valid_procedure_code("ABC")
    assert not agent._is_valid_procedure_code("1234")
    assert not agent._is_valid_procedure_code("A12345")
    assert not agent._is_valid_procedure_code("")


def test_is_valid_date_format():
    """Test validation of date format."""
    agent = ClaimsAnalyzerAgent()
    
    # Valid date formats
    assert agent._is_valid_date_format("01/15/2025")
    assert agent._is_valid_date_format("12-31-2025")
    
    # Invalid date formats
    assert not agent._is_valid_date_format("2025/01/15")
    assert not agent._is_valid_date_format("Jan 15, 2025")
    assert not agent._is_valid_date_format("01/15")
    assert not agent._is_valid_date_format("")


def test_analyze_cms1500_data():
    """Test analysis of extracted CMS-1500 data for potential issues."""
    agent = ClaimsAnalyzerAgent()
    
    # Create test extracted fields
    extracted_fields = {
        "patient_name": "John Doe",
        "patient_dob": "01/01/1970",
        "provider_npi": "12345",  # Invalid NPI format
        "diagnosis_codes": ["Z23", "ABC"],  # Second code is invalid
        "procedure_codes": ["99213"],
        "date_of_service": ["01/15/2025", "Jan 20"]  # Second date is invalid
    }
    
    # Analyze data
    result = agent._analyze_cms1500_data(extracted_fields)
    
    # Verify result
    assert "potential_issues" in result
    assert "missing_fields" in result
    assert "invalid_fields" in result
    
    # Verify specific issues
    assert "patient_id" in result["missing_fields"]
    assert "provider_npi" in result["invalid_fields"]
    assert any("Invalid diagnosis code" in issue for issue in result["potential_issues"])
    assert any("Invalid date format" in issue for issue in result["potential_issues"])


def test_analyze_eob_data():
    """Test analysis of extracted EOB data for potential issues."""
    agent = ClaimsAnalyzerAgent()
    
    # Create test with missing fields
    missing_fields = {
        "patient_name": "John Doe"
        # Missing claim_number, provider_name, total_billed, total_paid, service_lines
    }
    
    # Analyze data with missing fields
    missing_result = agent._analyze_eob_data(missing_fields)
    
    # Verify missing fields result
    assert "potential_issues" in missing_result
    assert "missing_fields" in missing_result
    assert "claim_number" in missing_result["missing_fields"]
    assert len(missing_result["potential_issues"]) >= 5  # Should have at least 5 issues
    
    # Create test with payment discrepancy
    payment_fields = {
        "claim_number": "ABC123",
        "patient_name": "John Doe",
        "provider_name": "Dr. Smith",
        "total_billed": "1000.00",
        "total_paid": "800.00",
        "service_lines": []
    }
    
    # Analyze data with payment discrepancy
    payment_result = agent._analyze_eob_data(payment_fields)
    
    # Verify payment discrepancy result
    assert any("Payment discrepancy" in issue for issue in payment_result["potential_issues"])
    
    # Create test with missing denial codes
    no_codes = {
        "claim_number": "ABC123",
        "patient_name": "John Doe",
        "provider_name": "Dr. Smith",
        "total_billed": "1000.00",
        "total_paid": "800.00",
        "service_lines": [
            {
                "procedure_code": "99213",
                "billed_amount": "1000.00",
                "paid_amount": "800.00"
                # No denial_reason or remark_codes
            }
        ]
    }
    
    # Analyze data with no codes
    no_codes_result = agent._analyze_eob_data(no_codes)
    
    # Verify no codes result
    assert any("No denial codes found" in issue for issue in no_codes_result["potential_issues"])


@patch('agent.analyzers.claims_analyzer.ClaimsAnalyzerAgent.analyze_cms1500')
@patch('agent.analyzers.claims_analyzer.ClaimsAnalyzerAgent.analyze_eob')
def test_analyze_document(mock_analyze_eob, mock_analyze_cms1500):
    """Test analyzing a document based on its type."""
    agent = ClaimsAnalyzerAgent()
    
    # Set up return values
    mock_analyze_cms1500.return_value = {"status": "success", "document_type": "CMS-1500"}
    mock_analyze_eob.return_value = {"status": "success", "document_type": "EOB"}
    
    # Test CMS-1500 analysis
    cms_result = agent.analyze_document(b"document data", "CMS-1500")
    assert cms_result["document_type"] == "CMS-1500"
    mock_analyze_cms1500.assert_called_once()
    
    # Reset mocks
    mock_analyze_cms1500.reset_mock()
    mock_analyze_eob.reset_mock()
    
    # Test CMS1500 analysis (alternate format)
    cms_result = agent.analyze_document(b"document data", "cms1500")
    assert cms_result["document_type"] == "CMS-1500"
    mock_analyze_cms1500.assert_called_once()
    
    # Reset mocks
    mock_analyze_cms1500.reset_mock()
    mock_analyze_eob.reset_mock()
    
    # Test EOB analysis
    eob_result = agent.analyze_document(b"document data", "EOB")
    assert eob_result["document_type"] == "EOB"
    mock_analyze_eob.assert_called_once()
    
    # Reset mocks
    mock_analyze_cms1500.reset_mock()
    mock_analyze_eob.reset_mock()
    
    # Test unsupported document type
    unsupported_result = agent.analyze_document(b"document data", "UNSUPPORTED")
    assert unsupported_result["status"] == "error"
    assert "Unsupported document type" in unsupported_result["message"]
    assert not mock_analyze_cms1500.called
    assert not mock_analyze_eob.called


def test_identify_claim_issues():
    """Test identification of claim issues."""
    agent = ClaimsAnalyzerAgent()
    
    # Create test claim data with several issues
    claim_data = {
        "patient_name": "John Doe",
        # Missing patient_dob and patient_id
        "provider_npi": "123",  # Invalid format
        "diagnosis_codes": ["Z23", "ABC"],  # Second code is invalid
        "procedure_codes": ["99213", "12AB"]  # Second code is invalid
    }
    
    # Identify issues
    result = agent.identify_claim_issues(claim_data)
    
    # Verify result
    assert result["status"] == "success"
    assert "issues" in result
    assert "recommendations" in result
    assert result["issue_count"] > 0
    
    # Verify categories of issues
    categories = [issue["category"] for issue in result["issues"]]
    assert "missing_information" in categories
    assert "invalid_format" in categories
    
    # Verify recommendations
    assert any("Review claim for completeness" in rec for rec in result["recommendations"])
    assert any("Check format" in rec for rec in result["recommendations"])
