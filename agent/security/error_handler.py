"""
Error Handling and Fallback System

This module implements error handling and fallback mechanisms for the Medical Billing Denial
Agent system, ensuring robustness and reliability in exceptional conditions.

Features:
- Standardized error handling
- Error categorization and prioritization
- Recovery procedures
- Graceful degradation
- User-friendly error messages
"""

import logging
import traceback
import time
import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Enumeration of error categories."""
    SYSTEM = "system"
    INPUT = "input"
    PROCESSING = "processing"
    SECURITY = "security"
    NETWORK = "network"
    DATABASE = "database"
    TIMEOUT = "timeout"
    THIRD_PARTY = "third_party"
    UNKNOWN = "unknown"


class ErrorDetails:
    """
    Container for detailed error information.
    
    This class stores structured information about an error,
    including its severity, category, and recovery options.
    """
    
    def __init__(self, 
                error: Exception,
                message: str,
                severity: ErrorSeverity = ErrorSeverity.ERROR,
                category: ErrorCategory = ErrorCategory.UNKNOWN,
                recovery_action: Optional[str] = None,
                context: Optional[Dict[str, Any]] = None):
        """
        Initialize the error details.
        
        Args:
            error: The exception that occurred
            message: Human-readable error message
            severity: Error severity level
            category: Error category
            recovery_action: Optional description of how to recover
            context: Optional context information when the error occurred
        """
        self.error = error
        self.error_type = type(error).__name__
        self.message = message
        self.severity = severity
        self.category = category
        self.recovery_action = recovery_action
        self.context = context or {}
        self.timestamp = time.time()
        self.traceback = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error details to a dictionary."""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "recovery_action": self.recovery_action,
            "context": self.context,
            "timestamp": self.timestamp,
            "traceback": self.traceback
        }
    
    def to_user_message(self) -> str:
        """
        Generate a user-friendly error message.
        
        Returns:
            User-friendly error message
        """
        if self.severity == ErrorSeverity.INFO:
            prefix = "Information"
        elif self.severity == ErrorSeverity.WARNING:
            prefix = "Warning"
        else:
            prefix = "Error"
            
        message = f"{prefix}: {self.message}"
        
        if self.recovery_action:
            message += f"\n\nRecommended action: {self.recovery_action}"
            
        return message


