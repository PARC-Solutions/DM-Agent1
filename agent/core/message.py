"""
Agent Message System

This module implements the standardized message format and handlers for inter-agent communication
in the Medical Billing Denial Agent system. It provides a structured way for agents to exchange
information, maintain context, and trace message flow through the system.

Features:
- Standardized message structure
- Message validation
- Context management
- Message tracing and logging
"""

import uuid
import time
import logging
import json
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    """Enum representing the priority of a message."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageType(Enum):
    """Enum representing the type of message being sent."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


@dataclass
class AgentMessage:
    """
    Standard message format for inter-agent communication.
    
    This class provides a structured format for messages exchanged between agents,
    including sender/recipient information, message content, and metadata for tracing.
    """
    # Required fields
    sender: str
    recipient: str
    content: Dict[str, Any]
    
    # Optional fields with defaults
    message_type: MessageType = field(default=MessageType.REQUEST)
    priority: MessagePriority = field(default=MessagePriority.NORMAL)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate message after initialization."""
        if isinstance(self.message_type, str):
            self.message_type = MessageType(self.message_type)
        
        if isinstance(self.priority, str):
            self.priority = MessagePriority(self.priority)
            
        # If no correlation ID is provided, use the message ID as the correlation ID
        if not self.correlation_id:
            self.correlation_id = self.message_id
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        message_dict = asdict(self)
        
        # Convert enums to string values
        message_dict["message_type"] = self.message_type.value
        message_dict["priority"] = self.priority.value
        
        return message_dict
    
    def to_json(self) -> str:
        """Convert the message to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create a message from a dictionary."""
        # Ensure enum values are properly handled
        if "message_type" in data and not isinstance(data["message_type"], MessageType):
            data["message_type"] = MessageType(data["message_type"])
            
        if "priority" in data and not isinstance(data["priority"], MessagePriority):
            data["priority"] = MessagePriority(data["priority"])
            
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_string: str) -> 'AgentMessage':
        """Create a message from a JSON string."""
        data = json.loads(json_string)
        return cls.from_dict(data)
    
    def create_response(self, content: Dict[str, Any], 
                        metadata: Optional[Dict[str, Any]] = None) -> 'AgentMessage':
        """
        Create a response message to this message.
        
        Args:
            content: The content of the response
            metadata: Optional additional metadata for the response
            
        Returns:
            A new AgentMessage configured as a response to this message
        """
        response_metadata = self.metadata.copy()
        if metadata:
            response_metadata.update(metadata)
            
        return AgentMessage(
            sender=self.recipient,
            recipient=self.sender,
            content=content,
            message_type=MessageType.RESPONSE,
            priority=self.priority,
            correlation_id=self.message_id,
            metadata=response_metadata
        )


class MessageBus:
    """
    Message routing system for inter-agent communication.
    
    This class handles the routing of messages between agents, provides tracing
    capabilities, and logs message flow through the system.
    """
    
    def __init__(self):
        """Initialize the message bus."""
        self.handlers = {}
        self.interceptors = []
        self.message_log = []
        self.max_log_size = 1000  # Maximum number of messages to keep in memory
        
    def register_handler(self, agent_name: str, handler_func):
        """
        Register a message handler for an agent.
        
        Args:
            agent_name: The name of the agent
            handler_func: The function to call when a message is sent to this agent
        """
        self.handlers[agent_name] = handler_func
        logger.info(f"Registered handler for agent: {agent_name}")
        
    def add_interceptor(self, interceptor_func):
        """
        Add a message interceptor that will be called for all messages.
        
        Interceptors can modify messages, log them, or prevent delivery.
        
        Args:
            interceptor_func: A function that takes a message and returns a 
                             modified message or None to block delivery
        """
        self.interceptors.append(interceptor_func)
        logger.info(f"Added message interceptor: {interceptor_func.__name__}")
        
    def _log_message(self, message: AgentMessage, direction: str):
        """
        Log a message for tracing and debugging.
        
        Args:
            message: The message to log
            direction: 'sent' or 'received'
        """
        log_entry = {
            "timestamp": time.time(),
            "direction": direction,
            "message": message.to_dict()
        }
        
        self.message_log.append(log_entry)
        
        # Trim the log if it exceeds the maximum size
        if len(self.message_log) > self.max_log_size:
            self.message_log = self.message_log[-self.max_log_size:]
            
        # Log the message
        logger.debug(f"Message {direction}: {message.message_id} from {message.sender} to {message.recipient}")
        
    def send(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Send a message to its recipient.
        
        Args:
            message: The message to send
            
        Returns:
            The response message if one is generated, otherwise None
        """
        # Apply interceptors
        for interceptor in self.interceptors:
            message = interceptor(message)
            if message is None:
                logger.warning("Message blocked by interceptor")
                return None
        
        # Log the outgoing message
        self._log_message(message, "sent")
        
        # Check if we have a handler for the recipient
        if message.recipient in self.handlers:
            handler = self.handlers[message.recipient]
            
            try:
                # Call the handler with the message
                response = handler(message)
                
                # If a response was returned, log it
                if response:
                    self._log_message(response, "received")
                    
                return response
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                
                # Create an error response
                error_content = {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                error_message = AgentMessage(
                    sender=message.recipient,
                    recipient=message.sender,
                    content=error_content,
                    message_type=MessageType.ERROR,
                    correlation_id=message.message_id
                )
                
                self._log_message(error_message, "sent")
                return error_message
        else:
            logger.warning(f"No handler registered for recipient: {message.recipient}")
            return None
            
    def get_message_history(self, 
                            correlation_id: Optional[str] = None,
                            start_time: Optional[float] = None,
                            end_time: Optional[float] = None,
                            agent_name: Optional[str] = None) -> List[Dict]:
        """
        Get the message history with optional filtering.
        
        Args:
            correlation_id: Filter by correlation ID
            start_time: Filter by start time
            end_time: Filter by end time
            agent_name: Filter by agent name (sender or recipient)
            
        Returns:
            A list of message log entries matching the filters
        """
        filtered_log = self.message_log
        
        # Apply filters
        if correlation_id:
            filtered_log = [
                entry for entry in filtered_log 
                if entry["message"].get("correlation_id") == correlation_id
            ]
            
        if start_time:
            filtered_log = [
                entry for entry in filtered_log 
                if entry["timestamp"] >= start_time
            ]
            
        if end_time:
            filtered_log = [
                entry for entry in filtered_log 
                if entry["timestamp"] <= end_time
            ]
            
        if agent_name:
            filtered_log = [
                entry for entry in filtered_log 
                if (entry["message"].get("sender") == agent_name or 
                    entry["message"].get("recipient") == agent_name)
            ]
            
        return filtered_log


# Global message bus instance
message_bus = MessageBus()
