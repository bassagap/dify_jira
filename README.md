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

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following variables:
```env
JIRA_SERVER_URL=https://your-jira-server.com
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
DIFY_DATASET_API_KEY=your-dify-api-key
DIFY_BASE_URL=http://localhost/v1  # or your Dify server URL
```

## Usage

The script provides three main ways to ingest data:

### 1. Ingest from Jira

To ingest issues directly from Jira:
```bash
python example.py --jira --project QAREF
```

Options:
- `--project`: Specify the Jira project key (default: QAREF)

### 2. Ingest All JSON Files

To ingest all JSON files from the dataset directory:
```bash
python example.py --all-json
```

### 3. Ingest Specific JSON File

To ingest a specific JSON file:
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

