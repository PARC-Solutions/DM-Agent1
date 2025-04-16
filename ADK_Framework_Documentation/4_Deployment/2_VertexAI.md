# Deploying to Vertex AI Agent Engine

[Agent Engine](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-engine/agent-engine-introduction) is a fully managed service on Google Cloud specifically designed for deploying, managing, and scaling AI agents built with frameworks such as ADK. This document guides you through the process of deploying your ADK agent to Vertex AI Agent Engine.

## Benefits of Agent Engine

- **Fully managed infrastructure**: No need to worry about server provisioning or scaling
- **Auto-scaling**: Automatically handles traffic spikes
- **Monitoring and analytics**: Built-in monitoring and logging
- **Authentication and security**: Integrated with Google Cloud's security features
- **Enterprise-grade reliability**: Built on Google Cloud's infrastructure

## Prerequisites

Before deploying your agent to Agent Engine, ensure you have:

1. **Google Cloud Project**: An active Google Cloud project with billing enabled
2. **Required APIs**: Vertex AI and Agent Engine APIs enabled
3. **Authentication**: Proper authentication set up for Google Cloud
4. **ADK Agent**: A functional ADK agent ready for deployment

### Setting Up Your Google Cloud Project

If you haven't already set up your Google Cloud environment:

```bash
# Install Google Cloud SDK if not already installed
curl https://sdk.cloud.google.com | bash
gcloud init

# Select or create a project
gcloud projects create [PROJECT_ID] --name="[PROJECT_NAME]"  # Optional: create new project
gcloud config set project [PROJECT_ID]

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
```

## Preparing Your Agent for Deployment

To deploy your ADK agent to Agent Engine, you need to package it properly:

### 1. Structure Your Project

Organize your project with a clear structure:

```
your-agent-project/
├── agent/
│   ├── __init__.py
│   ├── agent.py        # Contains your agent definition
│   └── tools.py        # Custom tools for your agent
├── requirements.txt    # Dependencies
├── setup.py            # Package configuration
└── README.md
```

### 2. Define Your Requirements

Create a `requirements.txt` file with your dependencies:

```
google-adk>=0.1.0
google-cloud-aiplatform>=1.25.0
# Any other dependencies your agent needs
```

### 3. Create a Setup File

Create a `setup.py` file to make your agent installable:

```python
from setuptools import setup, find_packages

setup(
    name="your-agent-package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-adk>=0.1.0",
        "google-cloud-aiplatform>=1.25.0",
        # Other dependencies
    ],
)
```

### 4. Prepare Your Agent

Ensure your agent is defined in a way that Agent Engine can use it:

```python
# agent/agent.py
from google.adk.agents import Agent
from .tools import get_weather, get_news  # Your custom tools

# Create your agent
my_agent = Agent(
    name="my_deployed_agent",
    model="gemini-2.0-flash",
    description="A helpful agent that can check weather and news",
    tools=[get_weather, get_news]
)

# Important: Export the agent as a variable that Agent Engine can import
agent_for_deployment = my_agent
```

## Deploying to Agent Engine

There are two main ways to deploy your agent to Agent Engine:

1. Using the Google Cloud Console (web interface)
2. Using the Google Cloud SDK (command line)

### Deployment with Google Cloud Console

1. **Package your agent**: First, create a distribution package:

```bash
# Create a wheel distribution
pip install build
python -m build
```

2. **Upload to Google Cloud Console**:
   - Navigate to [Vertex AI → Agent Engine](https://console.cloud.google.com/vertex-ai/agent-engine) in the Google Cloud Console
   - Click "Create Agent"
   - Follow the wizard to upload your agent package and configure deployment settings

### Deployment with Google Cloud SDK

You can automate deployment using the `gcloud` command line:

```bash
# Deploy your agent to Agent Engine
gcloud beta ai agents create \
  --region=us-central1 \
  --display-name="My Deployed Agent" \
  --agent-artifact-uri=gs://your-bucket/agent-package.whl \
  --agent-metadata=agent_module=agent.agent,agent_variable=agent_for_deployment
```

### Configuring Deployment Settings

When deploying, you'll need to specify several parameters:

- **Display Name**: A human-readable name for your agent
- **Description**: Optional description of what your agent does
- **Region**: The Google Cloud region to deploy to (e.g., `us-central1`)
- **Artifact URI**: The location of your agent package (GCS path)
- **Agent Module**: The Python module path to your agent (e.g., `agent.agent`)
- **Agent Variable**: The variable name that references your agent (e.g., `agent_for_deployment`)

### Setting Environment Variables

To provide configuration and secrets to your deployed agent:

```bash
# Add environment variables during deployment
gcloud beta ai agents create \
  --region=us-central1 \
  --display-name="My Deployed Agent" \
  --agent-artifact-uri=gs://your-bucket/agent-package.whl \
  --agent-metadata=agent_module=agent.agent,agent_variable=agent_for_deployment \
  --env-vars=API_KEY=your-api-key,ENVIRONMENT=production
```

For sensitive values, use Google Cloud Secret Manager:

```bash
# First, create a secret
gcloud secrets create api-key --data-file=./api-key.txt

# Reference the secret in your deployment
gcloud beta ai agents create \
  --region=us-central1 \
  --display-name="My Deployed Agent" \
  --agent-artifact-uri=gs://your-bucket/agent-package.whl \
  --agent-metadata=agent_module=agent.agent,agent_variable=agent_for_deployment \
  --env-vars=ENVIRONMENT=production \
  --secret-env-vars=API_KEY=projects/your-project/secrets/api-key/versions/latest
```

## Making Your Agent Publicly Accessible

By default, your deployed agent is only accessible within Google Cloud. To make it publicly accessible:

1. **Create an endpoint**:
```bash
gcloud beta ai agent-endpoints create \
  --region=us-central1 \
  --display-name="Public Endpoint" \
  --agent=your-agent-id
```

2. **Configure public access**:
```bash
gcloud beta ai agent-endpoints update your-endpoint-id \
  --region=us-central1 \
  --public-endpoint-enabled
```

## Interacting with Your Deployed Agent

Once deployed, you can interact with your agent through:

### REST API

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/agentEndpoints/YOUR_ENDPOINT_ID:generateAgentResponse \
  -d '{
    "message": "What's the weather in New York?",
    "sessionId": "user-session-123"
  }'
