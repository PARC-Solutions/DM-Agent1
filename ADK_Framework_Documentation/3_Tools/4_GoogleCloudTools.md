# Google Cloud Tools

ADK provides seamless integration with Google Cloud services, allowing your agents to leverage Google's cloud infrastructure and AI capabilities. This document covers the various Google Cloud tools available in ADK and how to use them effectively.

## Overview

Google Cloud tools in ADK allow your agents to:

- Access Google Search
- Query BigQuery datasets
- Interact with Vertex AI services
- Read and write to Cloud Storage
- Call other Google Cloud APIs

These integrations make it easy to build agents that can leverage Google's enterprise-grade infrastructure while maintaining the simplicity and flexibility of ADK.

## Prerequisites

Before using Google Cloud tools, you need to set up authentication:

1. Install the Google Cloud SDK:
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   ```

2. Authenticate with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```

3. Set your Google Cloud project:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

You may also need to enable specific APIs for services you want to use:

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable BigQuery API
gcloud services enable bigquery.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com
```

## Google Search

The Google Search tool allows your agents to search the web and retrieve up-to-date information.

### Setting Up

To use the Google Search tool, you need:

1. A Custom Search Engine ID (CSE ID)
2. An API key for Google Custom Search API

You can create these in the [Google Cloud Console](https://console.cloud.google.com/):

1. Create a new API key in the [API & Services > Credentials](https://console.cloud.google.com/apis/credentials) section
2. Enable the [Custom Search API](https://console.cloud.google.com/apis/library/customsearch.googleapis.com)
3. Create a [Programmable Search Engine](https://programmablesearchengine.google.com/about/) and get your CSE ID

### Using Google Search

```python
from google.adk.agents import Agent
from google.adk.tools.google_search import GoogleSearch

# Create a Google Search tool
search_tool = GoogleSearch(
    api_key="YOUR_API_KEY",
    cse_id="YOUR_CSE_ID"
)

# Create an agent with the search tool
search_agent = Agent(
    name="web_search_agent",
    model="gemini-2.0-flash",
    instruction="Search for information on Google when users ask questions.",
    tools=[search_tool]
)

# Example usage
response = search_agent.run("What is the capital of France?")
```

### Advanced Search Options

You can customize the search behavior:

```python
search_tool = GoogleSearch(
    api_key="YOUR_API_KEY",
    cse_id="YOUR_CSE_ID",
    num_results=5,  # Number of results to return
    safe_search=True,  # Enable safe search filtering
    language="en"  # Preferred language for results
)
```

## Vertex AI Integration

ADK integrates with Vertex AI, Google Cloud's machine learning platform, allowing your agents to leverage specialized machine learning models.

### Vertex Endpoint Predictor

The `VertexEndpointPredictor` tool allows your agent to call deployed models on Vertex AI:

```python
from google.adk.agents import Agent
from google.adk.tools.vertex import VertexEndpointPredictor

# Create a tool that calls a deployed Vertex AI model endpoint
vertex_predictor = VertexEndpointPredictor(
    project="your-gcp-project",
    location="us-central1",
    endpoint_id="your-endpoint-id"
)

# Create an agent with the Vertex AI tool
specialized_agent = Agent(
    name="ml_prediction_agent",
    model="gemini-2.0-flash",
    instruction="Help users get predictions from our specialized ML model.",
    tools=[vertex_predictor]
)
```

### Text Embedding Generator

For generating text embeddings using Vertex AI:

```python
from google.adk.agents import Agent
from google.adk.tools.vertex import VertexTextEmbeddingGenerator

# Create an embedding generator
embedding_tool = VertexTextEmbeddingGenerator(
    project="your-gcp-project",
    location="us-central1",
    model_name="textembedding-gecko@latest"  # Or another embedding model
)

# Use the embedding tool in your agent
agent = Agent(
    name="semantic_search_agent",
    model="gemini-2.0-flash",
    tools=[embedding_tool]
)
```

## BigQuery Integration

The BigQuery tool allows your agents to query data from Google BigQuery tables and datasets.

```python
from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryTool

# Create a BigQuery tool
bq_tool = BigQueryTool(
    project="your-gcp-project",
    location="US"  # or another location where your datasets are
)

# Create a data analysis agent
data_agent = Agent(
    name="data_analysis_agent",
    model="gemini-2.0-flash",
    instruction="""
    You help users analyze data from our BigQuery tables.
    When users ask about data, use the BigQuery tool to run SQL queries.
    Format results in a readable way.
    """,
    tools=[bq_tool]
)
```

### Example Queries

Your agent can now perform queries like:

```python
# The agent can run queries like:
response = data_agent.run("How many users registered last month?")

# The agent might generate and execute SQL like:
# SELECT COUNT(*) AS user_count 
# FROM `project.dataset.users` 
# WHERE registration_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH) AND CURRENT_DATE()
```

### Advanced BigQuery Features

For more complex scenarios, you can customize the BigQuery tool:

```python
bq_tool = BigQueryTool(
    project="your-gcp-project",
    dataset="your-default-dataset",  # Default dataset for queries
    max_results=1000,  # Maximum rows to return
    timeout=60,  # Query timeout in seconds
    dry_run=False,  # Set to True to estimate query cost without running
    use_query_cache=True  # Use BigQuery's query cache when possible
)
```

## Cloud Storage Integration

The Cloud Storage tool enables your agents to read and write files in Google Cloud Storage buckets.

```python
from google.adk.agents import Agent
from google.adk.tools.storage import GCSFileTool