class ErrorHandler:
    """
    Central error handling system.
    
    This class provides centralized error handling, categorization,
    and recovery for the Medical Billing Denial Agent system.
    """
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_log = []
        self.max_log_size = 1000  # Maximum errors to keep in memory
        self.error_counts = {}  # Counter for each error type
        self.error_categorizers = []  # Functions to categorize errors
        self.recovery_handlers = {}  # Handlers for specific error types
        self.global_recovery_handler = None  # Default handler
        
        # Initialize default categorizers
        self._initialize_default_categorizers()
    
    def _initialize_default_categorizers(self):
        """Initialize default error categorizers."""
        # Timeout error categorizer
        def timeout_categorizer(error: Exception) -> Optional[Tuple[ErrorCategory, ErrorSeverity]]:
            """Categorize timeout errors."""
            error_str = str(error).lower()
            if "timeout" in error_str or "timed out" in error_str:
                return ErrorCategory.TIMEOUT, ErrorSeverity.WARNING
            return None
            
        # Security error categorizer
        def security_categorizer(error: Exception) -> Optional[Tuple[ErrorCategory, ErrorSeverity]]:
            """Categorize security errors."""
            error_type = type(error).__name__
            if any(security_term in error_type.lower() 
                  for security_term in ["permission", "access", "auth", "security", "encrypt"]):
                return ErrorCategory.SECURITY, ErrorSeverity.ERROR
            return None
            
        # Input error categorizer
        def input_categorizer(error: Exception) -> Optional[Tuple[ErrorCategory, ErrorSeverity]]:
            """Categorize input errors."""
            error_type = type(error).__name__
            if error_type in ["ValueError", "TypeError", "KeyError", "IndexError"]:
                return ErrorCategory.INPUT, ErrorSeverity.WARNING
            return None
            
        # Add default categorizers
        self.add_error_categorizer(timeout_categorizer)
        self.add_error_categorizer(security_categorizer)
        self.add_error_categorizer(input_categorizer)
    
    def add_error_categorizer(self, categorizer_func: Callable[[Exception], Optional[Tuple[ErrorCategory, ErrorSeverity]]]):
        """
        Add an error categorization function.
        
        Args:
            categorizer_func: Function that takes an error and returns
                            a category and severity, or None if not applicable
        """
        self.error_categorizers.append(categorizer_func)
    
    def register_recovery_handler(self, error_type: str, handler_func: Callable):
        """
        Register a recovery handler for a specific error type.
        
        Args:
            error_type: Error type name to handle
            handler_func: Function to call for recovery
        """
        self.recovery_handlers[error_type] = handler_func
    
    def set_global_recovery_handler(self, handler_func: Callable):
        """
        Set the global recovery handler.
        
        Args:
            handler_func: Function to call for recovery
        """
        self.global_recovery_handler = handler_func
    
    def _categorize_error(self, error: Exception) -> Tuple[ErrorCategory, ErrorSeverity]:
        """
        Categorize an error.
        
        Args:
            error: The exception to categorize
            
        Returns:
            Tuple of category and severity
        """
        # Try each categorizer
        for categorizer in self.error_categorizers:
            result = categorizer(error)
            if result is not None:
                return result
                
        # Default categorization
        error_type = type(error).__name__
        
        # System errors
        if any(sys_err in error_type for sys_err in ["System", "OS", "IO", "FileNotFound"]):
            return ErrorCategory.SYSTEM, ErrorSeverity.ERROR
            
        # Network errors
        if any(net_err in error_type for net_err in ["Connection", "Socket", "Http", "URL"]):
            return ErrorCategory.NETWORK, ErrorSeverity.WARNING
            
        # Database errors
        if any(db_err in error_type for db_err in ["DB", "SQL", "Data", "Query"]):
            return ErrorCategory.DATABASE, ErrorSeverity.ERROR
            
        # Default unknown
        return ErrorCategory.UNKNOWN, ErrorSeverity.ERROR
    
    def handle_error(self, error: Exception, message: str = None, 
                   context: Dict[str, Any] = None) -> ErrorDetails:
        """
        Handle an error.
        
        Args:
            error: The exception to handle
            message: Optional custom error message
            context: Optional context information
            
        Returns:
            ErrorDetails containing information about the handled error
        """
        # Determine category and severity
        category, severity = self._categorize_error(error)
        
        # Create error message if not provided
        if message is None:
            message = str(error)
            
        # Determine recovery action based on error type
        recovery_action = None
        error_type = type(error).__name__
        
        # Track error counts
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Create error details
        error_details = ErrorDetails(
            error=error,
            message=message,
            severity=severity,
            category=category,
            recovery_action=recovery_action,
            context=context
        )
        
        # Log the error
        self._log_error(error_details)
        
        # Try to find a recovery handler
        recovery_handler = self.recovery_handlers.get(error_type, self.global_recovery_handler)
        if recovery_handler:
            try:
                recovery_result = recovery_handler(error, error_details)
                error_details.recovery_result = recovery_result
            except Exception as recovery_error:
                logger.error(f"Error in recovery handler: {recovery_error}")
        
        return error_details
    
    def _log_error(self, error_details: ErrorDetails):
        """
        Log an error.
        
        Args:
            error_details: Details of the error to log
        """
        # Add to in-memory log
        self.error_log.append(error_details)
        
        # Trim log if needed
        if len(self.error_log) > self.max_log_size:
            self.error_log = self.error_log[-self.max_log_size:]
            
        # Log to logger based on severity
        log_message = f"{error_details.category.value}: {error_details.message}"
        
        if error_details.severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif error_details.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif error_details.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif error_details.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
    
    def get_error_log(self, category: Optional[ErrorCategory] = None,
                    severity: Optional[ErrorSeverity] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the error log with optional filtering.
        
        Args:
            category: Optional category to filter by
            severity: Optional severity to filter by
            limit: Maximum number of errors to return
            
        Returns:
            List of error details dictionaries
        """
        filtered_log = self.error_log
        
        # Apply category filter
        if category is not None:
            filtered_log = [err for err in filtered_log if err.category == category]
            
        # Apply severity filter
        if severity is not None:
            filtered_log = [err for err in filtered_log if err.severity == severity]
            
        # Sort by timestamp (newest first)
        sorted_log = sorted(filtered_log, key=lambda err: err.timestamp, reverse=True)
        
        # Convert to dictionaries and apply limit
        return [err.to_dict() for err in sorted_log[:limit]]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get statistics about errors.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            "total_errors": len(self.error_log),
            "error_counts_by_type": self.error_counts,
            "error_counts_by_category": {
                category.value: sum(1 for err in self.error_log if err.category == category)
                for category in ErrorCategory
            },
            "error_counts_by_severity": {
                severity.value: sum(1 for err in self.error_log if err.severity == severity)
                for severity in ErrorSeverity
            }
        }


class FallbackSystem:
    """
    System for providing fallback functionality.
    
    This class provides mechanisms for graceful degradation and
    fallback to simpler alternatives when errors occur.
    """
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """
        Initialize the fallback system.
        
        Args:
            error_handler: Optional error handler to integrate with
        """
        self.error_handler = error_handler
        self.fallback_handlers = {}
        self.default_fallback_message = (
            "I apologize, but I'm currently experiencing difficulty processing your request. "
            "Let's try a different approach."
        )
    
    def register_fallback(self, component_name: str, fallback_func: Callable):
        """
        Register a fallback handler for a component.
        
        Args:
            component_name: Name of the component
            fallback_func: Function to call for fallback
        """
        self.fallback_handlers[component_name] = fallback_func
    
    def safe_execute(self, func: Callable, *args, component_name: str = None, 
                   fallback_args: Any = None, **kwargs) -> Tuple[Any, Optional[ErrorDetails]]:
        """
        Safely execute a function with fallback.
        
        Args:
            func: Function to execute
            component_name: Optional component name for specific fallback
            fallback_args: Optional arguments for fallback
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Tuple of (result, error_details) where error_details is None if no error
        """
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as error:
            # Handle the error
            if self.error_handler:
                context = {
                    "component": component_name,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                error_details = self.error_handler.handle_error(
                    error=error,
                    context=context
                )
            else:
                # Create minimal error details if no handler
                error_details = ErrorDetails(
                    error=error,
                    message=str(error),
                    category=ErrorCategory.UNKNOWN,
                    severity=ErrorSeverity.ERROR,
                    context={"component": component_name}
                )
            
            # Try component-specific fallback
            if component_name and component_name in self.fallback_handlers:
                fallback_func = self.fallback_handlers[component_name]
                try:
                    fallback_result = fallback_func(
                        error, fallback_args if fallback_args is not None else args
                    )
                    return fallback_result, error_details
                except Exception as fallback_error:
                    logger.error(f"Error in fallback handler: {fallback_error}")
            
            # Return default fallback
            return self._default_fallback(component_name), error_details
    
    def _default_fallback(self, component_name: str = None) -> Dict[str, Any]:
        """
        Default fallback when no specific fallback is available.
        
        Args:
            component_name: Optional component name that failed
            
        Returns:
            Default fallback result
        """
        return {
            "success": False,
            "fallback": True,
            "message": self.default_fallback_message,
            "component": component_name
        }
    
    def set_default_fallback_message(self, message: str):
        """
        Set the default fallback message.
        
        Args:
            message: New default message
        """
        self.default_fallback_message = message


# Create singleton instances
default_error_handler = ErrorHandler()
default_fallback_system = FallbackSystem(error_handler=default_error_handler)


def safe_execution_decorator(component_name: str = None):
    """
    Decorator for safe function execution with fallback.
    
    Args:
        component_name: Name of the component
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result, error = default_fallback_system.safe_execute(
                func, *args, component_name=component_name, **kwargs
            )
            return result
        return wrapper
    return decorator
