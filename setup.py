from setuptools import setup, find_packages

setup(
    name="medical-billing-denial-agent",
    version="0.1.0",
    description="AI agent system for analyzing and resolving medical billing denials",
    author="Medical Billing Denial Agent Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "google-adk",
        "google-cloud-aiplatform>=1.36.0",
        "langchain>=0.0.267",
        "python-dotenv>=1.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "mypy>=1.4.1",
            "pylint>=2.17.0",
        ],
    },
)
