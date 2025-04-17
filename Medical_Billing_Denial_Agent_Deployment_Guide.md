# Medical Billing Denial Agent: Complete Deployment Guide

This guide will walk you through exactly how to deploy the Medical Billing Denial Agent system step-by-step. This document is designed for first-time users with clear instructions on where to go and what to do at each stage.

## Table of Contents
1. [Google Cloud Account Setup](#1-google-cloud-account-setup)
2. [Install Required Software](#2-install-required-software)
3. [Get the Project Code](#3-get-the-project-code)
4. [Create Service Account & Permissions](#4-create-service-account--permissions)
5. [Configure Your Project](#5-configure-your-project)
6. [Deploy to Vertex AI](#6-deploy-to-vertex-ai)
7. [Set Up Monitoring](#7-set-up-monitoring)
8. [Verify Your Deployment](#8-verify-your-deployment)
9. [Troubleshooting](#9-troubleshooting)

## 1. Google Cloud Account Setup

### 1.1 Create or Access Your Google Cloud Account
- Go to https://cloud.google.com
- Click "Get Started for Free" if you don't have an account
- Sign in with your Google account
- Complete the registration process (requires credit card, but you get $300 free credit)

### 1.2 Create a New Project
- Once logged in, look at the top bar for the project dropdown menu
- Click on the dropdown (it may say "Select a project")
- Click "New Project" in the window that opens
- Enter a project name (e.g., "Medical-Billing-Agent")
- Click "Create"
- Wait for the notification that project creation is complete
- Click on the notification or select your new project from the dropdown

### 1.3 Enable Required APIs
- In the left navigation menu, click "APIs & Services" → "Library"
- Search for and enable each of these APIs (click on each one and press "Enable"):
  - "Vertex AI API"
  - "Cloud Storage API"
  - "IAM Service Account Credentials API"
  - "Logging API"
  - "Monitoring API"

## 2. Install Required Software

### 2.1 Install Python
- Go to https://www.python.org/downloads/
- Download Python 3.9 or higher for your operating system
- Run the installer
- **Important**: Check "Add Python to PATH" during installation
- Verify installation by opening a command prompt or terminal and typing:
  ```
  python --version
  ```

### 2.2 Install Git
- Go to https://git-scm.com/downloads
- Download Git for your operating system
- Run the installer with default options
- Verify installation by opening a command prompt or terminal and typing:
  ```
  git --version
  ```

### 2.3 Install Google Cloud SDK
- Go to https://cloud.google.com/sdk/docs/install
- Download the installer for your operating system
- Run the installer
- After installation completes, open a new terminal or command prompt
- Initialize the SDK by running:
  ```
  gcloud init
  ```
- Follow the prompts to log in to your Google account
- Select your new project when prompted

## 3. Get the Project Code

### 3.1 Clone the Repository
- Open a terminal or command prompt
- Navigate to where you want to save the project
- Run the following command:
  ```
  git clone --recursive https://github.com/yourusername/medical-billing-denial-agent.git
  ```
  (Replace "yourusername" with the actual repository owner)
- Move into the project directory:
  ```
  cd medical-billing-denial-agent
  ```

### 3.2 Set Up Python Environment
- Create a virtual environment:
  - On Windows:
    ```
    python -m venv venv
    venv\Scripts\activate
    ```
  - On macOS/Linux:
    ```
    python -m venv venv
    source venv/bin/activate
    ```
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```

## 4. Create Service Account & Permissions

### 4.1 Create a Service Account
- Go to Google Cloud Console: https://console.cloud.google.com
- Make sure your project is selected at the top
- In the left navigation menu, go to "IAM & Admin" → "Service Accounts"
- Click "Create Service Account" at the top of the page
- Enter these details:
  - Service account name: `medical-billing-agent-sa`
  - Description: `Service account for Medical Billing Denial Agent`
- Click "Create and Continue"

### 4.2 Assign Permissions
- In the "Grant this service account access to project" section, add the following roles:
  - Search for and add "Vertex AI User"
  - Click "Add Another Role" and add "Service Account User"
  - Click "Add Another Role" and add "Storage Object Admin"
  - Click "Add Another Role" and add "Logging Admin"
  - Click "Add Another Role" and add "Monitoring Admin"
- Click "Continue"
- In the "Grant users access to this service account" section, you can leave it empty
- Click "Done"

### 4.3 Create and Download Service Account Key
- In the service accounts list, find your new service account (`medical-billing-agent-sa`)
- Click on the three dots (⋮) at the end of the row and select "Manage keys"
- Click "Add Key" → "Create new key"
- Select "JSON" format
- Click "Create"
- The key file will download automatically to your computer
- Move this file to a secure location on your computer
- Remember this location as you'll need the path later

## 5. Configure Your Project

### 5.1 Set Up Environment Variables
- In your project directory, copy the deployment environment example file:
  ```
  cp deployment/vertex_ai/.env.deployment.example deployment/vertex_ai/.env.deployment
  ```
- Open the new `.env.deployment` file in a text editor
- Update the following values:
  - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID (find this at the top of the Google Cloud Console)
  - `GOOGLE_APPLICATION_CREDENTIALS`: Full path to your downloaded key file
    - Example on Windows: `C:\Users\YourName\keys\medical-billing-agent-sa-key.json`
    - Example on macOS/Linux: `/home/username/keys/medical-billing-agent-sa-key.json`
  - `DEPLOYMENT_ENVIRONMENT`: Set to `staging` for testing or `production` for final deployment
  - `VERTEX_AI_LOCATION`: Set to a region close to your users (e.g., `us-central1`)
  - `VERTEX_AI_MACHINE_TYPE`: For initial deployment, use `e2-standard-4`
  - `MIN_REPLICA_COUNT`: Start with `1`
  - `MAX_REPLICA_COUNT`: Start with `3`
- Save and close the file

### 5.2 Create a .env File from Example
- Copy the main environment example file:
  ```
  cp .env.example .env
  ```
- Open the `.env` file in a text editor
- Update at minimum:
  - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID (same as above)
  - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your key file (same as above)
  - `AGENT_MODEL`: Set to `gemini-pro` (or the specified model for your deployment)
- Save and close the file

## 6. Deploy to Vertex AI

### 6.1 Load Environment Variables
- In your terminal, make sure you're in the project directory
- Load the environment variables:
  - On Windows:
    - Open PowerShell and run:
    ```
    $env:GOOGLE_CLOUD_PROJECT="your-project-id"
    $env:GOOGLE_APPLICATION_CREDENTIALS="path-to-your-key-file.json"
    ```
    (Replace with your actual values)
  - On macOS/Linux:
    ```
    source deployment/vertex_ai/.env.deployment
    ```

### 6.2 Run the Deployment Script
- In your terminal, run:
  ```
  python deployment/vertex_ai/deploy.py
  ```
- This process will take 10-15 minutes to complete
- You'll see progress information in the terminal
- Wait for the "Deployment successful" message

### 6.3 For Advanced Deployment Options (Optional)
If you need specific deployment parameters:
```
python deployment/vertex_ai/deploy.py --environment production --project-id your-project-id --machine-type e2-standard-4 --min-replicas 2 --max-replicas 5
```

## 7. Set Up Monitoring

### 7.1 Configure Basic Monitoring
- In your terminal, run:
  ```
  python deployment/vertex_ai/monitoring.py --project-id your-project-id --agent-name medical-billing-denial-agent-production
  ```
  (Replace "your-project-id" with your actual Google Cloud project ID)

### 7.2 Set Up Log Storage (Optional but Recommended)
For storing logs long-term (good for HIPAA compliance):
- First, create a storage bucket in Google Cloud Console:
  - Go to "Cloud Storage" → "Buckets"
  - Click "Create Bucket"
  - Name your bucket (e.g., "medical-billing-agent-logs")
  - Select the same region as your deployment
  - Choose "Standard" storage class
  - Under "Choose how to control access to objects", select "Uniform"
  - Click "Create"
- Then set up log export:
  ```
  python deployment/vertex_ai/monitoring.py --project-id your-project-id --agent-name medical-billing-denial-agent-production --log-destination gs://your-log-bucket-name
  ```

## 8. Verify Your Deployment

### 8.1 Check Vertex AI Console
- Go to Google Cloud Console: https://console.cloud.google.com
- In the left navigation menu, go to "Vertex AI" → "Endpoints"
- Look for an endpoint named something like "medical-billing-denial-agent-production"
- Verify the status is "Deployed" with a green checkmark

### 8.2 Check Monitoring Dashboard
- In the left navigation menu, go to "Monitoring" → "Dashboards"
- Look for "Medical Billing Denial Agent Monitoring"
- Click to open and verify that metrics are being displayed

### 8.3 Test Your Deployment
- In Vertex AI Endpoints, click on your agent endpoint
- Look for a "Test" tab or "Try this API" option
- Send a simple test request to verify the agent responds correctly

## 9. Troubleshooting

### 9.1 Deployment Fails with Authentication Error
- **Problem**: Error about invalid credentials or authentication failure
- **Solution**:
  - Verify the path in `GOOGLE_APPLICATION_CREDENTIALS` is correct
  - Make sure the service account has all required permissions
  - Try downloading a new key file and updating the path

### 9.2 "Quota Exceeded" Error
- **Problem**: Error about quota limits or resource availability
- **Solution**:
  - Go to "IAM & Admin" → "Quotas" in Google Cloud Console
  - Filter for Vertex AI quotas
  - Select the quota that's reached its limit
  - Click "Edit Quotas" and request an increase

### 9.3 Deployment Script Errors
- **Problem**: Python errors when running the deployment script
- **Solution**:
  - Make sure all dependencies are installed: `pip install -r requirements.txt`
  - Check that your Python version is 3.9 or higher
  - Verify all environment variables are set correctly

### 9.4 Agent Not Responding
- **Problem**: Deployment succeeded but agent doesn't respond
- **Solution**:
  - Check logs: Go to "Logging" → "Logs Explorer" in Google Cloud Console
  - Filter for your endpoint name
  - Look for error messages
  - Make sure all required APIs are enabled

### 9.5 Getting Help
If you encounter issues not covered here:
- Review the detailed documentation in the `docs/` directory
- Check the ADK Framework Documentation for specific implementation details
- Contact medical-billing-agent-support@yourdomain.com for specialized assistance

---

## Maintenance and Updates

Once deployed, to update your agent:
1. Make code changes locally
2. Run the deployment script again with the `--update` flag:
   ```
   python deployment/vertex_ai/deploy.py --update
   ```

For HIPAA compliance in production:
1. Set up the encryption key as described in the deployment documentation
2. Regularly rotate encryption keys
3. Ensure all PHI processing follows your organization's compliance protocols

---

Congratulations! You've successfully deployed the Medical Billing Denial Agent to Google Vertex AI.
