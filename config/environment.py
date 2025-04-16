"""
Environment Configuration

This module handles environment variable loading and validation,
ensuring that all required configuration is present before the
application starts.
"""

import os
import logging
from typing import Dict, List, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_environment():
    """
    Load environment variables from .env file.
    
    Returns:
        bool: True if environment was loaded successfully
    """
    # Load environment variables from .env file
    load_dotenv()
    logger.info("Environment variables loaded")
    return True


def validate_environment(required_vars: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Validate that required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
                      If None, uses default required variables
    
    Returns:
        Dict[str, str]: Dictionary of validated environment variables
        
    Raises:
        ValueError: If any required variables are missing
    """
    if required_vars is None:
        required_vars = [
            "GOOGLE_CLOUD_PROJECT",
            "AGENT_MODEL",
            "AGENT_TEMPERATURE",
            "VERTEX_AI_LOCATION",
        ]
    
    missing_vars = []
    env_vars = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if value is None or value.strip() == "":
            missing_vars.append(var)
        else:
            env_vars[var] = value
    
    if missing_vars:
        missing_str = ", ".join(missing_vars)
        logger.error(f"Missing required environment variables: {missing_str}")
        raise ValueError(f"Missing required environment variables: {missing_str}")
    
    logger.info(f"Environment validated: {len(env_vars)} variables loaded")
    return env_vars


def get_env(var_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable with an optional default value.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if the variable is not set
        
    Returns:
        Optional[str]: Value of the environment variable or default
    """
    return os.getenv(var_name, default)


def check_google_cloud_setup() -> bool:
    """
    Check if Google Cloud is properly configured.
    
    Returns:
        bool: True if Google Cloud is configured, False otherwise
    """
    # Check for Google Cloud project
    project_id = get_env("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set")
        return False
    
    # Check for credentials
    credentials_path = get_env("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        return False
    
    # Check if credentials file exists
    if not os.path.isfile(credentials_path):
        logger.warning(f"Credentials file not found: {credentials_path}")
        return False
    
    logger.info(f"Google Cloud configured with project: {project_id}")
    return True
