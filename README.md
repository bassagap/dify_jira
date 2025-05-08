# Jira to Dify RAG Integration

This project provides tools to fetch issues from Jira and ingest them into a Dify RAG (Retrieval-Augmented Generation) system.

## Development with GitHub Codespaces

This repository is configured for development with GitHub Codespaces. To get started:

1. Click the "Code" button in this repository
2. Select the "Codespaces" tab
3. Click "Create codespace on main"

The development container will be automatically configured with:
- Python 3.9
- All required dependencies
- Git
- Common Python development tools
- Docker and Docker Compose

### Environment Setup

1. Create a `.env` file in the project root with your credentials:
```env
# Jira credentials
JIRA_SERVER_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Dify credentials
DIFY_API_KEY=your-dify-api-key
DIFY_BASE_URL=https://api.dify.ai/v1  # Optional, defaults to this value
```

## Local Development

If you prefer to develop locally, you have two options:

### Option 1: Using Docker Compose

1. Make sure you have Docker and Docker Compose installed
2. Clone the repository:
```bash
git clone https://github.com/yourusername/dify-jira.git
cd dify-jira
```
3. Run the setup script:
```bash
chmod +x setup-dify.sh
./setup-dify.sh
```
The script will:
- Initialize git repository if needed
- Set up the Dify submodule
- Configure the environment
- Start the Docker containers

4. Access the container:
```bash
docker-compose exec app bash
```

### Option 2: Direct Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dify-jira.git
cd dify-jira
```
2. Run the setup script:
```bash
chmod +x setup-dify.sh
./setup-dify.sh
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # Install development dependencies
```
4. Set up pre-commit hooks:
```bash
pre-commit install
```

## Project Structure

- `.devcontainer/`: Configuration for GitHub Codespaces and VS Code Remote Containers
- `.pre-commit-config.yaml`: Pre-commit hooks for code quality
- `docker-compose.yaml`: Local development environment
- `pyproject.toml`: Project metadata and dependencies
- `requirements.txt`: Core dependencies
- `setup-dify.sh`: Setup script for Dify environment
- `jira_rag/`: Main package code
- `tests/`: Test files
- `dify/`: Dify submodule (RAG system)

## Usage

The project provides two main components:

1. `JiraClient`: For fetching issues from Jira
2. `DifyIntegration`: For ingesting issues into Dify RAG

Example usage:

```python
from jira_rag.jira_client import JiraClient
from jira_rag.dify_integration import DifyIntegration

# Initialize clients
jira_client = JiraClient()
dify = DifyIntegration()

# Fetch issues from Jira
jql_query = "project = YOUR_PROJECT_KEY AND created >= -30d"
issues = jira_client.get_issues(jql_query, max_results=50)

# Ingest issues into Dify RAG
response = dify.ingest_issues(issues)
```

## Features

- Fetch issues from Jira using JQL queries
- Format issues for RAG ingestion
- Ingest issues into Dify RAG
- Delete documents from Dify RAG
- Environment variable configuration
- Type hints and documentation
- Automated code quality checks with pre-commit hooks
- Docker-based development environment
- Automated setup script for Dify environment

## Requirements

- Python 3.9+
- Jira API access
- Dify API access 