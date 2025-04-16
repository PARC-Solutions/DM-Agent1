# Model Integration

## Using Different Models with ADK

The Agent Development Kit (ADK) is designed for flexibility, allowing you to integrate various Large Language Models (LLMs) into your agents. This document details how to leverage Google Gemini models effectively and integrate other popular models, including those hosted externally or running locally.

## Integration Mechanisms

ADK primarily uses two mechanisms for model integration:

1. **Direct String / Registry**: For models tightly integrated with Google Cloud (like Gemini models accessed via Google AI Studio or Vertex AI) or models hosted on Vertex AI endpoints. You typically provide the model name or endpoint resource string directly to the `LlmAgent`. ADK's internal registry resolves this string to the appropriate backend client.

2. **Wrapper Classes**: For broader compatibility, especially with models outside the Google ecosystem or those requiring specific client configurations. You instantiate a specific wrapper class and pass this object as the `model` parameter to your `LlmAgent`.

## Using Google Gemini Models

This is the most direct way to use Google's flagship models within ADK.

### Basic Integration

Pass the model's identifier string directly to the `model` parameter of `LlmAgent` (or its alias, `Agent`):

```python
from google.adk.agents import Agent

# Create an agent using a Gemini model
my_agent = Agent(
    name="gemini_agent",
    model="gemini-2.0-flash",  # Directly use the model identifier
    description="A helpful assistant powered by Gemini"
)
```

### Available Gemini Models

ADK supports various Gemini models with different capabilities:

- `gemini-2.0-flash`: Optimized for fast responses
- `gemini-2.0-pro`: More powerful model for complex reasoning
- `gemini-2.0-pro-vision`: Supports image understanding
- `gemini-1.5-flash`: Legacy model, fast responses
- `gemini-1.5-pro`: Legacy model, more powerful

Use newer models (2.0 series) when possible for best results.

### Backend Options & Setup

The `google-genai` library, used internally by ADK for Gemini, can connect through either Google AI Studio or Vertex AI.

#### Google AI Studio

* **Use Case**: Ideal for development, prototyping, and personal projects.
* **Setup**: Typically requires an API key set as an environment variable:
  ```bash
  export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
  export GOOGLE_GENAI_USE_VERTEXAI=FALSE
  ```
