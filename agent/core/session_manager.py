"""
Session Manager Module

This module handles the creation, retrieval, and management of conversation sessions
for the Medical Billing Denial Agent system. It ensures that conversation context
is maintained across interactions and handles secure storage of session data.

Features:
- Session creation and management
- Conversation history tracking
- Document reference persistence
- Context storage across conversation turns
- Session timeout and recovery
"""

import logging
import os
import time
import uuid
import json
from typing import Any, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages conversation sessions for the Medical Billing Denial Agent.
    
    This class provides an interface for creating, retrieving, and updating
    sessions, as well as managing session context and history. It ensures that
    session data is securely stored and properly maintained throughout the
    conversation lifecycle.
    
    Features:
    - Session lifecycle management (creation, retrieval, deletion)
    - Conversation history tracking
    - Contextual information storage and retrieval
    - Session state persistence
    - Document reference management
    - Automatic session expiration handling
    
    Note: This is a simplified implementation that uses an in-memory dictionary.
    In a production environment, this would be replaced with a more robust
    storage solution such as a database or cloud storage service.
    """
    
    def __init__(self):
        """Initialize the SessionManager with appropriate configuration."""
        logger.info("Initializing SessionManager")
        
        self.session_ttl = int(os.getenv("SESSION_TTL", 3600))  # Default: 1 hour
        self.max_history_length = int(os.getenv("MAX_HISTORY_LENGTH", 10))  # Default: 10 turns
        self.sessions = {}  # In-memory storage for sessions
        
        # Define standard session fields for proper schema validation
        self.standard_fields = {
            "created_at", "last_active", "conversation_history", 
            "claim_details", "denial_codes", "documents", 
            "conversation_state", "remediation_provided",
            "documents_processing"
        }
        
        logger.info(f"SessionManager initialized with TTL: {self.session_ttl} seconds")
    
    def create_session(self, initial_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for a conversation.
        
        Args:
            initial_context: Optional initial context data for the session
            
        Returns:
            str: The ID of the newly created session
        """
        session_id = str(uuid.uuid4())
        
        # Initialize session with empty context
        session_context = {
            "created_at": time.time(),
            "last_active": time.time(),
            "conversation_history": [],
            "claim_details": {},
            "denial_codes": [],
            "documents": [],
            "conversation_state": "greeting",  # Initial state
            "remediation_provided": False,
            "documents_processing": False
        }
        
        # Add any initial context if provided
        if initial_context:
            for key, value in initial_context.items():
                if key in self.standard_fields:
                    session_context[key] = value
                else:
                    logger.warning(f"Ignoring non-standard field in initial context: {key}")
        
        # Store the session
        self.sessions[session_id] = session_context
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by its ID.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: The session context, or None if not found
        """
        try:
            session = self.sessions.get(session_id)
            
            # Check if session exists and is not expired
            if session:
                current_time = time.time()
                if current_time - session["last_active"] > self.session_ttl:
                    # Session expired
                    logger.info(f"Session {session_id} has expired")
                    self.delete_session(session_id)
                    return None
                
                # Update last active timestamp
                session["last_active"] = current_time
                
            return session
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """
        Update a session with new context information.
        
        Args:
            session_id: The ID of the session to update
            context_updates: Dictionary of context values to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            session = self.get_session(session_id)
            
            if not session:
                logger.warning(f"Attempted to update nonexistent session: {session_id}")
                return False
                
            # Update the session context
            session.update(context_updates)
            session["last_active"] = time.time()
            
            # Store the updated session
            self.sessions[session_id] = session
            
            logger.debug(f"Updated session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    def add_conversation_turn(self, session_id: str, user_input: str, agent_response: str, 
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a conversation turn to the session history.
        
        Args:
            session_id: The ID of the session
            user_input: The user's message
            agent_response: The agent's response
            metadata: Optional metadata about the turn (e.g., intent, task type)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            session = self.get_session(session_id)
            
            if not session:
                logger.warning(f"Attempted to update nonexistent session: {session_id}")
                return False
            
            # Add the conversation turn to history
            if "conversation_history" not in session:
                session["conversation_history"] = []
                
            # Create the conversation turn with metadata
            turn = {
                "timestamp": time.time(),
                "user_input": user_input,
                "agent_response": agent_response
            }
            
            # Add metadata if provided
            if metadata:
                turn["metadata"] = metadata
                
            # Add the turn to history
            session["conversation_history"].append(turn)
            
            # Trim history if it exceeds the maximum length
            if len(session["conversation_history"]) > self.max_history_length:
                # Remove oldest turns but keep the first turn for context
                first_turn = session["conversation_history"][0]
                session["conversation_history"] = [first_turn] + session["conversation_history"][-(self.max_history_length-1):]
                logger.debug(f"Trimmed conversation history for session {session_id} to {self.max_history_length} turns")
            
            session["last_active"] = time.time()
            
            # Store the updated session
            self.sessions[session_id] = session
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding conversation turn to session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session by its ID.
        
        Args:
            session_id: The ID of the session to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Deleted session: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
            
    def add_document_reference(self, session_id: str, document_id: str, 
                              document_type: str, document_metadata: Dict[str, Any]) -> bool:
        """
        Add a reference to a document in the session.
        
        Args:
            session_id: The ID of the session
            document_id: Unique identifier for the document
            document_type: Type of document (e.g., "cms1500", "eob")
            document_metadata: Metadata about the document
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            session = self.get_session(session_id)
            
            if not session:
                logger.warning(f"Attempted to update nonexistent session: {session_id}")
                return False
            
            # Initialize documents list if it doesn't exist
            if "documents" not in session:
                session["documents"] = []
                
            # Add document reference
            document_info = {
                "document_id": document_id,
                "document_type": document_type,
                "added_timestamp": time.time(),
                "metadata": document_metadata
            }
            
            # Check if document already exists (update if it does)
            existing_doc_index = None
            for i, doc in enumerate(session["documents"]):
                if doc.get("document_id") == document_id:
                    existing_doc_index = i
                    break
                    
            if existing_doc_index is not None:
                session["documents"][existing_doc_index] = document_info
                logger.debug(f"Updated document reference {document_id} in session {session_id}")
            else:
                session["documents"].append(document_info)
                logger.debug(f"Added document reference {document_id} to session {session_id}")
            
            session["last_active"] = time.time()
            
            # Store the updated session
            self.sessions[session_id] = session
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding document reference to session {session_id}: {e}")
            return False
    
    def get_document_references(self, session_id: str, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get document references from a session.
        
        Args:
            session_id: The ID of the session
            document_type: Optional filter by document type
            
        Returns:
            List[Dict[str, Any]]: List of document references
        """
        try:
            session = self.get_session(session_id)
            
            if not session:
                logger.warning(f"Attempted to retrieve documents from nonexistent session: {session_id}")
                return []
                
            # Get documents list, or empty list if none exist
            documents = session.get("documents", [])
            
            # Filter by document type if specified
            if document_type:
                documents = [doc for doc in documents if doc.get("document_type") == document_type]
                
            return documents
                
        except Exception as e:
            logger.error(f"Error retrieving document references from session {session_id}: {e}")
            return []
    
    def remove_document_reference(self, session_id: str, document_id: str) -> bool:
        """
        Remove a document reference from a session.
        
        Args:
            session_id: The ID of the session
            document_id: The ID of the document to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            session = self.get_session(session_id)
            
            if not session:
                logger.warning(f"Attempted to update nonexistent session: {session_id}")
                return False
                
            # Check if documents list exists
            if "documents" not in session:
                logger.warning(f"No documents in session {session_id}")
                return False
                
            # Find and remove the document
            initial_count = len(session["documents"])
            session["documents"] = [doc for doc in session["documents"] if doc.get("document_id") != document_id]
            
            # Check if any documents were removed
            if len(session["documents"]) == initial_count:
                logger.warning(f"Document {document_id} not found in session {session_id}")
                return False
                
            session["last_active"] = time.time()
            
            # Store the updated session
            self.sessions[session_id] = session
            
            logger.debug(f"Removed document reference {document_id} from session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing document reference from session {session_id}: {e}")
            return False
            
    def get_conversation_history(self, session_id: str, max_turns: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history from a session.
        
        Args:
            session_id: The ID of the session
            max_turns: Optional maximum number of turns to retrieve (most recent)
            
        Returns:
            List[Dict[str, Any]]: List of conversation turns
        """
        try:
            session = self.get_session(session_id)
            
            if not session:
                logger.warning(f"Attempted to retrieve history from nonexistent session: {session_id}")
                return []
                
            # Get conversation history, or empty list if none exists
            history = session.get("conversation_history", [])
            
            # Return limited number of turns if specified
            if max_turns and max_turns > 0:
                # Always include the first turn for context if it exists
                if len(history) > max_turns:
                    return [history[0]] + history[-(max_turns-1):]
                    
            return history
                
        except Exception as e:
            logger.error(f"Error retrieving conversation history from session {session_id}: {e}")
            return []
            
    def export_session(self, session_id: str) -> Optional[str]:
        """
        Export a session to JSON format.
        
        Args:
            session_id: The ID of the session to export
            
        Returns:
            Optional[str]: JSON string of the session or None if error
        """
        try:
            session = self.get_session(session_id)
            
            if not session:
                logger.warning(f"Attempted to export nonexistent session: {session_id}")
                return None
                
            # Add session ID to the export
            export_data = {
                "session_id": session_id,
                **session
            }
            
            return json.dumps(export_data, indent=2)
            
        except Exception as e:
            logger.error(f"Error exporting session {session_id}: {e}")
            return None
            
    def import_session(self, session_data: Union[str, Dict[str, Any]]) -> Optional[str]:
        """
        Import a session from JSON format.
        
        Args:
            session_data: JSON string or dictionary containing session data
            
        Returns:
            Optional[str]: The session ID or None if error
        """
        try:
            # Parse JSON if string provided
            if isinstance(session_data, str):
                session_data = json.loads(session_data)
                
            # Extract session ID if present, otherwise generate new one
            session_id = session_data.pop("session_id", str(uuid.uuid4()))
            
            # Validate the session data
            if "created_at" not in session_data or "conversation_history" not in session_data:
                logger.warning("Invalid session data format: missing required fields")
                return None
                
            # Update last_active to current time
            session_data["last_active"] = time.time()
            
            # Store the session
            self.sessions[session_id] = session_data
            
            logger.info(f"Imported session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error importing session: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.
        
        Returns:
            int: Number of sessions removed
        """
        try:
            current_time = time.time()
            expired_sessions = []
            
            # Find expired sessions
            for session_id, session in self.sessions.items():
                if current_time - session["last_active"] > self.session_ttl:
                    expired_sessions.append(session_id)
            
            # Remove expired sessions
            for session_id in expired_sessions:
                del self.sessions[session_id]
                
            count = len(expired_sessions)
            if count > 0:
                logger.info(f"Cleaned up {count} expired sessions")
            
            return count
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
