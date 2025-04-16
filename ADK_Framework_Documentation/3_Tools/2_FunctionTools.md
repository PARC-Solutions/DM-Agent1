# Function Tools

Function tools are the most basic and flexible way to extend agent capabilities in ADK. They allow you to define custom functionality as simple Python functions that agents can invoke when needed.

## Basic Function Tool

At its core, a function tool is just a Python function with a descriptive docstring and proper type hints:

```python
def get_current_time(timezone: str = "UTC") -> dict:
    """Get the current time in the specified timezone.
    
    Args:
        timezone: A valid timezone string (e.g., 'UTC', 'America/New_York')
            Default is 'UTC'.
            
    Returns:
        dict: A dictionary containing the current time information
    """
    from datetime import datetime
    import pytz
    
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {
            "status": "success",
            "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": timezone
        }
    except pytz.exceptions.UnknownTimeZoneError:
        return {
            "status": "error",
            "message": f"Unknown timezone: {timezone}",
            "valid_examples": ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
        }
```

## Providing Function Tools to an Agent

To make a function tool available to an agent, simply include it in the `tools` parameter when creating the agent:

```python
from google.adk.agents import Agent

# Create an agent with a function tool
agent = Agent(
    name="time_assistant",
    model="gemini-2.0-flash",
    description="An assistant that can tell you the current time in different timezones",
    tools=[get_current_time]  # Pass the function directly
)

# Use the agent with the tool
response = agent.run("What time is it in Tokyo?")
print(response.text)
```

## Function Tool Requirements

To create effective function tools, adhere to these requirements:

### 1. Proper Type Hints

Type hints help the LLM understand what arguments to provide and what to expect in return:

```python
def calculate_mortgage(
    principal: float,
    interest_rate: float,
    term_years: int
) -> dict:
    """Calculate mortgage details."""
    # Implementation...
```

The most common return type is `dict`, which allows you to return structured data to the agent.

### 2. Descriptive Docstrings

Comprehensive docstrings are crucial as they tell the agent when and how to use the tool:

```python
def search_product_catalog(
    query: str,
    category: str = None,
    max_results: int = 5
) -> dict:
    """Search the product catalog for items matching the query.
    
    This tool allows searching through the company's product database
    to find items that match the search terms. Results can be filtered
    by category and limited to a specific number.
    
    Args:
        query: Search terms to look for in product names and descriptions
        category: Optional category to filter results (e.g., "Electronics", "Clothing")
        max_results: Maximum number of results to return (default: 5, max: 20)
        
    Returns:
        dict: Contains 'status' and either 'products' (list of matching products)
            or 'error_message' if an error occurred
    """
    # Implementation...
```

### 3. Error Handling

Tools should handle errors gracefully and return structured error information rather than raising exceptions:

```python
def fetch_stock_data(ticker: str) -> dict:
    """Fetch current stock information for a given ticker."""
    try:
        # Code to fetch stock data...
        if not data:
            return {
                "status": "error",
                "error_type": "not_found",
                "message": f"No data found for ticker: {ticker}"
            }
        return {
            "status": "success",
            "data": data
        }
    except RateLimitError:
        return {
            "status": "error",
            "error_type": "rate_limit",
            "message": "API rate limit exceeded. Please try again later."
        }
    except ConnectionError:
        return {
            "status": "error",
            "error_type": "connection_error",
            "message": "Could not connect to stock data service."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "unknown",
            "message": f"An unexpected error occurred: {str(e)}"
        }
```

## Advanced Function Tools

### Long-Running Functions

For operations that take a significant amount of time, you can implement asynchronous tools:

```python
import asyncio
from google.adk.agents import Agent
from google.adk.tools import register_async_tool

# Define an asynchronous function
async def fetch_large_dataset(query: str) -> dict:
    """Fetch a large dataset based on the query.
    
    This operation may take some time to complete.
    
    Args:
        query: The search query for the dataset
        
    Returns:
        dict: The dataset results
    """
    # Simulate a long-running task
    await asyncio.sleep(5)  # In real usage, this would be an actual async API call
    return {
        "status": "success",
        "results": [{"id": 1, "data": "Sample result 1"}, {"id": 2, "data": "Sample result 2"}]
    }

# Register the async function as a tool
fetch_dataset_tool = register_async_tool(fetch_large_dataset)

# Create an agent with the async tool
agent = Agent(
    name="data_assistant",
    model="gemini-2.0-flash",
    description="An assistant that can fetch large datasets",
    tools=[fetch_dataset_tool]
)
```

### Function Parameters with Complex Types

For function parameters with complex types, use type hints and provide clear examples in the docstring:

```python
from typing import List, Dict, Union

def analyze_financial_data(
    transactions: List[Dict[str, Union[str, float, int]]],
    metrics: List[str] = ["total", "average", "max", "min"]
) -> dict:
    """Analyze a list of financial transactions.
    
    Args:
        transactions: A list of transaction dictionaries, where each dictionary has:
            - 'date': String in 'YYYY-MM-DD' format
            - 'amount': Numeric value of the transaction
            - 'category': String category name
            - 'description': Optional string description
            
            Example:
            [
                {"date": "2023-01-15", "amount": 120.50, "category": "Groceries"},
                {"date": "2023-01-16", "amount": 35.00, "category": "Transportation"}
            ]
            
        metrics: List of metrics to calculate, options:
            - "total": Sum of all transactions
            - "average": Average transaction amount
            - "max": Maximum transaction amount
            - "min": Minimum transaction amount
            Default: All metrics
            
    Returns:
        dict: Analysis results with calculated metrics
    """
    # Implementation...
```

