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

2. Set up Dify (optional, you have been already provided a running instance. Running Dify at Codespaces may be slow and not performant due to resources limitations):
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
uvicorn src.api.student_api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with Swagger documentation at `http://localhost:8000/docs`.

## API Endpoints

### Student API (`student_api.py`)
This is the main API for students to interact with Jira and Dify. It provides the following endpoints:

1. **Ingest from Jira**
   - **POST** `/ingest/jira`
   - Ingest issues directly from Jira
   - Parameters:
     - `project`: Jira project key (optional)
     - `jql`: JQL query to fetch issues (optional)
     - `max_results`: Maximum number of issues to fetch (default: 100)

2. **Ingest from JSON**
   - **POST** `/ingest/json`
   - Ingest issues from JSON files
   - Parameters:
     - `file_names`: List of JSON file names to ingest
     - `dataset_dir`: Directory containing the JSON files (default: "jira_rag/dataset")

3. **Test Connection**
   - **GET** `/test_connection`
   - Test connections to both Jira and Dify services

### Jira API (`jira_api.py`)
This API provides advanced Jira operations, mainly focused on test case management:

1. **Create Test Case**
   - **POST** `/create_test_case`
   - Create a single test case in Jira
   - Parameters:
     - `parent_key`: The issue this test case will be linked to
     - `project_key`: The project where the test case will be created

2. **Create Bulk Test Cases**
   - **POST** `/create_bulk_test_cases`
   - Create multiple test cases for a parent issue
   - Parameters:
     - `main_issue_key`: The parent issue key
     - `test_cases`: List of test cases to create
     - `link_type`: Type of link between issues (default: "Tests")
     - `labels`: Optional labels for the test cases
     - `component`: Optional component for the test cases
     - `reporter`: Optional reporter for the test cases

3. **Get Linked Test Cases**
   - **GET** `/get_linked_test_cases/{issue_key}`
   - Retrieve all test cases linked to a given issue
   - Parameters:
     - `issue_key`: The issue key to get linked test cases for
     - `link_type`: Type of link to filter by (default: "Tests")

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

