# Jira to Dify RAG Integration

This project provides tools to fetch issues from Jira and ingest them into a Dify RAG (Retrieval-Augmented Generation) system.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your credentials:
```env
# Jira credentials
JIRA_SERVER_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Dify credentials
DIFY_API_KEY=your-dify-api-key
DIFY_BASE_URL=https://api.dify.ai/v1  # Optional, defaults to this value
```

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

## Requirements

- Python 3.7+
- Jira API access
- Dify API access 