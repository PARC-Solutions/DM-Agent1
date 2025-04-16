# Artifacts

## Overview

In ADK, **Artifacts** represent a mechanism for managing named, versioned binary data associated with user interactions. They allow your agents and tools to handle data beyond simple text strings, enabling richer interactions involving files, images, audio, and other binary formats.

## What are Artifacts?

An Artifact is essentially a piece of binary data (like the content of a file) identified by a unique `filename` string within a specific scope (session or user). Each time you save an artifact with the same filename, a new version is created.

Artifacts are consistently represented using the standard `google.genai.types.Part` object. The core data is typically stored within the `inline_data` attribute of the `Part`, which itself contains:
- `data`: The raw binary content as `bytes`
- `mime_type`: A string indicating the type of the data (e.g., `'image/png'`)

Here's an example of how an artifact might be represented:

```python
import google.genai.types as types

# Assume 'image_bytes' contains the binary data of a PNG image
image_bytes = b'\x89PNG\r\n\x1a\n...' # Placeholder for actual image bytes

image_artifact = types.Part(
    inline_data=types.Blob(
        mime_type="image/png",
        data=image_bytes
    )
)

# You can also use the convenience constructor:
image_artifact_alt = types.Part.from_data(data=image_bytes, mime_type="image/png")

print(f"Artifact MIME Type: {image_artifact.inline_data.mime_type}")
print(f"Artifact Data (first 10 bytes): {image_artifact.inline_data.data[:10]}")
```

## Artifact Scopes

Artifacts can be associated with different scopes:

1. **Session Artifacts**: Tied to a specific conversation session and only accessible within that session.
2. **User Artifacts**: Associated with a user and accessible across all of their sessions.

## Working with Artifacts

### Creating and Storing Artifacts

To store an artifact, you typically use the `ArtifactService`:

```python
from google.adk.artifacts import InMemoryArtifactService
import google.genai.types as types

# Create an artifact service
artifact_service = InMemoryArtifactService()

# Create an artifact
image_bytes = get_image_bytes()  # Your function to get image data
image_artifact = types.Part.from_data(data=image_bytes, mime_type="image/png")

# Store the artifact
artifact_id = artifact_service.store_artifact(
    session_id="user_session_123",
    filename="profile_image.png",
    artifact=image_artifact
)

print(f"Stored artifact with ID: {artifact_id}")
```

### Retrieving Artifacts

To retrieve a stored artifact:

```python
# Get the latest version of an artifact
latest_image = artifact_service.get_artifact(
    session_id="user_session_123",
    filename="profile_image.png"
)

# Get a specific version
specific_version = artifact_service.get_artifact(
    session_id="user_session_123",
    filename="profile_image.png",
    version=2  # Specific version number
)
```

### Using Artifacts with Agents

When working with agents, you can pass artifacts directly to the `run` method:

```python
from google.adk.agents import Agent
import google.genai.types as types
from PIL import Image
import io

# Create a vision-capable agent
vision_agent = Agent(
    name="image_analyzer",
    model="gemini-2.0-pro-vision",  # Model with vision capabilities
    description="Analyzes images and provides descriptions"
)

# Load an image (using PIL in this example)
image = Image.open("path/to/image.jpg")
image_bytes = io.BytesIO()
image.save(image_bytes, format="JPEG")
image_bytes = image_bytes.getvalue()

# Create a Part object for the image
image_part = types.Part.from_data(data=image_bytes, mime_type="image/jpeg")

# Run the agent with the image artifact
response = vision_agent.run(
    "What's in this image?",
    artifacts=[image_part]  # Pass as a list of artifacts
)

print(response.text)
```

### Artifact Service Implementations

ADK provides different implementations for the `ArtifactService`:

1. **InMemoryArtifactService**:
   - Stores artifacts in memory
   - Suitable for development and testing
   - Artifacts are lost when the application restarts

2. **FileArtifactService**:
   - Stores artifacts on the local file system
   - Maintains persistence across application restarts
   - Good for simple applications

3. **GcsArtifactService**:
   - Stores artifacts in Google Cloud Storage
   - Provides scalability and durability
   - Suitable for production applications

### Configuring an Agent with an Artifact Service

To configure an agent to use a specific artifact service:

```python
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService

# Create an artifact service
artifact_service = InMemoryArtifactService()

# Create an agent with the artifact service
agent = Agent(
    name="multimedia_agent",
    model="gemini-2.0-pro-vision",
    description="An agent that can work with images and other media",
    artifact_service=artifact_service
)
```

## Common Use Cases for Artifacts

### 1. Image Analysis

Allowing agents to process and analyze images:

```python
# User uploads an image for analysis
image_bytes = get_uploaded_image()
image_part = types.Part.from_data(data=image_bytes, mime_type="image/jpeg")

# Ask the agent to analyze the image
response = vision_agent.run(
    "What objects can you see in this image?",
    artifacts=[image_part]
)
```

### 2. Document Processing

Working with document files:

```python
# User provides a PDF document
pdf_bytes = get_pdf_bytes()
pdf_part = types.Part.from_data(data=pdf_bytes, mime_type="application/pdf")

# Ask the agent to summarize the document
response = document_agent.run(
    "Summarize the main points of this document",
    artifacts=[pdf_part]
)
```

### 3. Audio Analysis

Processing audio files:

```python
# User provides an audio clip
audio_bytes = get_audio_bytes()
audio_part = types.Part.from_data(data=audio_bytes, mime_type="audio/mp3")

# Ask the agent about the audio
response = audio_agent.run(
    "Transcribe this audio clip and identify the main speakers",
    artifacts=[audio_part]
)
```

### 4. Multi-turn Conversations with Media

Maintaining context across a conversation involving media:

```python
# First message with an image
image_bytes = get_image_bytes()
image_part = types.Part.from_data(data=image_bytes, mime_type="image/jpeg")
response1 = agent.run(
    "What's in this image?",
    artifacts=[image_part],
    session_id="user_session_456"
)

# Follow-up question about the same image
response2 = agent.run(
    "How many people are there?",
    session_id="user_session_456"  # Same session ID
)
```

## Best Practices

1. **Appropriate Storage**:
   - Choose the right artifact service implementation based on your application requirements
   - Consider durability, scalability, and access patterns

2. **Version Management**:
   - Decide on a strategy for handling multiple versions of the same artifact
   - Consider cleanup policies for old versions

3. **Size Considerations**:
   - Be mindful of artifact sizes, especially for memory-based implementations
   - Consider thumbnailing or compressing large media files

4. **Type Safety**:
   - Always include the correct MIME type with artifacts
   - Ensure the appropriate model is used that can handle the artifact type

5. **Error Handling**:
   - Implement proper error handling for cases where artifacts might be missing or corrupted
   - Provide graceful degradation when media can't be processed

By effectively utilizing Artifacts, your agents can handle rich multimedia content, enabling more sophisticated and natural interactions beyond text-only conversations.
