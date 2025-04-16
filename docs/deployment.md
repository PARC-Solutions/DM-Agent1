# Deployment Guide: Medical Billing Denial Agent

This document provides detailed instructions for deploying the Medical Billing Denial Agent to Google Vertex AI. It covers all the steps required for setting up the deployment environment, configuring the agent, managing security settings, and monitoring the deployed system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Configuration](#configuration)
4. [Deployment Process](#deployment-process)
5. [Security & Compliance](#security--compliance)
6. [Monitoring & Logging](#monitoring--logging)
7. [Rollbacks & Disaster Recovery](#rollbacks--disaster-recovery)
8. [Troubleshooting](#troubleshooting)
9. [References](#references)

## Prerequisites

Before deploying the Medical Billing Denial Agent, ensure you have the following:

- **Google Cloud Account** with sufficient permissions:
  - Vertex AI Admin role
  - Service Account Admin role
  - Storage Admin role (for staging deployment files)
  - Monitoring Admin role (for setting up metrics and dashboards)
  - Logging Admin role (for log exports)

- **Development Environment**:
  - Python 3.9 or higher
  - Google Cloud SDK installed and configured
  - Access to the project repository

- **Project Resources**:
  - Google Cloud project with Vertex AI API enabled
  - Service account with appropriate permissions
  - KMS encryption key for HIPAA compliance (for production deployments)

## Environment Setup

### 1. Clone and Configure the Repository

If you haven't already set up the repository:

```bash
# Clone the repository
git clone --recursive https://github.com/yourusername/medical-billing-denial-agent.git
cd medical-billing-denial-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Deployment Environment Variables

Create a deployment environment file:

```bash
# Copy the deployment environment template
cp deployment/vertex_ai/.env.deployment.example deployment/vertex_ai/.env.deployment

# Edit the file with your deployment settings
nano deployment/vertex_ai/.env.deployment
```

Required variables to configure:
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account key file
- `DEPLOYMENT_ENVIRONMENT`: Target environment (development, staging, or production)

### 3. Set Up Service Account

For secure deployment, create a dedicated service account with the minimum required permissions:

```bash
# Create service account
gcloud iam service-accounts create medical-billing-agent-sa \
  --display-name="Medical Billing Denial Agent Service Account" \
  --project=your-project-id

# Assign necessary roles
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:medical-billing-agent-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:medical-billing-agent-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:medical-billing-agent-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"

# Create and download a key for the service account
gcloud iam service-accounts keys create medical-billing-agent-sa-key.json \
  --iam-account=medical-billing-agent-sa@your-project-id.iam.gserviceaccount.com
```

Update your `.env.deployment` file with the path to this key file.

### 4. Set Up HIPAA Compliance (Production Only)

For production deployments requiring HIPAA compliance, create a KMS encryption key:

```bash
# Create a key ring
gcloud kms keyrings create hipaa-keyring \
  --location=us-central1 \
  --project=your-project-id

# Create an encryption key
gcloud kms keys create data-encryption-key \
  --location=us-central1 \
  --keyring=hipaa-keyring \
  --purpose=encryption \
  --project=your-project-id

# Grant the service account permission to use the key
gcloud kms keys add-iam-policy-binding data-encryption-key \
  --location=us-central1 \
  --keyring=hipaa-keyring \
  --member="serviceAccount:medical-billing-agent-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter" \
  --project=your-project-id
```

Update your `.env.deployment` file with the encryption key name:

```
ENCRYPTION_KEY_NAME=projects/your-project-id/locations/us-central1/keyRings/hipaa-keyring/cryptoKeys/data-encryption-key
```

## Configuration

### Deployment Configuration Options

The deployment configuration is controlled by environment variables in the `.env.deployment` file and command-line options for the deployment script. Key configuration options include:

| Parameter | Description | Default Value | Required |
|-----------|-------------|---------------|----------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | None | Yes |
| `DEPLOYMENT_ENVIRONMENT` | Target environment | staging | Yes |
| `VERTEX_AI_LOCATION` | Google Cloud region | us-central1 | Yes |
| `VERTEX_AI_MACHINE_TYPE` | Machine type | e2-standard-4 | Yes |
| `MIN_REPLICA_COUNT` | Minimum number of replicas | 1 | Yes |
| `MAX_REPLICA_COUNT` | Maximum number of replicas | 3 | Yes |
| `ENCRYPTION_KEY_NAME` | KMS encryption key | None | For Production |
| `SERVICE_ACCOUNT` | Custom service account | Default compute | No |
| `NETWORK` | VPC network | Default | No |

### Resource Sizing Recommendations

| Environment | Machine Type | Min Replicas | Max Replicas | CPU Target |
|-------------|--------------|--------------|--------------|------------|
| Development | e2-standard-2 | 1 | 1 | N/A |
| Staging | e2-standard-4 | 1 | 2 | 70% |
| Production | e2-standard-4 | 2 | 5 | 60% |
| Production (High Load) | e2-standard-8 | 3 | 10 | 60% |

## Deployment Process

### 1. Run the Deployment Script

The deployment script handles:
- Authentication with Google Cloud
- Configuration validation
- Agent preparation
- Deployment to Vertex AI
- Verification of deployment success

```bash
# Load the deployment environment variables
source deployment/vertex_ai/.env.deployment

# Deploy to the default environment (staging)
python deployment/vertex_ai/deploy.py

# Or specify parameters explicitly
python deployment/vertex_ai/deploy.py \
  --environment production \
  --project-id your-project-id \
  --machine-type e2-standard-4 \
  --min-replicas 2 \
  --max-replicas 5
```

### 2. Set Up Monitoring and Alerting

After deployment, set up monitoring:

```bash
# Set up default monitoring and alerting
python deployment/vertex_ai/monitoring.py \
  --project-id your-project-id \
  --agent-name medical-billing-denial-agent-production

# For log export to a storage bucket
python deployment/vertex_ai/monitoring.py \
  --project-id your-project-id \
  --agent-name medical-billing-denial-agent-production \
  --log-destination gs://your-log-bucket
```

### 3. Verify Deployment

After deployment, verify that the agent is running correctly:

1. Check the Vertex AI console for the deployed endpoint
2. Verify that the monitoring dashboard is available
3. Test the agent with a simple query

## Security & Compliance

### HIPAA Compliance Measures

For HIPAA compliance, the deployment includes:

1. **Data Encryption**:
   - All data at rest is encrypted using the CMEK (Customer-Managed Encryption Key)
   - Data in transit is encrypted via TLS

2. **Access Controls**:
   - Custom service account with minimal permissions
   - IAM policies enforce least privilege

3. **Audit Logging**:
   - Comprehensive logging of all operations
   - Log export for long-term storage and compliance

4. **PHI Handling**:
   - PHI detection mechanism in the agent
   - Content moderation to prevent PHI leakage

### Security Best Practices

1. **Regular Key Rotation**:
   ```bash
   # Create a new version of the encryption key
   gcloud kms keys versions create \
     --location=us-central1 \
     --keyring=hipaa-keyring \
     --key=data-encryption-key \
     --primary \
     --project=your-project-id
   ```

2. **Network Security**:
   - Deploy agents in a private VPC network
   - Use VPC Service Controls to restrict API access

3. **Vulnerability Management**:
   - Regularly update dependencies
   - Monitor security bulletins for Vertex AI and related services

## Monitoring & Logging

### Available Metrics

The deployment automatically sets up the following custom metrics:

- `agent/request_count`: Number of requests to the agent
- `agent/response_time`: Time taken to generate a response
- `agent/error_count`: Number of errors encountered
- `agent/document_processing_time`: Time taken to process documents
- `agent/knowledge_retrieval_time`: Time taken to retrieve information

### Default Alerts

The system includes pre-configured alerts for:

- High error rates
- Slow response times
- Document processing failures

### Log Analysis

Important log entries to monitor:

- PHI detection events
- Authentication and authorization failures
- Knowledge base query failures
- Document processing errors

## Rollbacks & Disaster Recovery

### Rolling Back a Deployment

If you need to roll back to a previous version:

```bash
# Deploy a specific version
python deployment/vertex_ai/deploy.py \
  --environment production \
  --update \
  --app-version 1.0.0
```

### Disaster Recovery Process

In case of a major system failure:

1. Stop traffic to the affected endpoint
2. Identify the cause of the failure using logs and metrics
3. Roll back to the last known good configuration
4. Verify the rollback was successful
5. Conduct a post-mortem and implement preventive measures

## Troubleshooting

### Common Deployment Issues

| Issue | Possible Cause | Resolution |
|-------|---------------|------------|
| Deployment fails with authentication error | Invalid service account credentials | Verify the GOOGLE_APPLICATION_CREDENTIALS path is correct and the key is valid |
| "Quota exceeded" error | Project resource limits reached | Request a quota increase or reduce resource usage |
| Monitoring setup fails | Missing IAM permissions | Ensure the service account has monitoring.admin role |
| Model loading fails | Incompatible model version | Verify the model version in AGENT_MODEL is correct |

### Logs to Check

- Vertex AI deployment logs
- Agent initialization logs
- Custom metrics and alerts

### Support Resources

- Google Cloud Support: [https://cloud.google.com/support](https://cloud.google.com/support)
- Vertex AI Documentation: [https://cloud.google.com/vertex-ai/docs](https://cloud.google.com/vertex-ai/docs)
- Project Support: Contact medical-billing-agent-support@yourdomain.com

## References

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Google Cloud Monitoring](https://cloud.google.com/monitoring/docs)
- [HIPAA Compliance on Google Cloud](https://cloud.google.com/security/compliance/hipaa)
- [Agent Development Kit Documentation](https://cloud.google.com/agent-development-kit/docs)
- [Project Documentation](./architecture.md)