```

### Client Libraries

```python
from google.cloud import aiplatform

# Initialize the Agent Engine client
aiplatform.init(project="your-project-id", location="us-central1")

# Get your deployed agent endpoint
endpoint = aiplatform.AgentEndpoint("your-endpoint-id")

# Send a message to your agent
response = endpoint.generate_agent_response(
    message="What's the weather in New York?",
    session_id="user-session-123"
)

print(response.text)
```

## Monitoring Your Deployed Agent

Monitor your agent's performance and usage through the Google Cloud Console:

1. **Dashboard**: View overall usage metrics
2. **Logs**: Check detailed logs for debugging
3. **Monitoring**: Set up alerts for performance or error thresholds

### Setting Up Logging

Ensure your agent uses proper logging to capture information in Google Cloud:

```python
import logging

def get_weather(location: str) -> dict:
    """Get weather for a location."""
    logging.info(f"Weather requested for: {location}")
    try:
        # Implementation...
        return {"status": "success", "data": weather_data}
    except Exception as e:
        logging.error(f"Weather API error: {str(e)}")
        return {"status": "error", "message": str(e)}
```

## Updating Your Deployed Agent

To update your agent after deployment:

```bash
# Update an existing agent
gcloud beta ai agents update your-agent-id \
  --region=us-central1 \
  --agent-artifact-uri=gs://your-bucket/updated-agent-package.whl
```

## Advanced Configuration

### Scaling Configuration

Customize scaling behavior:

```bash
gcloud beta ai agents update your-agent-id \
  --region=us-central1 \
  --min-replica-count=1 \
  --max-replica-count=10
```

### Custom Container Deployment

For advanced customization, deploy using a custom container:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PORT 8080
CMD ["python", "app.py"]
```

Then deploy using the container:

```bash
# Build and push your container
gcloud builds submit --tag gcr.io/your-project/your-agent:latest

# Deploy using the container
gcloud beta ai agents create \
  --region=us-central1 \
  --display-name="Custom Container Agent" \
  --container-image-uri=gcr.io/your-project/your-agent:latest
```

## Troubleshooting

### Common Deployment Issues

1. **Missing dependencies**: Ensure all dependencies are listed in your `requirements.txt`
2. **Import errors**: Check that your module paths are correct
3. **Authentication issues**: Verify your service account has the necessary permissions
4. **Memory limits**: If your agent requires more memory, adjust the resources in deployment

### Debugging with Logs

To view logs for your deployed agent:

```bash
gcloud logging read "resource.type=aiplatform.googleapis.com/AgentEndpoint AND resource.labels.agent_id=your-agent-id" --limit=10
```

## Cost Management

Monitor and manage costs associated with your deployed agent:

1. **Resource utilization**: Monitor CPU, memory, and request usage
2. **Scaling settings**: Adjust min/max replicas based on usage patterns
3. **Budget alerts**: Set up budget alerts in Google Cloud to monitor spending

## Best Practices

1. **Version your deployments**: Keep track of different versions of your agent
2. **Use staging environments**: Test in a staging environment before production
3. **Implement monitoring**: Set up monitoring for key metrics
4. **Configure appropriate timeouts**: Set request timeout values based on your agent's processing needs
5. **Secure credentials**: Always use Secret Manager for sensitive credentials
6. **Document your deployment**: Keep documentation of your deployment configuration

## Conclusion

Deploying your ADK agent to Vertex AI Agent Engine provides a robust, scalable, and managed environment for your agent to operate in. By following the steps in this guide, you can move your agent from development to production with confidence.

For more detailed information, refer to the [official Vertex AI Agent Engine documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-engine/agent-engine-introduction).