* **Models**: Find all available models on the [Google AI for Developers site](https://ai.google.dev/).

#### Vertex AI

* **Use Case**: Recommended for production applications, leveraging Google Cloud infrastructure. Gemini on Vertex AI supports enterprise-grade features, security, and compliance controls.
* **Setup**:
  * Authenticate using Application Default Credentials (ADC):
    ```bash
    gcloud auth application-default login
    ```
  * Set your Google Cloud project and location:
    ```bash
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```
  * Enable Vertex AI:
    ```bash
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Model Parameters

You can configure various parameters when using Gemini models:

```python
from google.adk.agents import Agent

agent = Agent(
    name="configurable_gemini_agent",
    model="gemini-2.0-pro",
    description="Agent with custom model parameters",
    
    # Model parameters
    temperature=0.2,  # Lower values: more deterministic, higher values: more creative (0.0-1.0)
    top_p=0.95,       # Controls diversity via nucleus sampling
    top_k=40,         # Controls diversity via limiting vocabulary
    max_tokens=1024,  # Maximum output length
)
```

## Using OpenAI Models

ADK supports OpenAI models (like GPT-4) through a wrapper class:

```python
from google.adk.agents import Agent
from google.adk.models.openai import OpenAIModel

# Create an OpenAI model wrapper
openai_model = OpenAIModel(
    model_name="gpt-4",  # or "gpt-3.5-turbo", etc.
    api_key="YOUR_OPENAI_API_KEY"
)

# Create an agent using the OpenAI model
agent = Agent(
    name="openai_agent",
    model=openai_model,  # Pass the model wrapper
    description="A helpful assistant powered by GPT-4"
)
```

### OpenAI Model Parameters

You can configure various parameters for OpenAI models:

```python
from google.adk.models.openai import OpenAIModel

openai_model = OpenAIModel(
    model_name="gpt-4",
    api_key="YOUR_OPENAI_API_KEY",
    temperature=0.3,
    max_tokens=2048,
    top_p=0.9,
    frequency_penalty=0.0,
    presence_penalty=0.0
)
```

## Using Anthropic Models

ADK supports Anthropic Claude models through a wrapper class:

```python
from google.adk.agents import Agent
from google.adk.models.anthropic import AnthropicModel

# Create an Anthropic model wrapper
claude_model = AnthropicModel(
    model_name="claude-3-opus",  # or "claude-3-sonnet", "claude-2", etc.
    api_key="YOUR_ANTHROPIC_API_KEY"
)

# Create an agent using the Anthropic model
agent = Agent(
    name="claude_agent",
    model=claude_model,  # Pass the model wrapper
    description="A helpful assistant powered by Claude"
)
```

### Anthropic Model Parameters

```python
from google.adk.models.anthropic import AnthropicModel

claude_model = AnthropicModel(
    model_name="claude-3-opus",
    api_key="YOUR_ANTHROPIC_API_KEY",
    temperature=0.3,
    max_tokens=2048,
    top_p=0.9
)
```

## Using Vertex AI Model Endpoints

You can use any model deployed to a Vertex AI endpoint:

```python
from google.adk.agents import Agent
from google.adk.models.vertex import VertexAIEndpoint

# Create a Vertex AI endpoint wrapper
vertex_model = VertexAIEndpoint(
    project="your-gcp-project",
    location="us-central1",
    endpoint_id="your-endpoint-id"
)

# Create an agent using the Vertex AI endpoint
agent = Agent(
    name="custom_vertex_agent",
    model=vertex_model,  # Pass the model wrapper
    description="A helpful assistant using a custom model on Vertex AI"
)
```

### Vertex AI Model Parameters

```python
from google.adk.models.vertex import VertexAIEndpoint

vertex_model = VertexAIEndpoint(
    project="your-gcp-project",
    location="us-central1",
    endpoint_id="your-endpoint-id",
    
    # Optional parameters
    temperature=0.2,
    max_tokens=1024,
    credentials=your_custom_credentials  # Custom credentials if needed
)
```

## Using Local Models (e.g., via LiteLLM)

For local models or models accessed through frameworks like LiteLLM:

```python
from google.adk.agents import Agent
from google.adk.models.litellm import LiteLLMModel

# Create a LiteLLM model wrapper
litellm_model = LiteLLMModel(
    model_name="ollama/llama2",  # Local model via Ollama
    api_base="http://localhost:11434"  # Local server address
)

# Create an agent using the local model
agent = Agent(
    name="local_agent",
    model=litellm_model,  # Pass the model wrapper
    description="A helpful assistant using a local model"
)
```

### LiteLLM Parameters

```python
from google.adk.models.litellm import LiteLLMModel

litellm_model = LiteLLMModel(
    model_name="ollama/llama2",
    api_base="http://localhost:11434",
    temperature=0.3,
    max_tokens=2048,
    top_p=0.9,
    timeout=30  # Seconds before timeout
)
```

## Using Multiple Models in the Same Application

You can use different models for different agents in the same application:

```python
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.openai import OpenAIModel
from google.adk.models.anthropic import AnthropicModel

# Create different model wrappers
gemini_model = "gemini-2.0-pro"  # Direct string for Gemini
gpt_model = OpenAIModel(model_name="gpt-4", api_key="OPENAI_KEY")
claude_model = AnthropicModel(model_name="claude-3-opus", api_key="ANTHROPIC_KEY")

# Create agents with different models
routing_agent = Agent(
    name="router",
    model=gemini_model,
    description="Routes queries to specialized agents"
)

creative_agent = Agent(
    name="creative_writer",
    model=gpt_model,
    description="Specializes in creative writing"
)

analytical_agent = Agent(
    name="analyst",
    model=claude_model,
    description="Specializes in data analysis"
)

# Combine agents in a workflow
multi_model_system = SequentialAgent(
    name="multi_model_system",
    agents=[routing_agent, creative_agent, analytical_agent]
)
```

## Custom Model Wrappers

You can create custom model wrappers for models not directly supported by ADK:

```python
from google.adk.models import BaseModel
from google.adk.models import LlmRequest, LlmResponse
import requests

class CustomAPIModel(BaseModel):
    """Wrapper for a custom API-based language model."""
    
    def __init__(self, api_url, api_key, **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url
        self.api_key = api_key
    
    async def generate(self, request: LlmRequest) -> LlmResponse:
        """Generate a response from the model."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": request.prompt,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature or 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return LlmResponse(text=result["generated_text"])
            
        except Exception as e:
            # Handle errors
            return LlmResponse(
                text=f"Error generating response: {str(e)}",
                error=True
            )

# Use the custom model wrapper
custom_model = CustomAPIModel(
    api_url="https://your-custom-llm-api.com/generate",
    api_key="YOUR_API_KEY"
)

# Create an agent with the custom model
agent = Agent(
    name="custom_model_agent",
    model=custom_model,
    description="Agent using a custom model API"
)
```

## Model Fallback Mechanism

You can implement a fallback mechanism for model reliability:

```python
from google.adk.models import BaseModel, LlmRequest, LlmResponse
from google.adk.models.openai import OpenAIModel

class FallbackModel(BaseModel):
    """Model wrapper with fallback capability."""
    
    def __init__(self, primary_model, fallback_model):
        super().__init__()
        self.primary_model = primary_model
        self.fallback_model = fallback_model
    
    async def generate(self, request: LlmRequest) -> LlmResponse:
        try:
            # Try the primary model first
            response = await self.primary_model.generate(request)
            
            # If there was an error, try the fallback
            if response.error:
                print("Primary model failed, using fallback model")
                return await self.fallback_model.generate(request)
                
            return response
            
        except Exception as e:
            print(f"Error with primary model: {str(e)}, using fallback")
            # Try the fallback model
            try:
                return await self.fallback_model.generate(request)
            except Exception as fallback_error:
                # Both models failed
                return LlmResponse(
                    text="Sorry, I'm unable to generate a response at the moment.",
                    error=True
                )

# Create models
primary = OpenAIModel(model_name="gpt-4", api_key="OPENAI_KEY")
fallback = "gemini-2.0-pro"  # Gemini as fallback

# Create a fallback model
resilient_model = FallbackModel(primary_model=primary, fallback_model=fallback)

# Create an agent with the fallback mechanism
agent = Agent(
    name="resilient_agent",
    model=resilient_model,
    description="Agent with fallback model capability"
)
```

## Vision Models

For models that support image understanding:

```python
from google.adk.agents import Agent
import google.genai.types as types
from PIL import Image
import io

# Create an agent with a vision-capable model
vision_agent = Agent(
    name="image_analyzer",
    model="gemini-2.0-pro-vision",  # Vision-capable model
    description="Analyzes images and provides descriptions"
)

# Function to load an image for the agent
def analyze_image(image_path, question="What's in this image?"):
    # Load the image
    with Image.open(image_path) as img:
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format)
        img_bytes = img_byte_arr.getvalue()
    
    # Create a Part object for the image
    image_part = types.Part.from_data(data=img_bytes, mime_type=f"image/{img.format.lower()}")
    
    # Run the agent with the image
    response = vision_agent.run(
        question,
        artifacts=[image_part]  # Pass as a list of artifacts
    )
    
    return response.text

# Example usage
result = analyze_image("path/to/image.jpg", "Describe what you see in this image.")
print(result)
```

## Best Practices for Model Integration

### 1. Environment-based Model Selection

Configure models based on the environment:

```python
import os

# Determine which model to use based on environment
environment = os.environ.get("ENVIRONMENT", "development")

if environment == "production":
    # Use more powerful models in production
    model_name = "gemini-2.0-pro"
elif environment == "testing":
    # Use faster models for testing
    model_name = "gemini-2.0-flash"
else:  # development
    # Use local models for development if available
    try:
        from google.adk.models.litellm import LiteLLMModel
        model = LiteLLMModel(model_name="ollama/llama2")
    except:
        # Fall back to Gemini
        model_name = "gemini-2.0-flash"

# Create the agent with the selected model
agent = Agent(name="environment_aware_agent", model=model_name)
```

### 2. Model Parameter Optimization

Adjust model parameters based on the use case:

```python
# For factual, deterministic responses (e.g., customer support)
factual_agent = Agent(
    name="factual_agent",
    model="gemini-2.0-pro",
    temperature=0.1,  # Low temperature for deterministic outputs
    top_p=0.9,
    max_tokens=1024
)

# For creative tasks (e.g., content generation)
creative_agent = Agent(
    name="creative_agent",
    model="gemini-2.0-pro",
    temperature=0.8,  # Higher temperature for more creative outputs
    top_p=0.95,
    max_tokens=2048
)
```

### 3. Cost Management

Implement cost management strategies:

```python
# For low-cost operation, use smaller/faster models
low_cost_agent = Agent(
    name="efficient_agent",
    model="gemini-2.0-flash",  # Faster, more efficient model
    max_tokens=512,  # Limit response length
)

# For premium features, use more powerful models
premium_agent = Agent(
    name="premium_agent",
    model="gemini-2.0-pro",
    max_tokens=2048
)

# Choose model based on user tier
def get_agent_for_user(user_tier):
    if user_tier == "premium":
        return premium_agent
    else:
        return low_cost_agent
```

### 4. Model Versioning

Manage model versions explicitly:

```python
# Define model versions
MODEL_VERSIONS = {
    "current": "gemini-2.0-pro",
    "previous": "gemini-1.5-pro",
    "experimental": "gemini-2.0-pro-experimental"  # Hypothetical future version
}

# Create an agent with version tracking
agent = Agent(
    name="versioned_agent",
    model=MODEL_VERSIONS["current"],
    description=f"Agent using model version: {MODEL_VERSIONS['current']}"
)

# Log the model version for tracking
print(f"Using model version: {MODEL_VERSIONS['current']}")
```

## Conclusion

ADK's flexible model integration system allows you to use a wide range of LLMs, from Google Gemini models to OpenAI GPT models, Anthropic Claude models, and even local open-source models. By leveraging the appropriate integration mechanism and configuring models optimally for your use case, you can build agents that balance performance, cost, and reliability.

This flexibility enables you to:
- Choose the right model for each specific task
- Implement fallback mechanisms for reliability
- Optimize model parameters for different scenarios
- Manage costs by selecting appropriate models for different contexts

As you develop more sophisticated agent applications, consider creating a model selection strategy that aligns with your requirements for performance, cost, and reliability.
