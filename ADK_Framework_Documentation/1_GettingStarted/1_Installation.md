# Installation

## Creating & Activating a Virtual Environment

We recommend creating a virtual Python environment using venv:

```bash
python -m venv .venv
```

Now, you can activate the virtual environment using the appropriate command for your operating system and environment:

```bash
# Mac / Linux
source .venv/bin/activate

# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1
```

## Installing ADK

```bash
pip install google-adk
```

(Optional) Verify your installation:

```bash
pip show google-adk
```

## Setting Up Model Authentication

Your agent's ability to understand user requests and generate responses is powered by a Large Language Model (LLM). Your agent needs to make secure calls to this external LLM service, which requires authentication credentials. Without valid authentication, the LLM service will deny the agent's requests, and the agent will be unable to function.

### Using Google AI Studio

1. Get an API key from [Google AI Studio](https://ai.google.dev/).

2. Create a `.env` file in your project directory and add the following:

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_ACTUAL_API_KEY_HERE
```

3. Replace `GOOGLE_API_KEY` with your actual API key.

### Using Vertex AI

For production applications, you may want to use Vertex AI:

1. Authenticate using Application Default Credentials (ADC):

```bash
gcloud auth application-default login
```

2. Set your Google Cloud project and location:

```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
```

3. Enable Vertex AI in your environment:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

## Next Steps

Once you've completed the installation, proceed to the [Quickstart guide](./2_Quickstart.md) to create your first agent.
