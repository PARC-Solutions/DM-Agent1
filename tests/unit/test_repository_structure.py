"""
Repository Structure Tests

This module contains tests to verify that the repository structure
meets the requirements specified in US 1.1.
"""

import os
import pytest


def test_core_directories_exist():
    """Test that all required core directories exist in the repository."""
    required_directories = [
        "agent",
        "agent/core",
        "agent/classifiers",
        "agent/analyzers",
        "agent/advisors",
        "agent/tools",
        "agent/tools/document_processing",
        "agent/tools/knowledge_access",
        "knowledge_base",
        "tests",
        "tests/unit",
        "tests/integration",
        "docs",
    ]
    
    for directory in required_directories:
        assert os.path.isdir(directory), f"Required directory '{directory}' does not exist"


def test_core_files_exist():
    """Test that all required core files exist in the repository."""
    required_files = [
        "README.md",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "run.py",
        "agent/__init__.py",
        "agent/core/__init__.py",
        "agent/core/coordinator.py",
        "agent/core/session_manager.py",
    ]
    
    for file_path in required_files:
        assert os.path.isfile(file_path), f"Required file '{file_path}' does not exist"


def test_package_init_files_exist():
    """Test that all packages have __init__.py files."""
    packages = [
        "agent",
        "agent/core",
        "agent/classifiers",
        "agent/analyzers",
        "agent/advisors",
        "agent/tools",
        "agent/tools/document_processing",
        "agent/tools/knowledge_access",
    ]
    
    for package in packages:
        init_file = os.path.join(package, "__init__.py")
        assert os.path.isfile(init_file), f"Package '{package}' missing __init__.py file"


def test_environment_file_format():
    """Test that the .env.example file has the correct format."""
    with open(".env.example", "r") as f:
        env_content = f.read()
    
    # Check for required environment variable categories
    required_categories = [
        "Google Cloud Configuration",
        "Agent Configuration",
        "Vertex AI Configuration",
        "Knowledge Base Configuration",
        "Development Settings",
        "Security Settings",
    ]
    
    for category in required_categories:
        assert category in env_content, f"Environment category '{category}' missing from .env.example"
    
    # Check for specific required variables
    required_variables = [
        "GOOGLE_CLOUD_PROJECT",
        "AGENT_MODEL",
        "AGENT_TEMPERATURE",
        "VERTEX_AI_LOCATION",
        "KNOWLEDGE_BASE_INDEX_ID",
        "DEBUG",
        "LOG_LEVEL",
    ]
    
    for variable in required_variables:
        assert f"{variable}=" in env_content, f"Required environment variable '{variable}' missing from .env.example"


def test_readme_content():
    """Test that the README.md file contains required sections."""
    with open("README.md", "r") as f:
        readme_content = f.read()
    
    required_sections = [
        "# Medical Billing Denial Agent",
        "## What's Included",
        "## Getting Started",
        "## System Architecture",
        "## Development",
        "## Compliance and Security",
        "## License",
    ]
    
    for section in required_sections:
        assert section in readme_content, f"Required README section '{section}' is missing"
