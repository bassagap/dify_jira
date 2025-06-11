# Jira RAG Integration

This project provides integration between Jira and Dify RAG (Retrieval-Augmented Generation) system, allowing you to ingest Jira issues and JSON files into a Dify knowledge base.

## Features

- Ingest issues directly from Jira
- Ingest issues from JSON files
- Support for both single JSON file and batch processing
- Flexible command-line interface
- Comprehensive logging

## Prerequisites

- Python 3.7+
- Jira account with API access
- Dify account with API access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Run the Dify setup script:
   ```bash
   ./setup-dify.sh
   ```
   This script will:
   - Check for required tools (git, Docker, Docker Compose)
   - Initialize git repository if needed
   - Set up the Dify submodule from https://github.com/langgenius/dify.git
   - Configure the environment
   - Start the Docker containers
   - Open Dify in your browser at http://localhost/install

3. Complete Dify Installation:
   - When the browser opens, follow the Dify installation wizard
   - Create your admin account
   - Note down your API keys from the Dify dashboard

### 2. Environment Configuration

1. Edit `.env.example` file and fill in your credentials:

   ```env
   # Jira credentials
   JIRA_SERVER_URL=https://your-domain.atlassian.net   
   JIRA_EMAIL=your-email@example.com 
   JIRA_API_TOKEN=your-api-token 

   # Dify credentials
   DIFY_DATASET_API_KEY=your-dify-api-key                      
   DIFY_BASE_URL=https://api.dify.ai/v1         # Optional, defaults to this value
   ```

   To get your credentials:
   - **Jira API Token**: 
     1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
     2. Click "Create API token"
     3. Give it a name and copy the token
   
   - **Dify API Key**:
     1. Log in to your Dify dashboard
     2. Go to API Keys section
     3. Create a new API key or use an existing one


2. Copy the existing `.env.example` file to create your `.env` file:
   ```bash
   cp .env.example .env
   ```


### 3. Running the Example

Run the example script:
```bash
python example.py --json full_quidditch_jira_issues.json
```

Additional Options:
- `--dataset-dir`: Specify a different dataset directory (default: 'jira_rag/dataset')

## JSON File Format

The JSON files should follow this structure:
```json
[
  {
    "id": "issue-id",
    "key": "PROJECT-123",
    "fields": {
      "summary": "Issue summary",
      "description": "Issue description",
      "issuetype": {
        "name": "Story"
      },
      "status": {
        "name": "To Do"
      },
      "project": {
        "key": "PROJECT",
        "name": "Project Name"
      },
      "created": "2023-01-01T00:00:00",
      "updated": "2023-01-01T00:00:00"
    }
  }
]
```

## Project Structure

```
.
├── jira_rag/
│   ├── __init__.py
│   ├── jira_client.py
│   └── dify_integration.py
├── dataset/
│   └── *.json
├── example.py
├── requirements.txt
└── README.md
```

## Logging

The script provides detailed logging of its operations. Logs include:
- Environment variable loading status
- Jira connection status
- File ingestion progress
- Success/failure of operations

## Error Handling

The script includes comprehensive error handling for:
- Missing environment variables
- Invalid JSON files
- Jira connection issues
- Dify API errors

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Your chosen license]