### Function with Class Methods

You can also use class methods as tools:

```python
class DatabaseManager:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        # Set up database connection
        
    def query_database(self, query: str) -> dict:
        """Execute a query against the database.
        
        Args:
            query: SQL query to execute
            
        Returns:
            dict: Query results or error information
        """
        try:
            # Execute query and fetch results
            return {"status": "success", "results": [...]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create an instance
db_manager = DatabaseManager("connection_string_here")

# Create an agent with the method as a tool
agent = Agent(
    name="database_assistant",
    model="gemini-2.0-flash",
    description="An assistant that can query the database",
    tools=[db_manager.query_database]  # Use the method as a tool
)
```

## Best Practices for Function Tools

### 1. Keep Tools Focused

Design each tool to do one thing well with a clear purpose:

```python
# Good: Focused tools with clear purposes
def get_weather_forecast(location: str, days: int = 3) -> dict:
    """Get weather forecast for a location."""
    # Implementation...

def get_air_quality_index(location: str) -> dict:
    """Get current air quality index for a location."""
    # Implementation...

# Bad: Tool tries to do too much
def get_location_data(location: str, data_type: str) -> dict:
    """Get various data for a location based on data_type."""
    if data_type == "weather":
        # Implementation...
    elif data_type == "air_quality":
        # Implementation...
    elif data_type == "population":
        # Implementation...
    # Many more conditions...
```

### 2. Provide Sensible Defaults

Use default parameter values where appropriate:

```python
def search_news(
    query: str,
    days: int = 7,
    language: str = "en",
    max_results: int = 10
) -> dict:
    """Search recent news articles."""
    # Implementation...
```

### 3. Include Input Validation

Validate inputs to catch problems early and return helpful error messages:

```python
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email to the specified recipient."""
    # Input validation
    if not to or '@' not in to:
        return {
            "status": "error",
            "message": "Invalid email address. Please provide a valid 'to' email."
        }
    
    if not subject:
        return {
            "status": "error",
            "message": "Subject cannot be empty."
        }
    
    if not body:
        return {
            "status": "error",
            "message": "Email body cannot be empty."
        }
    
    # If validation passes, proceed with sending
    # Implementation...
```

### 4. Maintain Consistent Return Structure

Use a consistent structure for your return values:

```python
# Sample return structure template

# For success:
return {
    "status": "success",
    "data": {
        # The actual result data...
    },
    "message": "Optional success message"  # Optional
}

# For errors:
return {
    "status": "error",
    "error_code": "SPECIFIC_ERROR_CODE",  # Optional
    "message": "Description of what went wrong",
    "suggestions": ["Possible fix 1", "Possible fix 2"]  # Optional
}
```

### 5. Document Usage Examples

Include examples of how to use the tool in the docstring:

```python
def translate_text(text: str, target_language: str) -> dict:
    """Translate text to the specified language.
    
    Args:
        text: The text to translate
        target_language: The language code to translate to (e.g., 'es' for Spanish)
        
    Returns:
        dict: Translation results or error message
        
    Examples:
        translate_text("Hello world", "es") -> Returns Spanish translation
        translate_text("How are you?", "fr") -> Returns French translation
    """
    # Implementation...
```

## Examples of Common Function Tools

### Web Search Tool

```python
def web_search(query: str, num_results: int = 5) -> dict:
    """Search the web for information.
    
    Args:
        query: Search query string
        num_results: Number of results to return (1-10)
        
    Returns:
        dict: Search results with URLs and snippets
    """
    # Implementation using a search API
    # ...
    return {
        "status": "success",
        "results": [
            {"title": "Result 1", "url": "https://example.com/1", "snippet": "..."},
            {"title": "Result 2", "url": "https://example.com/2", "snippet": "..."},
            # More results...
        ]
    }
```

### Data Processing Tool

```python
from typing import List, Dict, Any

def analyze_data(
    data: List[Dict[str, Any]],
    analysis_type: str = "summary"
) -> dict:
    """Analyze a dataset and return statistics.
    
    Args:
        data: List of data points as dictionaries
        analysis_type: Type of analysis to perform:
            - "summary": Basic summary statistics
            - "correlation": Correlation between variables
            - "outliers": Detect outliers in the data
            
    Returns:
        dict: Analysis results
    """
    # Implementation...
```

### API Integration Tool

```python
def fetch_github_repository_info(repo_owner: str, repo_name: str) -> dict:
    """Fetch information about a GitHub repository.
    
    Args:
        repo_owner: The GitHub username or organization that owns the repository
        repo_name: The name of the repository
        
    Returns:
        dict: Repository information including stars, forks, open issues, etc.
    """
    import requests
    
    try:
        response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}")
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "data": {
                    "name": data["name"],
                    "description": data["description"],
                    "stars": data["stargazers_count"],
                    "forks": data["forks_count"],
                    "open_issues": data["open_issues_count"],
                    "language": data["language"],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"]
                }
            }
        elif response.status_code == 404:
            return {
                "status": "error",
                "error_code": "REPO_NOT_FOUND",
                "message": f"Repository {repo_owner}/{repo_name} not found"
            }
        else:
            return {
                "status": "error",
                "error_code": "API_ERROR",
                "message": f"GitHub API returned status code {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_code": "REQUEST_FAILED",
            "message": f"Failed to fetch repository info: {str(e)}"
        }
