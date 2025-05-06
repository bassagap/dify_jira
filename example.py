from jira_rag.jira_client import JiraClient
from jira_rag.dify_integration import DifyIntegration
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_env_vars():
    """Check if all required environment variables are set."""
    required_vars = ['JIRA_SERVER_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.error(f"Missing required environment variable: {var}")
    
    if missing_vars:
        env_path = Path('.env')
        if not env_path.exists():
            logger.error(f"No .env file found at {env_path.absolute()}")
            logger.error("Please create a .env file with the following variables:")
            logger.error("JIRA_SERVER_URL=https://your-jira-server.com")
            logger.error("JIRA_EMAIL=your-email@example.com")
            logger.error("JIRA_API_TOKEN=your-api-token")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Check for required environment variables
        check_env_vars()
        
        # Print environment variables (without sensitive data)
        logger.info("Environment variables loaded successfully")
        logger.info(f"JIRA_SERVER_URL: {os.getenv('JIRA_SERVER_URL')}")
        logger.info(f"JIRA_EMAIL: {os.getenv('JIRA_EMAIL')}")
        logger.info("JIRA_API_TOKEN: [REDACTED]")
        logger.info(f"NO_PROXY: {os.getenv('NO_PROXY')}")
        
        # Initialize Jira client
        logger.info("Initializing Jira client...")
        jira_client = JiraClient()
        
        # Test connection
        logger.info("Testing Jira connection...")
        server_info = jira_client.client.server_info()
        logger.info(f"Connected to Jira server: {server_info['serverTitle']} (Version: {server_info['version']})")
        
        # Initialize Dify integration
        logger.info("Initializing Dify integration...")
        #dify = DifyIntegration(dataset_id="e9188064-20ab-453c-a226-c2e1c1c48ce9")
        dify = DifyIntegration()
        
        # Fetch issues from QAREF project
        logger.info("Fetching issues from QAREF project...")
        jql_query = "project = QAREF ORDER BY created DESC"
        issues = jira_client.get_issues(jql_query, max_results=100)
        
        logger.info(f"Found {len(issues)} issues from QAREF project")
        
        if issues:
            # Ingest issues into Dify RAG
            logger.info("Ingesting issues into Dify RAG...")
            response = dify.ingest_issues(issues)
            logger.info(f"Ingestion response: {response}")
        else:
            logger.warning("No issues found in QAREF project")
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 