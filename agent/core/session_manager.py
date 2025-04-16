"""
Session Manager Module

This module handles the creation, retrieval, and management of conversation sessions
for the Medical Billing Denial Agent system. It ensures that conversation context
is maintained across interactions and handles secure storage of session data.
"""

import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages conversation sessions for the Medical Billing Denial Agent.
    
    This class provides an interface for creating, retrieving, and updating
    sessions, as well as managing session context and history. It ensures that
    session data is securely stored and properly maintained throughout the
    conversation lifecycle.
    
    Note: This is a simplified implementation that uses an in-memory dictionary.
    In a production environment, this would be replaced with a more robust
    storage solution.
    """
    
    def __init__(self):
        """Initialize the SessionManager with appropriate configuration."""
        logger.info("Initializing SessionManager")
        
        self.session_ttl = int(os.getenv("SESSION_TTL", 3600))  # Default: 1 hour
        self.sessions = {}  # In-memory storage for sessions
        
        logger.info(f"SessionManager initialized with TTL: {self.session_ttl} seconds")
    
    def create_session(self) -> str:
        """
        Create a new session for a conversation.
        
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
        }
        
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
    
    def add_conversation_turn(self, session_id: str, user_input: str, agent_response: str) -> bool:
        """
        Add a conversation turn to the session history.
        
        Args:
            session_id: The ID of the session
            user_input: The user's message
            agent_response: The agent's response
            
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
                
            session["conversation_history"].append({
                "timestamp": time.time(),
                "user_input": user_input,
                "agent_response": agent_response
            })
            
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
