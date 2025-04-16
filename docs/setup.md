# Development Setup Guide

This guide provides instructions for setting up the development environment for the Medical Billing Denial Agent project.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.9 or higher
- pip (Python package manager)
- Git
- Google Cloud SDK (for Vertex AI integration)

## Environment Setup

### 1. Clone the Repository

```bash
git clone --recursive https://github.com/yourusername/medical-billing-denial-agent.git
cd medical-billing-denial-agent
```

### 2. Set Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your specific configuration
# Make sure to set at minimum:
# - GOOGLE_CLOUD_PROJECT
# - GOOGLE_APPLICATION_CREDENTIALS
# - AGENT_MODEL
```

## Google Cloud Setup

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note the Project ID for your `.env` file

### 2. Set Up Service Account Credentials

1. In the Google Cloud Console, go to **IAM & Admin** > **Service Accounts**
2. Create a new service account with the following roles:
   - Vertex AI User
   - Vertex AI Service Agent
3. Create a key for this service account (JSON format)
4. Download the key file and store it securely
5. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable in your `.env` file to the path of this key file

### 3. Enable Required APIs

Enable the following APIs in your Google Cloud project:

- Vertex AI API
- Cloud Storage API
- IAM Service Account Credentials API

## Testing Your Setup

### 1. Run Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

### 2. Run the Development Server

```bash
python run.py
```

The server will start on the port specified in your `.env` file (default: 8080).

## Project Structure Overview

- `agent/`: Core agent implementation
  - `core/`: Main coordinator and session management
  - `classifiers/`: Denial classifier agents
  - `analyzers/`: Document analysis agents
  - `advisors/`: Remediation advisor agents
  - `tools/`: Specialized tools for different agent functions
- `config/`: Configuration and environment settings
- `knowledge_base/`: Knowledge data and integration
- `tests/`: Test suite
  - `unit/`: Unit tests for individual components
  - `integration/`: Integration tests for system functionality
- `docs/`: Documentation files

## Troubleshooting

### Common Issues

#### Environment Variable Problems

If you see errors about missing environment variables:

```
Environment validation failed: Missing required environment variables: GOOGLE_CLOUD_PROJECT, AGENT_MODEL
```

Make sure your `.env` file is properly set up with all required variables.

#### Google Cloud Authentication Issues

If you see authentication errors:

```
Google Cloud authentication failed: Could not find or load credentials
```

Check that:
1. Your service account key file exists at the path specified in `GOOGLE_APPLICATION_CREDENTIALS`
2. The service account has the necessary permissions
3. The APIs are enabled in your Google Cloud project

## Next Steps

After setting up your environment, you can:

1. Explore the ADK documentation in the `ADK_Framework_Documentation` directory
2. Review the project roadmap in `Medical_Billing_Denial_Agent_Roadmap.md`
3. Study the detailed technical plan in `Medical_Billing_Denial_Agent_Project_Plan.md`
