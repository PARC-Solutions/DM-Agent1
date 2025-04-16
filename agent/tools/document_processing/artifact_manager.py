"""
Document Artifact Management Module

This module provides tools for managing document artifacts during processing, ensuring
secure handling of PHI, artifact linking to conversation sessions, and proper document cleanup.
"""

import base64
import io
import json
import logging
import os
import shutil
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from google.adk.tools import tool
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Default configurations
DEFAULT_ARTIFACT_DIR = "temp_artifacts"
DEFAULT_RETENTION_HOURS = 24  # Keep artifacts for 24 hours by default
MAX_ARTIFACT_SIZE_MB = 50  # Maximum size for uploaded artifacts (50MB)


class ArtifactMetadata(BaseModel):
    """Metadata for a document artifact."""
    artifact_id: str
    filename: str
    content_type: str
    session_id: Optional[str] = None
    upload_time: datetime
    expiration_time: datetime
    size_bytes: int
    additional_info: Dict[str, Any] = {}


class ArtifactManager:
    """
    Manager for document artifacts, handling secure storage and lifecycle management.
    """
    
    def __init__(self, 
                 artifact_dir: str = DEFAULT_ARTIFACT_DIR,
                 retention_hours: int = DEFAULT_RETENTION_HOURS):
        """
        Initialize the artifact manager.
        
        Args:
            artifact_dir: Directory to store artifacts
            retention_hours: How long to keep artifacts before cleanup
        """
        self.artifact_dir = artifact_dir
        self.retention_hours = retention_hours
        self.metadata_path = os.path.join(artifact_dir, "artifact_metadata.json")
        
        # Create artifact directory if it doesn't exist
        os.makedirs(artifact_dir, exist_ok=True)
        
        # Load existing metadata if available
        self.artifacts_metadata = {}
        self._load_metadata()
        
        # Clean up expired artifacts on initialization
        self.cleanup_expired_artifacts()
    
    def _load_metadata(self):
        """Load artifact metadata from file if it exists."""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    metadata_json = json.load(f)
                    
                    # Convert string timestamps back to datetime objects
                    for artifact_id, metadata in metadata_json.items():
                        if 'upload_time' in metadata:
                            metadata['upload_time'] = datetime.fromisoformat(metadata['upload_time'])
                        if 'expiration_time' in metadata:
                            metadata['expiration_time'] = datetime.fromisoformat(metadata['expiration_time'])
                    
                    self.artifacts_metadata = metadata_json
            except Exception as e:
                logger.error(f"Error loading artifact metadata: {e}")
                self.artifacts_metadata = {}
    
    def _save_metadata(self):
        """Save artifact metadata to file."""
        try:
            # Convert datetime objects to ISO format for JSON serialization
            metadata_json = {}
            for artifact_id, metadata in self.artifacts_metadata.items():
                metadata_copy = metadata.copy()
                if isinstance(metadata_copy.get('upload_time'), datetime):
                    metadata_copy['upload_time'] = metadata_copy['upload_time'].isoformat()
                if isinstance(metadata_copy.get('expiration_time'), datetime):
                    metadata_copy['expiration_time'] = metadata_copy['expiration_time'].isoformat()
                metadata_json[artifact_id] = metadata_copy
            
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata_json, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving artifact metadata: {e}")
    
    def store_artifact(self, 
                      document_data: Union[bytes, str], 
                      filename: str,
                      content_type: str,
                      session_id: Optional[str] = None,
                      additional_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a document artifact securely.
        
        Args:
            document_data: The document data (either binary or Base64 encoded)
            filename: Original filename
            content_type: MIME type of the document
            session_id: Optional session ID to link the artifact to
            additional_info: Additional metadata to store with the artifact
            
        Returns:
            Artifact ID for future reference
        """
        # Generate a unique artifact ID
        artifact_id = str(uuid.uuid4())
        
        # Ensure document_data is bytes
        if isinstance(document_data, str):
            try:
                document_data = base64.b64decode(document_data)
            except Exception as e:
                logger.error(f"Failed to decode Base64 string: {e}")
                raise ValueError("Invalid document data: not a valid Base64 string")
        
        # Check size limits
        size_bytes = len(document_data)
        if size_bytes > (MAX_ARTIFACT_SIZE_MB * 1024 * 1024):
            raise ValueError(f"Document exceeds maximum size of {MAX_ARTIFACT_SIZE_MB}MB")
        
        # Create a file path for the artifact
        artifact_path = os.path.join(self.artifact_dir, artifact_id)
        
        # Save the file
        with open(artifact_path, 'wb') as f:
            f.write(document_data)
        
        # Set expiration time
        upload_time = datetime.now()
        expiration_time = upload_time + timedelta(hours=self.retention_hours)
        
        # Create metadata
        metadata = {
            "artifact_id": artifact_id,
            "filename": filename,
            "content_type": content_type,
            "session_id": session_id,
            "upload_time": upload_time,
            "expiration_time": expiration_time,
            "size_bytes": size_bytes,
            "additional_info": additional_info or {}
        }
        
        # Store metadata
        self.artifacts_metadata[artifact_id] = metadata
        self._save_metadata()
        
        return artifact_id
    
    def get_artifact(self, artifact_id: str) -> Optional[bytes]:
        """
        Retrieve a stored artifact by ID.
        
        Args:
            artifact_id: The ID of the artifact to retrieve
            
        Returns:
            The artifact data as bytes, or None if not found
        """
        if artifact_id not in self.artifacts_metadata:
            return None
        
        artifact_path = os.path.join(self.artifact_dir, artifact_id)
        if not os.path.exists(artifact_path):
            # Metadata exists but file doesn't - clean up metadata
            del self.artifacts_metadata[artifact_id]
            self._save_metadata()
            return None
        
        with open(artifact_path, 'rb') as f:
            return f.read()
    
    def get_artifact_metadata(self, artifact_id: str) -> Optional[Dict]:
        """
        Get metadata for an artifact.
        
        Args:
            artifact_id: The ID of the artifact
            
        Returns:
            Metadata dictionary or None if not found
        """
        return self.artifacts_metadata.get(artifact_id)
    
    def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact and its metadata.
        
        Args:
            artifact_id: The ID of the artifact to delete
            
        Returns:
            True if deleted, False if not found
        """
        if artifact_id not in self.artifacts_metadata:
            return False
        
        # Delete the file
        artifact_path = os.path.join(self.artifact_dir, artifact_id)
        if os.path.exists(artifact_path):
            os.remove(artifact_path)
        
        # Remove metadata
        del self.artifacts_metadata[artifact_id]
        self._save_metadata()
        
        return True
    
    def get_artifacts_by_session(self, session_id: str) -> List[Dict]:
        """
        Get all artifacts associated with a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            List of artifact metadata dictionaries
        """
        return [
            metadata for metadata in self.artifacts_metadata.values()
            if metadata.get("session_id") == session_id
        ]
    
    def cleanup_expired_artifacts(self) -> int:
        """
        Clean up all expired artifacts.
        
        Returns:
            Number of artifacts cleaned up
        """
        now = datetime.now()
        expired_artifacts = [
            artifact_id for artifact_id, metadata in self.artifacts_metadata.items()
            if metadata.get("expiration_time", now) < now
        ]
        
        for artifact_id in expired_artifacts:
            self.delete_artifact(artifact_id)
        
        return len(expired_artifacts)
    
    def update_session_id(self, artifact_id: str, session_id: str) -> bool:
        """
        Update the session ID for an artifact.
        
        Args:
            artifact_id: The ID of the artifact
            session_id: The new session ID
            
        Returns:
            True if updated, False if artifact not found
        """
        if artifact_id not in self.artifacts_metadata:
            return False
        
        self.artifacts_metadata[artifact_id]["session_id"] = session_id
        self._save_metadata()
        
        return True


# Create a global instance of the artifact manager
_artifact_manager = None


def get_artifact_manager() -> ArtifactManager:
    """
    Get or create the global artifact manager instance.
    
    Returns:
        The artifact manager
    """
    global _artifact_manager
    if _artifact_manager is None:
        _artifact_manager = ArtifactManager()
    return _artifact_manager


@tool
def store_document(document_data: Union[bytes, str], 
                  filename: str,
                  content_type: str,
                  session_id: Optional[str] = None) -> Dict:
    """
    Securely store a document for processing.
    
    Args:
        document_data: The document data (either binary or Base64 encoded)
        filename: Original filename
        content_type: MIME type of the document (e.g., "application/pdf")
        session_id: Optional session ID to link the document to
        
    Returns:
        dict: Information about the stored document, including its artifact ID
    """
    logger.info(f"Storing document {filename} for processing")
    
    try:
        artifact_manager = get_artifact_manager()
        
        artifact_id = artifact_manager.store_artifact(
            document_data=document_data,
            filename=filename,
            content_type=content_type,
            session_id=session_id
        )
        
        return {
            "status": "success",
            "artifact_id": artifact_id,
            "message": f"Document {filename} stored successfully"
        }
        
    except Exception as e:
        logger.error(f"Error storing document: {e}")
        return {
            "status": "error",
            "message": f"Failed to store document: {str(e)}"
        }


@tool
def retrieve_document(artifact_id: str, as_base64: bool = False) -> Dict:
    """
    Retrieve a stored document by its artifact ID.
    
    Args:
        artifact_id: The ID of the stored document
        as_base64: Whether to return the document as Base64-encoded string
        
    Returns:
        dict: Document data and metadata
    """
    logger.info(f"Retrieving document with ID {artifact_id}")
    
    try:
        artifact_manager = get_artifact_manager()
        
        # Get document data
        document_data = artifact_manager.get_artifact(artifact_id)
        if document_data is None:
            return {
                "status": "error",
                "message": f"Document with ID {artifact_id} not found"
            }
        
        # Get metadata
        metadata = artifact_manager.get_artifact_metadata(artifact_id)
        
        # Convert to Base64 if requested
        if as_base64:
            document_data = base64.b64encode(document_data).decode('utf-8')
        
        return {
            "status": "success",
            "filename": metadata.get("filename", "unknown"),
            "content_type": metadata.get("content_type", "application/octet-stream"),
            "size_bytes": len(document_data) if isinstance(document_data, bytes) else metadata.get("size_bytes", 0),
            "document_data": document_data if as_base64 else "<binary data>",
            "upload_time": metadata.get("upload_time").isoformat() if isinstance(metadata.get("upload_time"), datetime) else None,
            "message": "Document retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve document: {str(e)}"
        }


@tool
def delete_document(artifact_id: str) -> Dict:
    """
    Delete a stored document by its artifact ID.
    
    Args:
        artifact_id: The ID of the stored document
        
    Returns:
        dict: Result of the deletion operation
    """
    logger.info(f"Deleting document with ID {artifact_id}")
    
    try:
        artifact_manager = get_artifact_manager()
        
        success = artifact_manager.delete_artifact(artifact_id)
        if not success:
            return {
                "status": "error",
                "message": f"Document with ID {artifact_id} not found"
            }
        
        return {
            "status": "success",
            "message": f"Document with ID {artifact_id} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return {
            "status": "error",
            "message": f"Failed to delete document: {str(e)}"
        }


@tool
def list_session_documents(session_id: str) -> Dict:
    """
    List all documents associated with a session.
    
    Args:
        session_id: The session ID
        
    Returns:
        dict: List of documents and their metadata
    """
    logger.info(f"Listing documents for session {session_id}")
    
    try:
        artifact_manager = get_artifact_manager()
        
        artifacts = artifact_manager.get_artifacts_by_session(session_id)
        
        # Format the response
        documents = []
        for artifact in artifacts:
            # Convert datetime objects to ISO format strings
            artifact_copy = artifact.copy()
            if isinstance(artifact_copy.get('upload_time'), datetime):
                artifact_copy['upload_time'] = artifact_copy['upload_time'].isoformat()
            if isinstance(artifact_copy.get('expiration_time'), datetime):
                artifact_copy['expiration_time'] = artifact_copy['expiration_time'].isoformat()
            
            documents.append(artifact_copy)
        
        return {
            "status": "success",
            "session_id": session_id,
            "document_count": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        logger.error(f"Error listing session documents: {e}")
        return {
            "status": "error",
            "message": f"Failed to list session documents: {str(e)}"
        }
