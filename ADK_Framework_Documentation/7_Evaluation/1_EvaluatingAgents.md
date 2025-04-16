# Evaluating Agents

## Why Evaluate Agents

In traditional software development, unit tests and integration tests provide confidence that code functions as expected and remains stable through changes. These tests provide a clear "pass/fail" signal, guiding further development. However, LLM agents introduce a level of variability that makes traditional testing approaches insufficient.

Due to the probabilistic nature of models, deterministic "pass/fail" assertions are often unsuitable for evaluating agent performance. Instead, we need qualitative evaluations of both the final output and the agent's trajectory - the sequence of steps taken to reach the solution. This involves assessing the quality of the agent's decisions, its reasoning process, and the final result.

This may seem like a lot of extra work to set up, but the investment of automating evaluations pays off quickly. If you intend to progress beyond prototype, this is a highly recommended best practice.

## Preparing for Agent Evaluations

Before automating agent evaluations, define clear objectives and success criteria:

* **Identify Critical Tasks**: What are the essential tasks your agent must accomplish?
* **Choose Relevant Metrics**: What metrics will you track to measure performance?

These considerations will guide the creation of evaluation scenarios and enable effective monitoring of agent behavior in real-world deployments.

## What to Evaluate?

To bridge the gap between a proof-of-concept and a production-ready AI agent, a robust and automated evaluation framework is essential. Unlike evaluating generative models, where the focus is primarily on the final output, agent evaluation requires a deeper understanding of the decision-making process. Agent evaluation can be broken down into two components:

1. **Evaluating Trajectory and Tool Use**: Analyzing the steps an agent takes to reach a solution, including its choice of tools, strategies, and the efficiency of its approach.

2. **Evaluating the Final Response**: Assessing the quality, relevance, and correctness of the agent's final output.

## Trajectory Evaluation

The trajectory is just a list of steps the agent took before it returned to the user. We can compare that against the list of steps we expect the agent to have taken.

Before responding to a user, an agent typically performs a series of actions, which we refer to as a 'trajectory.' It might compare the user input with session history to disambiguate a term, or lookup a policy document, search a knowledge base or invoke an API to save a ticket. We call this a 'trajectory' of actions. Evaluating an agent's performance requires comparing its actual trajectory to an expected, or ideal, one. This comparison can reveal errors and inefficiencies in the agent's process. The expected trajectory represents the ground truth -- the list of steps we anticipate the agent should take.

For example:

```
// Trajectory evaluation will compare
expected_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
actual_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
```

Several ground-truth-based trajectory evaluations exist:

1. **Exact match**: Requires a perfect match to the ideal trajectory.
2. **In-order match**: Requires the correct actions in the correct order, allows for extra actions.
3. **Any-order match**: Requires the correct actions in any order, allows for extra actions.
4. **Precision**: Measures the relevance/correctness of predicted actions.
5. **Recall**: Measures how many essential actions are captured in the prediction.
6. **Single-tool use**: Checks for the inclusion of a specific action.

## Response Evaluation

While trajectory evaluation focuses on the process, response evaluation assesses the final output. This involves:

1. **Correctness**: Is the information provided accurate and factual?
2. **Completeness**: Does the response address all aspects of the user's query?
3. **Relevance**: Is the response directly related to what the user asked?
4. **Helpfulness**: Does the response actually solve the user's problem?
5. **Format**: Is the response structured appropriately (e.g., code blocks for code, bullet points for lists)?

## Implementing Agent Evaluation

ADK provides tools for implementing automated agent evaluations:

```python
from google.adk.evaluation import evaluate_agent
from google.adk.evaluation.evaluators import ExactMatchEvaluator

# Define test cases
test_cases = [
    {
        "input": "What's the weather in New York?",
        "expected_output": "The weather in New York is sunny with a temperature of 25 degrees Celsius.",
        "expected_trajectory": ["determine_intent", "get_weather", "format_response"]
    },
    {
        "input": "Tell me about quantum computing",
        "expected_output": "Quantum computing is a type of computing that uses quantum bits or qubits...",
        "expected_trajectory": ["determine_intent", "search_knowledge_base", "format_response"]
    }
]

# Run evaluation
results = evaluate_agent(
    agent=my_agent,
    test_cases=test_cases,
    evaluators=[ExactMatchEvaluator()]
)

# Analyze results
print(f"Overall success rate: {results['success_rate']:.2f}")
for case_result in results['case_results']:
    print(f"Case: {case_result['input']}")
    print(f"  Success: {case_result['success']}")
    if 'error' in case_result:
        print(f"  Error: {case_result['error']}")
```

## Advanced Evaluation Techniques

### LLM-based Evaluation

For more nuanced evaluation, you can use LLM-based evaluators that assess responses based on multiple criteria:

```python
from google.adk.evaluation.evaluators import LlmEvaluator

llm_evaluator = LlmEvaluator(
    model="gemini-2.0-pro",
    criteria=[
        "Accuracy: Is the information factually correct?",
        "Completeness: Does the response address all aspects of the query?",
        "Clarity: Is the response easy to understand?",
        "Helpfulness: Does the response provide actionable information?"
    ],
    scoring_scale="1-5"
)

results = evaluate_agent(
    agent=my_agent,
    test_cases=test_cases,
    evaluators=[llm_evaluator]
)
```

### Human-in-the-Loop Evaluation

For critical applications, combine automated evaluation with human review:

```python
from google.adk.evaluation.evaluators import HumanReviewEvaluator

# This evaluator will prompt for human input during evaluation
human_evaluator = HumanReviewEvaluator(
    prompt_template="Please rate this response (1-5):\nQuery: {input}\nResponse: {output}\nRating: "
)

results = evaluate_agent(
    agent=my_agent,
    test_cases=sample_cases,
    evaluators=[human_evaluator]
)
```

## Continuous Evaluation in Production

For production systems, implement continuous evaluation:

1. **Sample Live Traffic**: Randomly sample a percentage of live user interactions.
2. **Shadow Testing**: Test new agent versions against live traffic in parallel with the production system.
3. **A/B Testing**: Compare different agent versions with real users.
4. **Monitoring Key Metrics**: Track user satisfaction, task completion rates, and other KPIs.

## Best Practices for Agent Evaluation

1. **Start Early**: Begin developing evaluation scenarios during agent design, not after deployment.
2. **Diverse Test Cases**: Include edge cases, common queries, and potential failure modes.
3. **Combine Methods**: Use both automatic and human evaluation for a complete picture.
4. **Iterate**: Use evaluation results to improve your agent, then evaluate again.
5. **Domain-Specific Metrics**: Develop evaluation criteria specific to your agent's domain and purpose.
6. **Version Control**: Keep track of agent versions and their performance metrics to measure progress.

By implementing a robust evaluation framework, you can ensure your agents are reliable, effective, and continuously improving.
