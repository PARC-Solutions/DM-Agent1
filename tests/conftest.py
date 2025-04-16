"""
Pytest Configuration for Medical Billing Denial Agent Tests

This module contains fixtures and configuration for pytest to enable
effective testing of the Medical Billing Denial Agent system.
"""

import os
import pytest
import logging
from typing import Dict, Any

from agent.core.session_manager import SessionManager


# Configure logging for tests
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def session_manager():
    """Fixture that provides a SessionManager instance for testing."""
    return SessionManager()


@pytest.fixture
def sample_session_data() -> Dict[str, Any]:
    """Fixture that provides sample session data for testing."""
    return {
        "conversation_history": [
            {
                "timestamp": 1650000000.0,
                "user_input": "What does CARC code 16 mean?",
                "agent_response": "CARC code 16 indicates 'Claim/service lacks information or has submission/billing error(s).'",
                "metadata": {
                    "task_type": "denial_classification",
                    "intent": "code_explanation"
                }
            }
        ],
        "claim_details": {
            "patient_name": "SAMPLE PATIENT",
            "claim_number": "SAMPLE123",
            "date_of_service": "2025-01-15",
        },
        "denial_codes": ["16", "N479"],
        "documents": [
            {
                "document_id": "doc-sample1",
                "document_type": "cms1500",
                "added_timestamp": 1650000000.0,
                "metadata": {
                    "filename": "sample_cms1500.pdf",
                    "content_type": "application/pdf",
                    "page_count": 1
                }
            }
        ],
        "conversation_state": "analyzing_denial",
        "remediation_provided": False,
        "documents_processing": False,
        "created_at": 1650000000.0,
        "last_active": 1650000100.0
    }


@pytest.fixture
def sample_session(session_manager, sample_session_data):
    """Fixture that provides a sample session in the session manager."""
    session_id = session_manager.create_session()
    session_manager.update_session(session_id, sample_session_data)
    return session_id
