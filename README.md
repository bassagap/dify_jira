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

## Complete Setup Process

### 1. Initial Setup

1. Make the setup script executable:
   ```bash
   chmod +x setup-dify.sh
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
   - Start the Dify Docker containers
   - Start the jira-api Docker container
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
   - **Jira API Token**(for jira access): 
     1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
     2. Click "Create API token"
     3. Give it a name and copy the token
   
   - **Dify dataset API Key**(for data upload):
     1. Log in to your Dify dashboard
     2. Go to API Keys section in the Knowledge Base field
     3. Create a new API key or use an existing one


2. Copy the existing `.env.example` file to create your `.env` file:
   ```bash
   cp .env.example .env
   ```


### 3. Running the Example

Run the example script:
```bash
python example.py
```

The script will:
- Connect to your Jira instance using the provided credentials
- Fetch issues from the QAREF project
- Create a new dataset in Dify if one doesn't exist
- Ingest the Jira issues into Dify's knowledge base
- Log the progress and any errors that occur

