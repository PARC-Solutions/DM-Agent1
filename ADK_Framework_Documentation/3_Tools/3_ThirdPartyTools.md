# Third-Party Tools

ADK is designed to be highly extensible, allowing you to seamlessly integrate tools from other AI Agent frameworks like LangChain and CrewAI. This interoperability is crucial because it allows for faster development time and enables you to reuse existing tools from these ecosystems.

## Using LangChain Tools

ADK provides the `LangchainTool` wrapper to integrate tools from the LangChain ecosystem into your agents.

### How to Integrate LangChain Tools

First, ensure you have the LangChain library installed:

```bash
pip install langchain
```

Then, you can wrap any LangChain tool for use with ADK:

```python
from google.adk.agents import Agent
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import tool

# Create a LangChain tool
@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information on a topic.
    
    Args:
        query: The topic to search for
    """
    # Implementation...
    return f"Wikipedia results for: {query}"

# Wrap it for use with ADK
wrapped_wiki_tool = LangchainTool(search_wikipedia)

# Create an agent with the wrapped tool
agent = Agent(
    name="research_assistant",
    model="gemini-2.0-flash",
    instruction="Help users find information by searching Wikipedia when needed.",
    tools=[wrapped_wiki_tool]
)
```

### Example: Web Search using LangChain's Tavily Tool

Tavily provides a search API that returns answers derived from real-time search results, intended for use by applications like AI agents:

```python
from google.adk.agents import Agent
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import TavilySearchResults

# Create the LangChain tool (requires Tavily API key)
tavily_search = TavilySearchResults(max_results=3, api_key="your-tavily-api-key")

# Wrap it for use with ADK
wrapped_tavily = LangchainTool(tavily_search)

# Create an agent with the wrapped tool
search_agent = Agent(
    name="web_search_agent",
    model="gemini-2.0-flash",
    instruction="Help users find information by searching the web when needed.",
    tools=[wrapped_tavily]
)

# Example usage
response = search_agent.run("What are the latest developments in quantum computing?")
print(response.text)
```

### Example: Document Processing with LangChain

LangChain provides powerful document processing tools that can be integrated with ADK:

```python
from google.adk.agents import Agent
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import tool
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

@tool
def extract_pdf_text(pdf_path: str) -> str:
    """Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        return "\n\n".join([chunk.page_content for chunk in chunks])
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

# Wrap the LangChain tool for ADK
pdf_tool = LangchainTool(extract_pdf_text)

# Create an agent with the PDF tool
document_agent = Agent(
    name="document_assistant",
    model="gemini-2.0-flash",
    instruction="Help users process and understand PDF documents.",
    tools=[pdf_tool]
)
```

## Using CrewAI Tools

Similar to LangChain, you can integrate tools from the CrewAI ecosystem using the `CrewaiTool` wrapper:

### How to Integrate CrewAI Tools

First, install the CrewAI library:

```bash
pip install crewai crewai_tools
```

Then, wrap CrewAI tools for use with ADK:

```python
from google.adk.agents import Agent
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import WebsiteSearchTool

# Create the CrewAI tool
website_search = WebsiteSearchTool()

# Wrap it for use with ADK
wrapped_website_search = CrewaiTool(website_search)

# Create an agent with the wrapped tool
website_agent = Agent(
    name="website_search_agent",
    model="gemini-2.0-flash",
    instruction="Search websites for specific information when users request it.",
    tools=[wrapped_website_search]
)
```

### Example: Finance Data with CrewAI Tools

CrewAI provides specialized tools for finance and other domains:

```python
from google.adk.agents import Agent
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import SECFilingsTool, StockPriceTool

# Create CrewAI tools
sec_filings_tool = SECFilingsTool()
stock_price_tool = StockPriceTool()

# Wrap them for use with ADK
wrapped_sec_tool = CrewaiTool(sec_filings_tool)
wrapped_stock_tool = CrewaiTool(stock_price_tool)

# Create a finance-focused agent
finance_agent = Agent(
    name="finance_advisor",
    model="gemini-2.0-flash",
    description="I provide financial insights and stock information",
    tools=[wrapped_sec_tool, wrapped_stock_tool]
)

# Example usage
response = finance_agent.run("What are the latest SEC filings for Tesla?")
print(response.text)
```

