# Deploying to Cloud Run

[Cloud Run](https://cloud.google.com/run) is a managed compute platform on Google Cloud that enables you to run containers directly on top of Google's scalable infrastructure. It's an excellent option for deploying ADK agents when you need more control over your deployment environment compared to Vertex AI Agent Engine.

## Benefits of Cloud Run

- **Serverless**: Fully managed infrastructure with automatic scaling
- **Container-based**: Run any container that listens for HTTP requests
- **Pay-per-use**: Only pay for the compute resources you use
- **Custom domains**: Easy integration with custom domains
- **Integration**: Seamless integration with other Google Cloud services
- **Customizable**: Fine-grained control over environment, memory, and CPU allocation

## Prerequisites

Before deploying to Cloud Run, ensure you have:

1. **Google Cloud Project**: An active Google Cloud project with billing enabled
2. **Required APIs**: Cloud Run API enabled
3. **Docker**: Docker installed locally for container building
4. **gcloud CLI**: Google Cloud CLI installed and configured
5. **ADK Agent**: A functional ADK agent ready for deployment

### Setting Up Your Environment

```bash
# Install the Google Cloud SDK if you haven't already
curl https://sdk.cloud.google.com | bash
gcloud init

# Select or create a project
gcloud projects create [PROJECT_ID] --name="[PROJECT_NAME]"  # Optional: create new project
gcloud config set project [PROJECT_ID]

# Enable the Cloud Run API
gcloud services enable run.googleapis.com

# Configure Docker for Google Container Registry
gcloud auth configure-docker
```

## Containerizing Your ADK Agent

To deploy to Cloud Run, you need to package your agent as a Docker container:

### 1. Create a Flask Application

First, create a Flask application to serve your agent:

```python
# app.py
from flask import Flask, request, jsonify
from google.adk.agents import Agent
from your_agent_module import your_agent  # Import your agent

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id', 'default-session')
    
    # Run your agent
    response = your_agent.run(message, session_id=session_id)
    
    return jsonify({
        'response': response.text,
        'session_id': session_id
    })

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

### 2. Create a Dockerfile

Create a Dockerfile in your project directory:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080

# Run the application
CMD ["python", "app.py"]
```

### 3. Create a Requirements File

Create a `requirements.txt` file with all your dependencies:

```
flask==2.0.1
gunicorn==20.1.0
google-adk==0.1.0
# Add any other dependencies your agent needs
```

### 4. Build and Push the Container

Build your container image and push it to Google Container Registry:

```bash
# Build the container image
gcloud builds submit --tag gcr.io/[PROJECT_ID]/adk-agent:v1

# Alternatively, build locally and push
docker build -t gcr.io/[PROJECT_ID]/adk-agent:v1 .
docker push gcr.io/[PROJECT_ID]/adk-agent:v1
```

## Deploying to Cloud Run

Once your container is built and pushed, deploy it to Cloud Run:

### 1. Basic Deployment

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

The `--allow-unauthenticated` flag makes your service publicly accessible. Remove it if you want to restrict access.

### 2. Advanced Deployment Options

For production deployments, you might want to set additional options:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars "ENVIRONMENT=production"
```

### 3. Setting Environment Variables

For sensitive values like API keys, set them as environment variables:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --platform managed \
  --region us-central1 \
  --set-env-vars "API_KEY=your-api-key,ENVIRONMENT=production"
```

For better security, use Secret Manager:

```bash
# First, create a secret
gcloud secrets create api-key --data-file=./api-key.txt

# Then reference it in your deployment
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --platform managed \
  --region us-central1 \
  --set-secrets "API_KEY=api-key:latest"
```

## Setting Up a Custom Domain

To use a custom domain with your Cloud Run service:

1. **Verify domain ownership** in the Google Cloud Console
2. **Map the domain** to your Cloud Run service:

```bash
gcloud beta run domain-mappings create \
  --service adk-agent \
  --domain agent.yourdomain.com \
  --region us-central1
```

3. **Configure DNS records** as instructed by Google Cloud

## Continuous Deployment with Cloud Build

Set up continuous deployment using Cloud Build:

1. Create a `cloudbuild.yaml` file:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/adk-agent:$COMMIT_SHA', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/adk-agent:$COMMIT_SHA']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
    - 'run'
    - 'deploy'
    - 'adk-agent'
    - '--image'
    - 'gcr.io/$PROJECT_ID/adk-agent:$COMMIT_SHA'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'

