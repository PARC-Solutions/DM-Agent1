# Medical Billing Denial Agent

This repository contains an AI agent system built using Google's Agent Development Kit (ADK) that helps healthcare providers analyze and resolve medical billing denials. The system processes denial information from various sources, identifies the root causes, and provides actionable remediation steps.

## What's Included

- **Multi-Agent System**: A coordinated set of specialized agents for denial management
- **Knowledge Bases**: Comprehensive databases of CARC/RARC codes and resolution strategies
- **Document Processing Tools**: Tools to extract information from CMS-1500 forms and EOBs
- **ADK Framework Documentation**: Comprehensive documentation on the Google ADK framework
- **ADK Python Library**: Included as a git submodule, providing the official Google ADK implementation

## Getting Started

1. Clone this repository:
   ```
   git clone --recursive https://github.com/yourusername/medical-billing-denial-agent.git
   ```

2. Set up your environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

4. Run the development server:
   ```
   python run.py
   ```

5. For more detailed setup instructions, see the [Development Setup Guide](docs/setup.md)

## System Architecture

The Medical Billing Denial Agent uses a multi-agent architecture:

1. **Main Denial Assistant Agent**: Coordinates the conversation flow with users
2. **Denial Classifier Agent**: Interprets CARC/RARC codes to identify denial reasons
3. **Claims Analyzer Agent**: Extracts and analyzes information from claim documents
4. **Remediation Advisor Agent**: Provides actionable steps for denial resolution

The system utilizes knowledge bases for:
- CARC/RARC codes and descriptions
- Resolution strategies for different denial types
- "Don't Bill Together" code compatibility rules

See the [Architecture Documentation](docs/architecture.md) for more details.

## Development

- **Project Roadmap**: See [Roadmap](Medical_Billing_Denial_Agent_Roadmap.md) for implementation timeline
- **Project Plan**: See [Project Plan](Medical_Billing_Denial_Agent_Project_Plan.md) for technical details
- **Testing**: Run tests using `pytest tests/`
- **Code Style**: This project follows PEP 8 guidelines, enforced with Black and Pylint

## Compliance and Security

This system is designed with HIPAA compliance in mind:
- No PHI (Protected Health Information) is stored permanently
- All data is encrypted in transit and at rest
- Comprehensive audit logging
- Access controls and authentication

For more information, see the [Security Documentation](docs/security.md)

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file in the ADK repository for details.
