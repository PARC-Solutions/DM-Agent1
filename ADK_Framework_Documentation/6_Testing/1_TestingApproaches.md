# Testing Your Agents

Proper testing is essential for building reliable and robust agent applications. This guide covers approaches for testing your ADK agents, from basic unit tests to comprehensive integration testing.

## Unit Testing Your Agents

Unit tests verify that individual components of your agent system work correctly in isolation. These tests are fast to run and help catch issues early in the development process.

### Testing Tools and Functions

Start by testing the individual tools your agent uses. Here's an example of testing a weather function tool:

```python
import unittest

# Import the function to test
from your_agent_package.tools import get_weather

class TestWeatherTool(unittest.TestCase):
    def test_get_weather_success(self):
        result = get_weather("New York")
        self.assertEqual(result["status"], "success")
        self.assertIn("temperature", result["report"])
    
    def test_get_weather_failure(self):
        result = get_weather("NonexistentCity")
        self.assertEqual(result["status"], "error")
        self.assertIn("error_message", result)

if __name__ == "__main__":
    unittest.main()
```

### Testing Agent Behavior with Mocks

For testing the agent itself, you'll often want to mock the LLM and tool calls to control the testing environment:

```python
import unittest
from unittest.mock import patch, MagicMock
from google.adk.agents import Agent

class TestMyAgent(unittest.TestCase):
    @patch("google.adk.agents.LlmAgent._call_llm")
    def test_agent_response(self, mock_call_llm):
        # Setup the mock to return a predetermined response
        mock_response = MagicMock()
        mock_response.text = "The weather in New York is sunny."
        mock_call_llm.return_value = mock_response
        
        # Create the agent with mocked tools
        mock_weather_tool = MagicMock(return_value={"status": "success", "report": "Sunny, 25°C"})
        
        agent = Agent(
            name="test_agent",
            model="gemini-2.0-flash",
            tools=[mock_weather_tool]
        )
        
        # Test the agent's response
        response = agent.run("What's the weather in New York?")
        self.assertIn("sunny", response.text.lower())

if __name__ == "__main__":
    unittest.main()
```

## Integration Testing

Integration tests verify that the different components of your system work together correctly. For ADK agents, this typically means testing the interaction between:

1. The agent and its tools
2. Multiple agents in a workflow
3. The agent and external systems (like databases or APIs)

```python
import unittest
from google.adk.agents import Agent, SequentialAgent

class TestCustomerSupportSystem(unittest.TestCase):
    def setUp(self):
        # Create the actual components we want to test together
        self.router_agent = create_router_agent()
        self.support_agent = create_support_agent()
        
        # Combine them into a workflow
        self.support_system = SequentialAgent(
            name="test_support_system",
            agents=[self.router_agent, self.support_agent]
        )
    
    def test_end_to_end_pricing_query(self):
        # Test a complete customer journey
        response = self.support_system.run("How much does the premium phone cost?")
        
        # Verify the response contains pricing information
        self.assertIn("$999", response.text)
        
        # You can also inspect the session state or other outputs
        # to verify the correct path was taken through the system

if __name__ == "__main__":
    unittest.main()
```

## Testing with Agent Evaluation Framework

For more comprehensive testing, ADK's evaluation framework can be used to test both the agent's final responses and its trajectory (the sequence of actions taken):

```python
from google.adk.evaluation import evaluate_agent, TrajectoryEvaluator

# Define test cases
test_cases = [
    {
        "input": "What's the weather in New York?",
        "expected_output": {"contains": ["New York", "temperature"]},
        "expected_trajectory": ["determine_intent", "get_weather", "format_response"]
    },
    {
        "input": "What time is it in London?",
        "expected_output": {"contains": ["London", "time"]},
        "expected_trajectory": ["determine_intent", "get_current_time", "format_response"]
    }
]

# Create custom evaluators if needed
class CustomEvaluator(TrajectoryEvaluator):
    def evaluate(self, actual_trajectory, expected_trajectory):
        # Custom evaluation logic
        return {"score": 0.95, "details": "All critical steps were performed correctly"}

# Run the evaluation
results = evaluate_agent(
    agent=my_agent,
    test_cases=test_cases,
    evaluators=[CustomEvaluator()]
)

# Print results
print(f"Overall score: {results['overall_score']}")
for case_result in results['case_results']:
    print(f"Case: {case_result['input']}")
    print(f"Success: {case_result['success']}")
    print(f"Score: {case_result['score']}")
```

## Best Practices for Testing ADK Agents

1. **Test at different levels**: Unit test individual tools, integration test agent workflows, and end-to-end test complete user journeys.

2. **Mock external dependencies**: Use mocks for LLMs, APIs, and databases to create predictable, repeatable tests.

3. **Test edge cases**: Include tests for error handling, unexpected inputs, and boundary conditions.

4. **Automate tests**: Set up CI/CD pipelines to run tests automatically on code changes.

5. **Test for regressions**: When you fix a bug, add a test to ensure it doesn't reappear in the future.

6. **Consider performance**: Include tests for response time, especially for agents with complex workflows or large knowledge bases.

7. **Test across environments**: Ensure your agent works correctly in all deployment environments (development, staging, production).