images:
  - 'gcr.io/$PROJECT_ID/adk-agent:$COMMIT_SHA'
```

2. Set up a trigger in Cloud Build to run on repository changes

## Implementing a Production-Ready Server

For production, use Gunicorn as the WSGI server instead of Flask's development server:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080

# Run the application with Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

This configuration uses:
- One worker process (`--workers 1`)
- Multiple threads (`--threads 8`) for concurrent requests
- No timeout (`--timeout 0`) for long-running operations

## Optimizing Container Performance

### 1. Multi-stage Builds

Use multi-stage builds to create smaller containers:

```dockerfile
# Build stage
FROM python:3.9 AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

ENV PORT=8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

### 2. Resource Allocation

Optimize memory and CPU allocation based on your agent's needs:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --memory 2Gi \
  --cpu 1
```

### 3. Startup CPU Boost

For faster startup times, enable CPU boost:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --cpu 1 \
  --cpu-boost
```

## Monitoring Your Cloud Run Service

### 1. Cloud Monitoring

Set up monitoring for your Cloud Run service:

```bash
gcloud monitoring dashboards create \
  --config-from-file=dashboard.json
```

### 2. Logging

View logs for your service:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=adk-agent" --limit=10
```

### 3. Error Reporting

Implement error handling in your application to track errors in Error Reporting:

```python
import logging
import google.cloud.logging
import traceback

# Setup Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception
    logging.error(f"Unhandled exception: {str(e)}")
    logging.error(traceback.format_exc())
    
    # Return an error response
    return jsonify({"error": "Internal server error"}), 500
```

## Securing Your Cloud Run Service

### 1. Authentication

Require authentication for your service:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --no-allow-unauthenticated
```

### 2. IAM Permissions

Grant specific IAM roles for service access:

```bash
gcloud run services add-iam-policy-binding adk-agent \
  --member="user:example@gmail.com" \
  --role="roles/run.invoker" \
  --region=us-central1
```

### 3. VPC Connectivity

For additional security, configure VPC connectivity:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --vpc-connector=projects/[PROJECT_ID]/locations/us-central1/connectors/my-connector
```

## Cost Optimization

### 1. Scaling to Zero

By default, Cloud Run scales to zero when not in use. Control minimum instances:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --min-instances=0 \
  --max-instances=10
```

### 2. Request-based Scaling

Cloud Run automatically scales based on request volume. Set concurrency:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --concurrency=80
```

### 3. CPU Allocation

Allocate CPU only when processing requests to reduce costs:

```bash
gcloud run deploy adk-agent \
  --image gcr.io/[PROJECT_ID]/adk-agent:v1 \
  --cpu-throttling
```

## Troubleshooting

### Common Deployment Issues

1. **Container fails to start**: Check logs for startup errors
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=adk-agent AND severity>=ERROR"
   ```

2. **Memory limits**: If your agent requires more memory, increase allocation
   ```bash
   gcloud run deploy adk-agent --memory 2Gi
   ```

3. **Timeout errors**: Increase the request timeout
   ```bash
   gcloud run deploy adk-agent --timeout=300
   ```

4. **Authentication issues**: Check IAM permissions and service account configuration

## Best Practices

1. **Health Checks**: Implement a health check endpoint
2. **Graceful Shutdown**: Handle SIGTERM signals for clean shutdowns
3. **Stateless Design**: Design your service to be stateless
4. **Optimize Cold Starts**: Minimize dependencies and use startup strategies
5. **Proper Error Handling**: Implement comprehensive error handling
6. **Staged Rollouts**: Use revisions and traffic splitting for safe deployments
7. **Monitoring**: Set up alerts for errors and performance issues

## Conclusion

Cloud Run provides a flexible, scalable platform for deploying ADK agents when you need more control over your environment than Vertex AI Agent Engine offers. By containerizing your agent and deploying it to Cloud Run, you get the benefits of serverless infrastructure while maintaining flexibility in your application's configuration and behavior.

This approach is particularly well-suited for:

- Agents that need custom dependencies or runtime environments
- Applications that require fine-grained control over HTTP handling
- Services that need to integrate with existing APIs or systems
- Deployments that require custom domains or authentication schemes

For more information, refer to the [official Cloud Run documentation](https://cloud.google.com/run/docs).
