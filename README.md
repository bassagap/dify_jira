# Jira-Dify Integration API

This API service integrates Jira with Dify, allowing you to ingest Jira issues into Dify's knowledge base for enhanced search and retrieval capabilities.

## Features

- Ingest Jira issues directly from Jira into Dify
- Ingest Jira issues from JSON files
- Configure metadata for better search and filtering
- Swagger documentation for easy API exploration

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Jira account with API access
- Dify instance (can be set up using the provided setup script)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Set up Dify (if not already set up):
```bash
./setup-dify.sh
```

3. Create a `.env` file in the root directory with the following variables:
```env
# Jira Configuration
JIRA_SERVER_URL=https://your-jira-server.com
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Dify Configuration
DIFY_BASE_URL=http://localhost/v1
DIFY_DATASET_API_KEY=your-dify-api-key
DIFY_DATASET_ID=your-dataset-id  # Optional, will be created if not provided
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the API server:
```bash
uvicorn jira_api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with Swagger documentation at `http://localhost:8000/docs`.

## API Endpoints

### 1. Ingest Jira Issues

**POST** `/ingest/jira`
- Ingest issues directly from Jira
- Query parameters:
  - `jql`: JQL query to fetch issues
  - `max_results`: Maximum number of issues to fetch (default: 100)

### 2. Ingest from JSON

**POST** `/ingest/json`
- Ingest issues from a JSON file
- Body: JSON file path relative to the `dataset` directory

## Metadata Configuration

The API supports the following metadata options:

1. **Built-in Metadata**
   - Automatically enabled for all documents
   - Includes creation date, update date, and document type

2. **Custom Metadata**
   - `issue_key`: The Jira issue key (e.g., "PROJ-123")
   - Additional metadata can be added through the Dify interface

## Architecture

The project follows a clean architecture with the following components:

- `jira_api.py`: FastAPI application with endpoints
- `jira_rag/jira_client.py`: Jira client for issue operations
- `jira_rag/dify_integration.py`: Dify integration for document ingestion

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]

