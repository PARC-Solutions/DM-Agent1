# Building Responsible AI Agents

When creating AI agents, it's essential to incorporate responsible AI practices from the beginning. This section outlines key principles and strategies for building agents that are ethical, safe, and aligned with user needs.

## Key Principles for Responsible Agent Development

1. **Safety**: Implement guardrails to prevent harmful outputs or actions
2. **Transparency**: Make your agent's capabilities and limitations clear to users
3. **Fairness**: Mitigate biases and ensure equitable treatment
4. **Privacy**: Handle user data responsibly and with consent
5. **Reliability**: Ensure consistent performance and error handling

## Implementation Strategies

### Using Callbacks for Safety Guardrails

Use the ADK callback system to implement safety checks before responses are sent to users:

```python
def safety_check(callback_context, llm_response):
    """Check for potentially harmful content in the model's response."""
    # Implement your safety checks here
    harmful_keywords = ["harmful", "illegal", "dangerous"]
    for keyword in harmful_keywords:
        if keyword in llm_response.text.lower():
            # Return a safe alternative response
            return LlmResponse(text="I'm unable to provide that information as it may not be appropriate or safe.")
    return llm_response  # Allow the original response if no issues found

agent = Agent(
    name="safe_agent",
    model="gemini-2.0-flash",
    instruction="Be helpful and safe",
    after_model_callback=safety_check
)
```

### Setting Clear User Expectations

Always be transparent about your agent's capabilities and limitations in its introduction:

```python
agent = Agent(
    name="support_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are a support agent that can help with basic account questions.
    Make it clear to users that:
    - You cannot access their personal account information
    - You cannot process payments
    - You may occasionally provide outdated information
    - Users should verify important information through official channels
    """
)
```

### Implementing Content Moderation

Add content moderation for inputs to prevent misuse:

```python
def moderate_input(callback_context, user_message):
    """Check user inputs for inappropriate content."""
    # Basic moderation check
    inappropriate_terms = ["offensive_term1", "offensive_term2"]
    
    if any(term in user_message.lower() for term in inappropriate_terms):
        return LlmResponse(
            text="I'm unable to respond to this message as it appears to contain inappropriate content."
        )
    
    # Proceed with normal processing if no issues found
    return None

agent = Agent(
    name="moderated_agent",
    model="gemini-2.0-flash",
    before_request_callback=moderate_input
)
```

### Handling Sensitive Information

Design your agent to recognize and properly handle sensitive information:

```python
def detect_pii(callback_context, llm_response):
    """Detect and redact personally identifiable information."""
    # Use a regex pattern to identify potential PII
    # This is a simplified example - production systems should use more robust methods
    import re
    
    # Pattern for things that look like credit card numbers
    cc_pattern = r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
    
    # Redact any matches
    redacted_text = re.sub(cc_pattern, "[REDACTED CREDIT CARD]", llm_response.text)
    
    # Apply other PII detection patterns as needed
    
    # Return the modified response
    if redacted_text != llm_response.text:
        llm_response.text = redacted_text
    
    return llm_response

agent = Agent(
    name="privacy_conscious_agent",
    model="gemini-2.0-flash",
    before_response_callback=detect_pii
)
```

### Adding Citations and References

Make your agent more reliable by having it provide citations when appropriate:

```python
from google.adk.agents import Agent
from google.adk.tools.rag import create_rag_tool

# Create RAG tool with citation capability
rag_tool = create_rag_tool(
    knowledge_base=your_documents,
    embedding_model="text-embedding-3-small",
    include_sources=True  # This enables source tracking
)

citation_agent = Agent(
    name="citation_agent",
    model="gemini-2.0-pro",
    instruction="""
    When answering questions, use the search_knowledge_base tool to find information.
    Always cite your sources by including the document name/URL after providing information.
    Format citations like this: [Source: document_name]
    """,
    tools=[rag_tool]
)
```

## Bias Mitigation Strategies

### Diverse Testing Data

Ensure your agent is tested with diverse inputs that represent a wide range of perspectives, cultures, and user needs:

```python
test_cases = [
    # Diverse set of test queries representing different backgrounds,
    # perspectives, topics, and complexity levels
    "How can I improve energy efficiency in my home?",
    "What are traditional cooking methods in West African cuisine?",
    "How do I set up accessibility features on my smartphone?",
    "Can you explain the basics of investment strategies for retirement?",
    # ... many more diverse examples
]

# Evaluate agent performance across all test cases
# Look for inconsistencies in response quality or approach
```

### Regular Bias Audits

Implement regular audits to identify and address potential biases:

```python
from google.adk.evaluation import evaluate_agent
from google.adk.evaluation.evaluators import BiasEvaluator

# Create a bias evaluator
bias_evaluator = BiasEvaluator(
    categories=["gender", "race", "age", "socioeconomic", "cultural"],
    model="gemini-2.0-pro"
)

# Run evaluation
results = evaluate_agent(
    agent=my_agent,
    test_cases=fairness_test_cases,
    evaluators=[bias_evaluator]
)

# Review results and make necessary adjustments
```

## User Feedback and Continuous Improvement

Implement mechanisms to collect and act on user feedback:

```python
def collect_feedback(agent_response, user_feedback):
    """Process user feedback for agent improvement."""
    
    # Log feedback for analysis
    log_entry = {
        "timestamp": time.time(),
        "agent_response": agent_response,
        "user_feedback": user_feedback,
        "session_id": current_session_id
    }
    
    # Store in feedback database
    feedback_db.insert(log_entry)
    
    # For critical issues, trigger alerts
    if user_feedback.get("rating", 5) < 2:
        send_alert_to_team(log_entry)
    
    # Return acknowledgment
    return {"status": "Feedback received", "id": log_entry["id"]}
```

## Documentation and Transparency

Maintain clear documentation about your agent's:

1. **Intended Use Cases**: What your agent is designed to do
2. **Limitations**: What your agent should not be used for
3. **Data Usage**: How user data is processed and stored
4. **Model Information**: What models power your agent and their known limitations
5. **Monitoring Practices**: How you ensure continued safety and performance

## Regulatory Compliance

Ensure your agent complies with relevant regulations:

- **Data Protection**: GDPR, CCPA, and other data privacy laws
- **Accessibility**: ADA, WCAG guidelines for accessible AI
- **Industry-Specific**: HIPAA for healthcare, FERPA for education, etc.

## Best Practices Checklist

When building responsible agents, use this checklist:

- [ ] Implement safety checks using callbacks
- [ ] Set clear expectations with users
- [ ] Add content moderation for inputs
- [ ] Handle sensitive information appropriately
- [ ] Test with diverse inputs and scenarios
- [ ] Conduct regular bias audits
- [ ] Collect and incorporate user feedback
- [ ] Maintain comprehensive documentation
- [ ] Ensure regulatory compliance
- [ ] Establish an incident response plan
- [ ] Create a mechanism for user feedback and appeals

By following these guidelines, you can build agents that are not only capable but also responsible, trustworthy, and aligned with human values and needs.
