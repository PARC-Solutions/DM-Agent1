#!/usr/bin/env python3
"""
Vertex AI Deployment Script

This script deploys the Medical Billing Denial Agent to Google Vertex AI.
It handles configuration, authentication, and the deployment process.
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Google Cloud imports
try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import utils
except ImportError:
    print("Google Cloud AI Platform libraries not found.")
    print("Install them with: pip install google-cloud-aiplatform")
    sys.exit(1)

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from deployment.vertex_ai.deploy_config import (
    load_deployment_config,
    DeploymentEnvironment,
    get_deployment_labels,
    VertexAIDeploymentConfig
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def validate_environment() -> None:
    """
    Validate that the environment is properly configured for deployment.
    
    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = ["GOOGLE_CLOUD_PROJECT", "GOOGLE_APPLICATION_CREDENTIALS"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set these variables before deployment."
        )
    
    # Validate credentials file exists
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path and not os.path.exists(credentials_path):
        raise ValueError(
            f"Credentials file not found at: {credentials_path}\n"
            f"Please check the GOOGLE_APPLICATION_CREDENTIALS path."
        )


def initialize_vertex_ai(config: VertexAIDeploymentConfig) -> None:
    """
    Initialize the Vertex AI client with the deployment configuration.
    
    Args:
        config: The deployment configuration
    """
    logger.info(f"Initializing Vertex AI client in {config.location}")
    aiplatform.init(
        project=config.project_id,
        location=config.location,
    )


def create_agent_config(
    config: VertexAIDeploymentConfig,
    agent_module_path: str,
    agent_class_name: str,
) -> Dict[str, Any]:
    """
    Create the configuration dictionary for Vertex AI agent deployment.
    
    Args:
        config: The deployment configuration
        agent_module_path: The module path to the agent class
        agent_class_name: The name of the agent class to deploy
        
    Returns:
        Dict[str, Any]: The agent configuration dictionary
    """
    # Set base directory (repository root)
    base_dir = Path(__file__).parent.parent.parent
    
    # Create the agent configuration
    agent_config = {
        "display_name": config.display_name,
        "machine_type": config.machine_type.value,
        "min_replica_count": config.min_replica_count,
        "max_replica_count": config.max_replica_count,
        "agent_module_path": agent_module_path,
        "agent_class_name": agent_class_name,
        "environment_variables": config.environment_variables,
        "labels": get_deployment_labels(),
    }
    
    # Add security configuration
    if config.encryption_spec_key_name:
        agent_config["encryption_spec_key_name"] = config.encryption_spec_key_name
    
    if config.service_account:
        agent_config["service_account"] = config.service_account
    
    if config.network:
        agent_config["network"] = config.network
    
    return agent_config


def deploy_agent(
    config: VertexAIDeploymentConfig,
    agent_module_path: str,
    agent_class_name: str,
    staging_bucket: Optional[str] = None,
    update_if_exists: bool = False,
) -> str:
    """
    Deploy the agent to Vertex AI.
    
    Args:
        config: The deployment configuration
        agent_module_path: The module path to the agent class
        agent_class_name: The name of the agent class to deploy
        staging_bucket: Optional GCS bucket for staging deployment files
        update_if_exists: Whether to update the agent if it already exists
        
    Returns:
        str: The deployed agent endpoint
    """
    # Initialize Vertex AI
    initialize_vertex_ai(config)
    
    # Create agent configuration
    agent_config = create_agent_config(
        config, agent_module_path, agent_class_name
    )
    
    # Log deployment information
    logger.info(f"Deploying agent: {config.display_name}")
    logger.info(f"Environment: {config.environment.value}")
    logger.info(f"Machine type: {config.machine_type.value}")
    logger.info(f"Replicas: {config.min_replica_count} - {config.max_replica_count}")
    
    # Check if agent already exists
    existing_endpoints = aiplatform.Endpoint.list(
        filter=f'display_name="{config.display_name}"'
    )
    
    if existing_endpoints and not update_if_exists:
        raise ValueError(
            f"Agent with name '{config.display_name}' already exists. "
            f"Use --update flag to update the existing agent."
        )
    
    # Deploy the agent
    try:
        from google.adk.deployment import deploy_to_vertex
        
        # Import the agent class
        sys.path.append(str(Path(__file__).parent.parent.parent))
        module = __import__(agent_module_path, fromlist=[agent_class_name])
        agent_class = getattr(module, agent_class_name)
        agent = agent_class()
        
        # Deploy to Vertex
        endpoint = deploy_to_vertex(
            agent=agent,
            project_id=config.project_id,
            location=config.location,
            staging_bucket=staging_bucket,
            machine_type=config.machine_type.value,
            min_replica_count=config.min_replica_count,
            max_replica_count=config.max_replica_count,
            encryption_spec_key_name=config.encryption_spec_key_name,
            service_account=config.service_account,
            network=config.network,
            labels=get_deployment_labels()
        )
        
        logger.info(f"Agent successfully deployed to: {endpoint.resource_name}")
        return endpoint.resource_name
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise


