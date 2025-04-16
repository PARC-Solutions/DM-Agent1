# Google Agent Development Kit (ADK) Documentation

The Google Agent Development Kit (ADK) is a powerful framework for building AI agents powered by Gemini and other large language models. This comprehensive documentation will guide you through installation, basic concepts, and advanced use cases.

## Table of Contents

### Getting Started

- [Installation](./1_GettingStarted/1_Installation.md) - Setting up the ADK and prerequisites
- [Quickstart](./1_GettingStarted/2_Quickstart.md) - Building your first agent in minutes
- [Quickstart with Streaming](./1_GettingStarted/3_QuickstartStreaming.md) - Using streaming for real-time responses
- [Tutorial](./1_GettingStarted/4_Tutorial.md) - Comprehensive tutorial for a complete agent application

### Core Concepts

- [Agents](./2_CoreConcepts/1_Agents.md) - Understanding the agent architecture
- [Tools](./2_CoreConcepts/2_Tools.md) - Extending agents with external capabilities
- [Sessions and Memory](./2_CoreConcepts/3_Sessions_and_Memory.md) - Managing conversation context
- [Artifacts](./2_CoreConcepts/4_Artifacts.md) - Working with binary data and media

### Tools

- [Tools Overview](./3_Tools/1_ToolsOverview.md) - Introduction to tools and capabilities
- [Function Tools](./3_Tools/2_FunctionTools.md) - Creating Python function tools
- [Third-Party Tools](./3_Tools/3_ThirdPartyTools.md) - Integrating LangChain, CrewAI, and other frameworks
- [Google Cloud Tools](./3_Tools/4_GoogleCloudTools.md) - Using Google Cloud services with ADK
- [MCP Tools](./3_Tools/5_MCPTools.md) - Model Context Protocol for extensibility
- [OpenAPI Tools](./3_Tools/6_OpenAPITools.md) - Generating tools from API specifications
- [Authentication](./3_Tools/7_Authentication.md) - Securing tool access

### Deployment

- [Deployment Options](./4_Deployment/1_DeploymentOptions.md) - Overview of deployment strategies
- [Vertex AI](./4_Deployment/2_VertexAI.md) - Deploying to Google Cloud Vertex AI
- [Cloud Run](./4_Deployment/3_CloudRun.md) - Containerized deployment with Cloud Run

### Advanced Features

- [Callbacks](./5_Advanced/1_Callbacks.md) - Customizing agent behavior with callbacks
- [Runtime](./5_Advanced/2_Runtime.md) - Understanding the ADK runtime and event system
- [Model Integration](./5_Advanced/3_ModelIntegration.md) - Working with different LLMs
- [Agent Patterns](./5_Advanced/4_AgentPatterns.md) - Advanced multi-agent architectures

### Testing and Examples

- [Testing Approaches](./6_Testing/1_TestingApproaches.md) - Strategies for testing your agents
- [Sample Agents](./6_Examples/1_SampleAgents.md) - Example agents demonstrating various capabilities

### Evaluation and Responsible AI

- [Evaluating Agents](./7_Evaluation/1_EvaluatingAgents.md) - Frameworks for assessing agent performance
- [Responsible Agents](./8_ResponsibleAI/1_ResponsibleAgents.md) - Building ethical and safe AI agents

### API Reference

- [API Reference](./ADK-API-Refference.md) - Comprehensive API documentation

## Quick Links

- **Installation:** `pip install google-adk`
- **Basic Agent:**
  ```python
  from google.adk.agents import Agent
  
  agent = Agent(
      name="my_first_agent",
      model="gemini-2.0-pro",
      instruction="You are a helpful assistant."
  )
  
  response = agent.run("Hello, who are you?")
  print(response.text)
  ```

## Using This Documentation

- **New to ADK?** Start with [Installation](./1_GettingStarted/1_Installation.md) and [Quickstart](./1_GettingStarted/2_Quickstart.md).
- **Building your first real agent?** Follow the complete [Tutorial](./1_GettingStarted/4_Tutorial.md).
- **Understanding core functionality?** Dive into the [Core Concepts](./2_CoreConcepts) section.
- **Adding capabilities?** Explore the various [Tools](./3_Tools) available.
- **Moving to production?** Check out the [Deployment](./4_Deployment) options.
- **Building sophisticated systems?** Master the [Advanced Features](./5_Advanced) section.
- **Testing and evaluation?** See the [Testing](./6_Testing) and [Evaluation](./7_Evaluation) sections.
- **Ensuring ethical usage?** Review the [Responsible AI](./8_ResponsibleAI) guidelines.

## Examples and Resources

- Example code can be found throughout the documentation
- Complete applications showcase real-world usage patterns
- Best practices are highlighted in relevant sections

The ADK empowers developers to create sophisticated, capable agents by combining the reasoning power of LLMs with the ability to perform real-world actions through tools and external integrations.
