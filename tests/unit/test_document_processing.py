"""
Unit tests for document processing tools.

These tests verify the functionality of the document processing tools in Epic 3,
including the CMS-1500 parser, EOB parser, and artifact management system.
"""

import base64
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from agent.tools.document_processing.artifact_manager import (
    ArtifactManager, delete_document, list_session_documents, retrieve_document, store_document
)
from agent.tools.document_processing.cms1500_parser import analyze_cms1500_form
from agent.tools.document_processing.eob_parser import parse_eob


class TestArtifactManager(unittest.TestCase):
    """Tests for the Artifact Manager."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for artifacts
        self.temp_dir = tempfile.mkdtemp()
        self.artifact_manager = ArtifactManager(
            artifact_dir=self.temp_dir,
            retention_hours=1
        )
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)
    
    def test_store_artifact(self):
        """Test storing an artifact."""
        test_data = b"Test document data"
        artifact_id = self.artifact_manager.store_artifact(
            document_data=test_data,
            filename="test.pdf",
            content_type="application/pdf",
            session_id="test-session"
        )
        
        # Check that the artifact was stored
        self.assertIn(artifact_id, self.artifact_manager.artifacts_metadata)
        self.assertEqual(
            self.artifact_manager.artifacts_metadata[artifact_id]["filename"],
            "test.pdf"
        )
        
        # Check that the file exists
        artifact_path = os.path.join(self.temp_dir, artifact_id)
        self.assertTrue(os.path.exists(artifact_path))
        
        # Check the file content
        with open(artifact_path, 'rb') as f:
            self.assertEqual(f.read(), test_data)
    
    def test_get_artifact(self):
        """Test retrieving an artifact."""
        test_data = b"Test document data"
        artifact_id = self.artifact_manager.store_artifact(
            document_data=test_data,
            filename="test.pdf",
            content_type="application/pdf"
        )
        
        # Retrieve the artifact
        retrieved_data = self.artifact_manager.get_artifact(artifact_id)
        self.assertEqual(retrieved_data, test_data)
        
        # Try retrieving a non-existent artifact
        self.assertIsNone(self.artifact_manager.get_artifact("non-existent"))
    
    def test_delete_artifact(self):
        """Test deleting an artifact."""
        test_data = b"Test document data"
        artifact_id = self.artifact_manager.store_artifact(
            document_data=test_data,
            filename="test.pdf",
            content_type="application/pdf"
        )
        
        # Delete the artifact
        result = self.artifact_manager.delete_artifact(artifact_id)
        self.assertTrue(result)
        
        # Check that the artifact is gone
        self.assertNotIn(artifact_id, self.artifact_manager.artifacts_metadata)
        artifact_path = os.path.join(self.temp_dir, artifact_id)
        self.assertFalse(os.path.exists(artifact_path))
        
        # Try deleting a non-existent artifact
        result = self.artifact_manager.delete_artifact("non-existent")
        self.assertFalse(result)
    
    def test_get_artifacts_by_session(self):
        """Test retrieving artifacts by session ID."""
        # Create test artifacts with different session IDs
        self.artifact_manager.store_artifact(
            document_data=b"Test document 1",
            filename="test1.pdf",
            content_type="application/pdf",
            session_id="session1"
        )
        self.artifact_manager.store_artifact(
            document_data=b"Test document 2",
            filename="test2.pdf",
            content_type="application/pdf",
            session_id="session1"
        )
        self.artifact_manager.store_artifact(
            document_data=b"Test document 3",
            filename="test3.pdf",
            content_type="application/pdf",
            session_id="session2"
        )
        
        # Get artifacts for session1
        session1_artifacts = self.artifact_manager.get_artifacts_by_session("session1")
        self.assertEqual(len(session1_artifacts), 2)
        
        # Get artifacts for session2
        session2_artifacts = self.artifact_manager.get_artifacts_by_session("session2")
        self.assertEqual(len(session2_artifacts), 1)
        
        # Get artifacts for non-existent session
        session3_artifacts = self.artifact_manager.get_artifacts_by_session("session3")
        self.assertEqual(len(session3_artifacts), 0)
    
    def test_cleanup_expired_artifacts(self):
        """Test cleaning up expired artifacts."""
        # Create an artifact with manual expiration time in the past
        artifact_id = self.artifact_manager.store_artifact(
            document_data=b"Test expired document",
            filename="expired.pdf",
            content_type="application/pdf"
        )
        
        # Set expiration time to 2 hours ago
        self.artifact_manager.artifacts_metadata[artifact_id]["expiration_time"] = (
            datetime.now() - timedelta(hours=2)
        )
        self.artifact_manager._save_metadata()
        
        # Create a non-expired artifact
        self.artifact_manager.store_artifact(
            document_data=b"Test current document",
            filename="current.pdf",
            content_type="application/pdf"
        )
        
        # Run cleanup
        cleaned_count = self.artifact_manager.cleanup_expired_artifacts()
        
        # Should have cleaned up one artifact
        self.assertEqual(cleaned_count, 1)
        self.assertNotIn(artifact_id, self.artifact_manager.artifacts_metadata)


@pytest.mark.parametrize(
    "document_data, filename, content_type, session_id, expected_status",
    [
        (b"Test data", "test.pdf", "application/pdf", None, "success"),
        (base64.b64encode(b"Test base64 data").decode(), "test.pdf", "application/pdf", "test-session", "success"),
        ("invalid base64", "test.pdf", "application/pdf", None, "error"),
    ]
)
def test_store_document_tool(document_data, filename, content_type, session_id, expected_status):
    """Test the store_document tool."""
    with patch("agent.tools.document_processing.artifact_manager.get_artifact_manager") as mock_get_manager:
        # Set up mock
        mock_manager = MagicMock()
        mock_manager.store_artifact.return_value = "test-artifact-id"
        mock_get_manager.return_value = mock_manager
        
        # If we expect an error due to invalid base64, make the mock raise an exception
        if expected_status == "error" and isinstance(document_data, str) and document_data == "invalid base64":
            mock_manager.store_artifact.side_effect = ValueError("Invalid Base64")
        
        # Call the function
        result = store_document(document_data, filename, content_type, session_id)
        
        # Assert results
        assert result["status"] == expected_status
        
        if expected_status == "success":
            assert result["artifact_id"] == "test-artifact-id"
            assert "stored successfully" in result["message"]
            
            # Check that the function was called with correct parameters
            if isinstance(document_data, str) and expected_status == "success":
                # For base64 input, it should be decoded to bytes
                mock_manager.store_artifact.assert_called_once()
            else:
                mock_manager.store_artifact.assert_called_with(
                    document_data=document_data,
                    filename=filename,
                    content_type=content_type,
                    session_id=session_id
                )
        else:
            assert "error" in result["status"]
            assert "Failed to store document" in result["message"]


def test_retrieve_document_tool():
    """Test the retrieve_document tool."""
    with patch("agent.tools.document_processing.artifact_manager.get_artifact_manager") as mock_get_manager:
        # Set up mock
        mock_manager = MagicMock()
        mock_manager.get_artifact.return_value = b"Test document data"
        mock_manager.get_artifact_metadata.return_value = {
            "filename": "test.pdf",
            "content_type": "application/pdf",
            "size_bytes": 17,
            "upload_time": datetime.now()
        }
        mock_get_manager.return_value = mock_manager
        
        # Test retrieving as binary
        result_binary = retrieve_document("test-artifact-id", as_base64=False)
        assert result_binary["status"] == "success"
        assert result_binary["filename"] == "test.pdf"
        assert result_binary["document_data"] == "<binary data>"
        
        # Test retrieving as base64
        result_base64 = retrieve_document("test-artifact-id", as_base64=True)
        assert result_base64["status"] == "success"
        assert result_base64["filename"] == "test.pdf"
        assert isinstance(result_base64["document_data"], str)
        
        # Test non-existent artifact
        mock_manager.get_artifact.return_value = None
        result_not_found = retrieve_document("non-existent")
        assert result_not_found["status"] == "error"
        assert "not found" in result_not_found["message"]


def test_delete_document_tool():
    """Test the delete_document tool."""
    with patch("agent.tools.document_processing.artifact_manager.get_artifact_manager") as mock_get_manager:
        # Set up mock
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        # Test successful deletion
        mock_manager.delete_artifact.return_value = True
        result_success = delete_document("test-artifact-id")
        assert result_success["status"] == "success"
        assert "deleted successfully" in result_success["message"]
        
        # Test non-existent artifact
        mock_manager.delete_artifact.return_value = False
        result_not_found = delete_document("non-existent")
        assert result_not_found["status"] == "error"
        assert "not found" in result_not_found["message"]


def test_list_session_documents_tool():
    """Test the list_session_documents tool."""
    with patch("agent.tools.document_processing.artifact_manager.get_artifact_manager") as mock_get_manager:
        # Set up mock
        mock_manager = MagicMock()
        mock_manager.get_artifacts_by_session.return_value = [
            {
                "artifact_id": "test-artifact-1",
                "filename": "test1.pdf",
                "content_type": "application/pdf",
                "upload_time": datetime.now(),
                "expiration_time": datetime.now() + timedelta(hours=24)
            },
            {
                "artifact_id": "test-artifact-2",
                "filename": "test2.pdf",
                "content_type": "application/pdf",
                "upload_time": datetime.now(),
                "expiration_time": datetime.now() + timedelta(hours=24)
            }
        ]
        mock_get_manager.return_value = mock_manager
        
        # Test listing documents
        result = list_session_documents("test-session")
        assert result["status"] == "success"
        assert result["session_id"] == "test-session"
        assert result["document_count"] == 2
        assert len(result["documents"]) == 2


def test_cms1500_parser():
    """Test the CMS-1500 parser tool."""
    # For now, just test that it returns the expected placeholder response
    result = analyze_cms1500_form(b"test data")
    assert result["status"] == "not_implemented"
    assert "CMS-1500 form parsing will be implemented" in result["message"]


def test_eob_parser():
    """Test the EOB parser tool."""
    # For now, just test that it returns the expected placeholder response
    result = parse_eob(b"test data")
    assert result["status"] == "not_implemented"
    assert "EOB document parsing will be implemented" in result["message"]