## Custom Tool Wrappers

You can also create custom wrappers for tools from other frameworks by implementing the appropriate adapter pattern:

```python
from google.adk.agents import BaseTool
from some_other_framework import ExternalTool

class CustomToolWrapper(BaseTool):
    """Wrapper for tools from another framework."""
    
    def __init__(self, external_tool):
        self.external_tool = external_tool
        
    def run(self, **kwargs):
        # Convert ADK format to the external tool's format
        external_result = self.external_tool.execute(**kwargs)
        
        # Convert the result back to ADK's expected format
        return {
            "status": "success",
            "result": external_result
        }
        
    def get_schema(self):
        # Define the schema based on the external tool
        return {
            "name": self.external_tool.name,
            "description": self.external_tool.description,
            "parameters": {
                # Map external tool parameters to ADK format
            }
        }

# Create the custom wrapper
external_tool = ExternalTool()
wrapped_tool = CustomToolWrapper(external_tool)

# Use it with an ADK agent
agent = Agent(
    name="custom_tool_agent",
    model="gemini-2.0-flash",
    tools=[wrapped_tool]
)
```

## Benefits of Third-Party Tool Integration

Using third-party tools with ADK offers several advantages:

1. **Expanding Capabilities**: Access specialized tools without having to build them from scratch.
2. **Ecosystem Compatibility**: Work with established AI agent ecosystems and their community-developed tools.
3. **Faster Development**: Reduce development time by leveraging existing implementations.
4. **Best-of-Breed Approach**: Select the best tools from different frameworks for your specific use case.

## Common Issues and Solutions

### Issue: Tool Signature Mismatch

When integrating third-party tools, you might encounter parameter signature mismatches between what the ADK agent expects and what the tool provides.

**Solution**: Create a thin adapter function:

```python
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import DuckDuckGoSearchTool

# Original tool has different parameter names
ddg_tool = DuckDuckGoSearchTool()

# Create an adapter function
def search_web(query: str) -> dict:
    """Search the web using DuckDuckGo.
    
    Args:
        query: The search query
        
    Returns:
        dict: Search results
    """
    # Adapt the parameter names
    results = ddg_tool.run({"query": query})
    return {"status": "success", "results": results}

# Create an agent with the adapted tool
agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    tools=[search_web]
)
```

### Issue: Handling Tool-Specific Authentication

Third-party tools often require their own authentication mechanisms.

**Solution**: Configure authentication during tool initialization:

```python
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import YouTubeSearchTool

# Configure authentication during initialization
youtube_tool = YouTubeSearchTool(api_key="your-youtube-api-key")
wrapped_youtube = LangchainTool(youtube_tool)

# Create an agent with the authenticated tool
agent = Agent(
    name="youtube_agent",
    model="gemini-2.0-flash",
    tools=[wrapped_youtube]
)
```

## Best Practices for Third-Party Tool Integration

1. **Test Thoroughly**: Third-party tools may change or have unexpected behaviors. Test them extensively before deploying.

2. **Handle Errors Gracefully**: Ensure that errors from third-party tools are properly caught and formatted for your agent.

3. **Keep Dependencies Updated**: Regularly update your third-party frameworks to get the latest features and security patches.

4. **Document Tool Behavior**: Ensure your team understands how the integrated tools work and what their limitations are.

5. **Consider Performance Impact**: Some third-party tools may introduce latency or have rate limits. Plan accordingly.

6. **Provide Clear Instructions**: When integrating third-party tools, update your agent's instructions to include guidance on when and how to use these tools.

## Conclusion

The ability to integrate tools from other frameworks is one of ADK's most powerful features. By leveraging existing ecosystems like LangChain and CrewAI, you can rapidly extend your agent's capabilities without reinventing the wheel.

Remember that third-party integrations may introduce dependencies and potential points of failure, so balance the convenience of integration with the need for reliability and maintenance.
