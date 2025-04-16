"""
Vertex AI Deployment Configuration

This module provides configuration settings and utility functions for deploying
the Medical Billing Denial Agent to Vertex AI.
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional, List, Union
from enum import Enum


class DeploymentEnvironment(Enum):
    """Supported deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class MachineType(Enum):
    """Available machine types for Vertex AI deployment."""
    E2_STANDARD_2 = "e2-standard-2"  # 2 vCPUs, 8 GB memory
    E2_STANDARD_4 = "e2-standard-4"  # 4 vCPUs, 16 GB memory
    E2_STANDARD_8 = "e2-standard-8"  # 8 vCPUs, 32 GB memory
    E2_HIGHCPU_4 = "e2-highcpu-4"    # 4 vCPUs, 4 GB memory
    E2_HIGHMEM_2 = "e2-highmem-2"    # 2 vCPUs, 16 GB memory
    
    @classmethod
    def get_default(cls) -> 'MachineType':
        """Return the default machine type based on project plan."""
        return cls.E2_STANDARD_4


@dataclass
class VertexAIDeploymentConfig:
    """Configuration settings for Vertex AI deployment."""
    # Core configuration
    project_id: str
    location: str = "us-central1"
    environment: DeploymentEnvironment = DeploymentEnvironment.STAGING
    display_name: str = "medical-billing-denial-agent"
    
    # Resource configuration
    machine_type: MachineType = MachineType.get_default()
    min_replica_count: int = 1
    max_replica_count: int = 3
    autoscaling_target_cpu_utilization: int = 70
    
    # Security configuration
    encryption_spec_key_name: Optional[str] = None
    service_account: Optional[str] = None
    network: Optional[str] = None
    
    # Application-specific configuration
    environment_variables: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize defaults for mutable fields."""
        if self.environment_variables is None:
            self.environment_variables = {}
            
        # Set up default encryption key for HIPAA compliance in production
        if self.environment == DeploymentEnvironment.PRODUCTION and not self.encryption_spec_key_name:
            self.encryption_spec_key_name = (
                f"projects/{self.project_id}/locations/{self.location}/keyRings/"
                f"hipaa-keyring/cryptoKeys/data-encryption-key"
            )
            

def load_deployment_config() -> VertexAIDeploymentConfig:
    """
    Load deployment configuration from environment variables.
    
    Returns:
        VertexAIDeploymentConfig: The deployment configuration
    """
    # Required configuration
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set")
    
    # Optional configuration with defaults
    location = os.environ.get("VERTEX_AI_LOCATION", "us-central1")
    env_name = os.environ.get("DEPLOYMENT_ENVIRONMENT", "staging")
    environment = DeploymentEnvironment(env_name)
    
    # Resource configuration
    machine_type_name = os.environ.get("VERTEX_AI_MACHINE_TYPE", "e2-standard-4")
    machine_type = MachineType(machine_type_name)
    min_replicas = int(os.environ.get("MIN_REPLICA_COUNT", "1"))
    max_replicas = int(os.environ.get("MAX_REPLICA_COUNT", "3"))
    cpu_target = int(os.environ.get("CPU_UTILIZATION_TARGET", "70"))
    
    # Security configuration
    encryption_key = os.environ.get("ENCRYPTION_KEY_NAME")
    service_account = os.environ.get("SERVICE_ACCOUNT")
    network = os.environ.get("NETWORK")
    
    # Environment variables to pass to the deployment
    env_vars = {}
    for key, value in os.environ.items():
        if key.startswith("AGENT_"):
            env_vars[key] = value
    
    return VertexAIDeploymentConfig(
        project_id=project_id,
        location=location,
        environment=environment,
        display_name=f"medical-billing-denial-agent-{env_name}",
        machine_type=machine_type,
        min_replica_count=min_replicas,
        max_replica_count=max_replicas,
        autoscaling_target_cpu_utilization=cpu_target,
        encryption_spec_key_name=encryption_key,
        service_account=service_account,
        network=network,
        environment_variables=env_vars
    )


def get_deployment_labels() -> Dict[str, str]:
    """
    Get default labels to apply to the deployment.
    
    Returns:
        Dict[str, str]: Dictionary of labels
    """
    return {
        "app": "medical-billing-denial-agent",
        "environment": os.environ.get("DEPLOYMENT_ENVIRONMENT", "staging"),
        "version": os.environ.get("APP_VERSION", "1.0.0"),
        "managed-by": "adk-deployment"
    }