# Create a Cloud Storage tool
storage_tool = GCSFileTool(
    bucket_name="your-gcs-bucket"
)

# Create an agent with the storage tool
storage_agent = Agent(
    name="file_storage_agent",
    model="gemini-2.0-flash",
    instruction="Help users manage files in Google Cloud Storage.",
    tools=[storage_tool]
)
```

### Reading Files

```python
def read_gcs_file(file_path: str) -> dict:
    """Read a file from Google Cloud Storage.
    
    Args:
        file_path: Path to the file in the bucket
        
    Returns:
        dict: File content or error message
    """
    try:
        content = storage_tool.read_file(file_path)
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Add the function to your agent
storage_agent = Agent(
    name="file_reader_agent",
    model="gemini-2.0-flash",
    tools=[read_gcs_file]
)
```

### Writing Files

```python
def write_gcs_file(file_path: str, content: str) -> dict:
    """Write content to a file in Google Cloud Storage.
    
    Args:
        file_path: Path where to write the file in the bucket
        content: Content to write to the file
        
    Returns:
        dict: Success status or error message
    """
    try:
        storage_tool.write_file(file_path, content)
        return {"status": "success", "message": f"File written to {file_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Add the function to your agent
storage_agent = Agent(
    name="file_writer_agent",
    model="gemini-2.0-flash",
    tools=[write_gcs_file]
)
```

## Natural Language Processing Tools

ADK integrates with Google Cloud's Natural Language API for text analysis:

```python
from google.adk.agents import Agent
from google.adk.tools.language import EntityExtractionTool, SentimentAnalysisTool

# Create NLP tools
entity_tool = EntityExtractionTool(project="your-gcp-project")
sentiment_tool = SentimentAnalysisTool(project="your-gcp-project")

# Create an agent with the NLP tools
nlp_agent = Agent(
    name="text_analysis_agent",
    model="gemini-2.0-flash",
    instruction="Analyze text for entities and sentiment when users ask.",
    tools=[entity_tool, sentiment_tool]
)
```

## Authentication Best Practices

When working with Google Cloud tools, follow these authentication best practices:

### Using Application Default Credentials (ADC)

For development and testing:

```python
# Set up Google Cloud authentication
# This uses the environment's Application Default Credentials
import google.auth

credentials, project = google.auth.default()

# These credentials are used automatically by Google Cloud tools
from google.adk.tools.storage import GCSFileTool

storage_tool = GCSFileTool(credentials=credentials)
```

### Service Account Authentication

For production deployments, use service account authentication:

```python
from google.oauth2 import service_account
from google.adk.tools.bigquery import BigQueryTool

# Load service account credentials
credentials = service_account.Credentials.from_service_account_file(
    'path/to/service-account-key.json'
)

# Create a tool with these credentials
bq_tool = BigQueryTool(
    project="your-gcp-project",
    credentials=credentials
)
```

### Environment Variables

You can also set environment variables for authentication:

```bash
# Set environment variable for your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Set path to service account key (alternative to ADC)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

## Multi-Service Agents

You can combine multiple Google Cloud tools in a single agent:

```python
from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryTool
from google.adk.tools.storage import GCSFileTool
from google.adk.tools.google_search import GoogleSearch

# Create multiple Google Cloud tools
bq_tool = BigQueryTool(project="your-gcp-project")
storage_tool = GCSFileTool(bucket_name="your-gcs-bucket")
search_tool = GoogleSearch(api_key="YOUR_API_KEY", cse_id="YOUR_CSE_ID")

# Create an agent with multiple Google Cloud tools
cloud_agent = Agent(
    name="gcp_power_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are an assistant with access to Google Cloud services.
    - Use BigQuery to analyze data
    - Use Cloud Storage to read and write files
    - Use Google Search to find information
    Choose the appropriate tool based on the user's request.
    """,
    tools=[
        bq_tool.query,  # BigQuery query method
        storage_tool.read_file,  # GCS read file method
        storage_tool.write_file,  # GCS write file method
        search_tool  # Google Search tool
    ]
)
```

## Troubleshooting

Common issues when working with Google Cloud tools:

### Authentication Issues

If you encounter authentication errors:

1. Check that you've run `gcloud auth application-default login`
2. Verify your service account has the necessary permissions
3. Confirm the environment variable `GOOGLE_APPLICATION_CREDENTIALS` is set correctly

### API Enablement

If you get "API not enabled" errors:

```bash
# Enable the required API
gcloud services enable SERVICE_NAME.googleapis.com
```

### Rate Limiting

If you encounter rate limits:

1. Implement exponential backoff in your tools
2. Request quota increases if needed
3. Optimize queries to reduce API usage

## Conclusion

Google Cloud tools in ADK provide a powerful way to extend your agents with Google's cloud capabilities. By combining these tools, you can build sophisticated agents that leverage Google's infrastructure for search, data analysis, machine learning, and storage operations.

For more information, refer to the [Google Cloud documentation](https://cloud.google.com/docs) and the specific API documentation for each service.