def setup_arguments() -> argparse.Namespace:
    """
    Set up command-line arguments for the deployment script.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Deploy Medical Billing Denial Agent to Vertex AI")
    
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default="staging",
        help="Deployment environment"
    )
    
    parser.add_argument(
        "--agent-module",
        default="agent.core.coordinator",
        help="Module path to the agent class"
    )
    
    parser.add_argument(
        "--agent-class",
        default="MedicalBillingDenialCoordinator",
        help="Name of the agent class to deploy"
    )
    
    parser.add_argument(
        "--project-id",
        help="Google Cloud project ID (overrides GOOGLE_CLOUD_PROJECT)"
    )
    
    parser.add_argument(
        "--location",
        default="us-central1",
        help="Google Cloud region for deployment"
    )
    
    parser.add_argument(
        "--machine-type",
        default="e2-standard-4",
        help="Machine type for deployment"
    )
    
    parser.add_argument(
        "--min-replicas",
        type=int,
        default=1,
        help="Minimum number of replicas"
    )
    
    parser.add_argument(
        "--max-replicas",
        type=int,
        default=3,
        help="Maximum number of replicas"
    )
    
    parser.add_argument(
        "--staging-bucket",
        help="GCS bucket for staging deployment files"
    )
    
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update the agent if it already exists"
    )
    
    parser.add_argument(
        "--service-account",
        help="Custom service account for the deployment"
    )
    
    parser.add_argument(
        "--network",
        help="VPC network for deployment"
    )
    
    parser.add_argument(
        "--encryption-key",
        help="KMS encryption key (required for HIPAA compliance in production)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the deployment script."""
    # Parse command-line arguments
    args = setup_arguments()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Set environment variables from arguments
    if args.environment:
        os.environ["DEPLOYMENT_ENVIRONMENT"] = args.environment
    
    if args.project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = args.project_id
    
    if args.location:
        os.environ["VERTEX_AI_LOCATION"] = args.location
    
    if args.machine_type:
        os.environ["VERTEX_AI_MACHINE_TYPE"] = args.machine_type
    
    if args.min_replicas:
        os.environ["MIN_REPLICA_COUNT"] = str(args.min_replicas)
    
    if args.max_replicas:
        os.environ["MAX_REPLICA_COUNT"] = str(args.max_replicas)
    
    if args.encryption_key:
        os.environ["ENCRYPTION_KEY_NAME"] = args.encryption_key
    
    if args.service_account:
        os.environ["SERVICE_ACCOUNT"] = args.service_account
    
    if args.network:
        os.environ["NETWORK"] = args.network
    
    try:
        # Validate environment
        validate_environment()
        
        # Load deployment configuration
        config = load_deployment_config()
        
        # Deploy the agent
        deploy_agent(
            config=config,
            agent_module_path=args.agent_module,
            agent_class_name=args.agent_class,
            staging_bucket=args.staging_bucket,
            update_if_exists=args.update
        )
        
        logger.info("Deployment completed successfully")
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
